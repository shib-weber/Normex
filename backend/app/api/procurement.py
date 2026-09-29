from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import (
    Tender,
    TenderSubmission,
    EvaluationRecord,
    Organization,
    AuditEvent,
    OfficialUser,
)
from app.services.role_service import current_user, require_roles, ROLE_LABELS
from app.services.analysis_service import analyze

router = APIRouter(
    prefix="/procurement",
    tags=["procurement-workflow"],
)


# ============================================================
# SCHEMAS
# ============================================================

class TenderCreate(BaseModel):
    title: str = Field(min_length=5, max_length=300)
    description: str = Field(min_length=20, max_length=50000)
    category: str = Field(default="General", min_length=2, max_length=120)
    budget: float = Field(gt=0)
    deadline: str = Field(min_length=8, max_length=30)


class ComplianceReviewIn(BaseModel):
    decision: str = Field(pattern="^(APPROVE|RETURN)$")
    notes: str = ""


class SubmissionCreate(BaseModel):
    bid_amount: float = Field(gt=0)
    proposal: dict = Field(default_factory=dict)


class EvaluationIn(BaseModel):
    technical_score: float = Field(ge=0, le=100)
    compliance_score: float = Field(ge=0, le=100)
    commercial_score: float = Field(ge=0, le=100)
    notes: str = ""
    decision: str = Field(
        default="SHORTLISTED",
        pattern="^(REVIEW|SHORTLISTED|RECOMMENDED|REJECTED)$",
    )


class AwardIn(BaseModel):
    submission_id: int


# ============================================================
# HELPERS
# ============================================================

def audit(
    db: Session,
    user: OfficialUser,
    action: str,
    entity_type: str,
    entity_id,
    details=None,
):
    db.add(
        AuditEvent(
            actor_id=user.id,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id),
            details=details or {},
        )
    )


def next_tender_number(db: Session) -> str:
    """
    Generate a collision-safe tender number.

    Example:
    NMX-TND-2026-0001
    """
    year = datetime.utcnow().year

    latest = (
        db.query(Tender)
        .filter(Tender.tender_number.like(f"NMX-TND-{year}-%"))
        .order_by(Tender.id.desc())
        .first()
    )

    if latest:
        try:
            last_number = int(latest.tender_number.split("-")[-1])
        except (ValueError, IndexError):
            last_number = 0
    else:
        last_number = 0

    return f"NMX-TND-{year}-{last_number + 1:04d}"


def serialize_submission(s, db):
    org = db.get(Organization, s.vendor_org_id)

    return {
        "id": s.id,
        "vendor": org.name if org else "Vendor",
        "vendor_org_id": s.vendor_org_id,
        "bid_amount": s.bid_amount,
        "technical_score": s.technical_score,
        "commercial_score": s.commercial_score,
        "final_score": s.final_score,
        "status": s.status,
        "proposal": s.proposal,
        "submitted_at": s.submitted_at.isoformat(),
    }


def serialize_tender(t, db, user=None):
    org = db.get(Organization, t.issuing_org_id)

    submissions = (
        db.query(TenderSubmission)
        .filter(TenderSubmission.tender_id == t.id)
        .all()
    )

    show_submissions = (
        user
        and user.role
        in {
            "PROCUREMENT_OFFICER",
            "GOVERNMENT_REVIEWER",
            "ORGANIZATION_ADMIN",
            "AUDITOR",
            "ADMIN",
        }
    )

    return {
        "id": t.id,
        "tender_number": t.tender_number,
        "title": t.title,
        "description": t.description,
        "category": t.category,
        "organization": org.name if org else "Unknown",
        "organization_id": t.issuing_org_id,
        "status": t.status,
        "budget": t.budget,
        "deadline": t.deadline,
        "requirements": t.requirements or {},
        "analysis": t.analysis_result or {},
        "compliance_status": t.compliance_status,
        "submission_count": len(submissions),
        "submissions": (
            [serialize_submission(s, db) for s in submissions]
            if show_submissions
            else []
        ),
        "created_at": t.created_at.isoformat(),
        "updated_at": t.updated_at.isoformat(),
    }


# ============================================================
# OVERVIEW
# ============================================================

@router.get("/overview")
def overview(
    db: Session = Depends(get_db),
    user: OfficialUser = Depends(current_user),
):
    q = db.query(Tender)

    if user.role in {"ORGANIZATION_ADMIN", "PROCUREMENT_OFFICER"}:
        q = q.filter(Tender.issuing_org_id == user.organization_id)
    elif user.role == "VENDOR":
        q = q.filter(Tender.status == "PUBLISHED")

    tenders = q.order_by(Tender.created_at.desc()).all()

    drafts = sum(1 for t in tenders if t.status == "DRAFT")
    reviews = sum(1 for t in tenders if t.status == "COMPLIANCE_REVIEW")
    published = sum(1 for t in tenders if t.status == "PUBLISHED")
    
    bids = sum(
        len(
            db.query(TenderSubmission)
            .filter(TenderSubmission.tender_id == t.id)
            .all()
        )
        for t in tenders
    )

    return {
        "role": user.role,
        "role_label": ROLE_LABELS.get(user.role, user.role),
        "counts": {
            "draft": drafts,
            "review": reviews,
            "published": published,
            "bids": bids,
        },
        "workflow": [
            "Create tender",
            "NORMEX analysis",
            "Compliance review",
            "Publish",
            "Vendor bidding",
            "Close bidding",
            "Evaluation",
            "Award",
            "Audit",
        ],
        "tenders": [
            serialize_tender(t, db, user)
            for t in tenders
        ],
    }


# ============================================================
# CREATE TENDER
# ============================================================

@router.post("/tenders")
def create_tender(
    payload: TenderCreate,
    db: Session = Depends(get_db),
    user: OfficialUser = Depends(
        require_roles(
            "ORGANIZATION_ADMIN",
            "PROCUREMENT_OFFICER",
        )
    ),
):
    if not user.organization_id:
        raise HTTPException(
            status_code=400,
            detail="Your account is not linked to an organization.",
        )

    organization = db.get(Organization, user.organization_id)
    if not organization:
        raise HTTPException(
            status_code=400,
            detail="Your organization could not be found.",
        )

    try:
        result = analyze(db, payload.description)
        tender_number = next_tender_number(db)

        has_gaps = bool(result.get("gaps"))
        compliance_status = "REVIEW_REQUIRED" if has_gaps else "ANALYSIS_READY"
        initial_status = "COMPLIANCE_REVIEW" if has_gaps else "DRAFT"

        tender = Tender(
            tender_number=tender_number,
            title=payload.title.strip(),
            description=payload.description.strip(),
            category=payload.category.strip(),
            issuing_org_id=organization.id,
            created_by=user.id,
            budget=float(payload.budget),
            deadline=payload.deadline,
            status=initial_status,
            requirements=result.get("extraction", {}),
            analysis_result=result,
            compliance_status=compliance_status,
        )

        db.add(tender)
        db.flush()

        audit(
            db,
            user,
            "TENDER_CREATED",
            "TENDER",
            tender.id,
            {
                "tender_number": tender.tender_number,
                "title": tender.title,
                "category": tender.category,
                "budget": tender.budget,
                "organization_id": organization.id,
            },
        )

        db.commit()
        db.refresh(tender)

        return serialize_tender(tender, db, user)

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Tender creation failed: {str(exc)}",
        )


# ============================================================
# COMPLIANCE REVIEW
# ============================================================

@router.post("/tenders/{tender_id}/compliance-review")
def compliance_review(
    tender_id: int,
    payload: ComplianceReviewIn,
    db: Session = Depends(get_db),
    user: OfficialUser = Depends(require_roles("COMPLIANCE_OFFICER")),
):
    tender = db.get(Tender, tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found.")

    if tender.status not in {"DRAFT", "COMPLIANCE_REVIEW"}:
        raise HTTPException(
            status_code=409,
            detail=f"Tender cannot be reviewed from status {tender.status}.",
        )

    if payload.decision == "APPROVE":
        tender.compliance_status = "APPROVED"
        tender.status = "READY_TO_PUBLISH"
        action = "TENDER_COMPLIANCE_APPROVED"
    else:
        tender.compliance_status = "REVIEW_REQUIRED"
        tender.status = "COMPLIANCE_REVIEW"
        action = "TENDER_RETURNED_FOR_CORRECTION"

    audit(db, user, action, "TENDER", tender.id, {"decision": payload.decision, "notes": payload.notes})

    db.commit()
    db.refresh(tender)

    return serialize_tender(tender, db, user)


# ============================================================
# PUBLISH
# ============================================================

@router.post("/tenders/{tender_id}/publish")
def publish(
    tender_id: int,
    db: Session = Depends(get_db),
    user: OfficialUser = Depends(
        require_roles("ORGANIZATION_ADMIN", "PROCUREMENT_OFFICER", "COMPLIANCE_OFFICER")
    ),
):
    tender = db.get(Tender, tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found.")

    if user.role in {"ORGANIZATION_ADMIN", "PROCUREMENT_OFFICER"}:
        if tender.issuing_org_id != user.organization_id:
            raise HTTPException(status_code=403, detail="You cannot publish a tender belonging to another organization.")

    if tender.status != "READY_TO_PUBLISH" or tender.compliance_status != "APPROVED":
        raise HTTPException(
            status_code=409,
            detail="Tender must pass compliance review and be marked READY_TO_PUBLISH before publication.",
        )

    tender.status = "PUBLISHED"
    audit(db, user, "TENDER_PUBLISHED", "TENDER", tender.id, {"tender_number": tender.tender_number})

    db.commit()
    db.refresh(tender)

    return serialize_tender(tender, db, user)


# ============================================================
# CLOSE BIDDING
# ============================================================

@router.post("/tenders/{tender_id}/close")
def close_bidding(
    tender_id: int,
    db: Session = Depends(get_db),
    user: OfficialUser = Depends(require_roles("ORGANIZATION_ADMIN", "PROCUREMENT_OFFICER")),
):
    tender = db.get(Tender, tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found.")

    if tender.issuing_org_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Tender belongs to another organization.")

    if tender.status != "PUBLISHED":
        raise HTTPException(status_code=409, detail="Only published tenders can be closed.")

    tender.status = "EVALUATION"
    audit(db, user, "BIDDING_CLOSED", "TENDER", tender.id)

    db.commit()
    db.refresh(tender)

    return serialize_tender(tender, db, user)


# ============================================================
# SUBMIT / UPDATE BID
# ============================================================

@router.post("/tenders/{tender_id}/submit")
def submit(
    tender_id: int,
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    user: OfficialUser = Depends(require_roles("VENDOR")),
):
    tender = db.get(Tender, tender_id)
    if not tender or tender.status != "PUBLISHED":
        raise HTTPException(status_code=404, detail="Published tender not found.")

    if not user.organization_id:
        raise HTTPException(status_code=400, detail="Vendor organization is not configured.")

    existing = (
        db.query(TenderSubmission)
        .filter_by(tender_id=tender.id, vendor_org_id=user.organization_id)
        .first()
    )

    if existing:
        existing.bid_amount = payload.bid_amount
        existing.proposal = payload.proposal
        submission = existing
        action_name = "BID_UPDATED"
    else:
        submission = TenderSubmission(
            tender_id=tender.id,
            vendor_org_id=user.organization_id,
            bid_amount=payload.bid_amount,
            proposal=payload.proposal,
        )
        db.add(submission)
        action_name = "BID_SUBMITTED"

    db.flush()

    audit(
        db,
        user,
        action_name,
        "TENDER_SUBMISSION",
        submission.id,
        {"tender": tender.tender_number, "bid_amount": payload.bid_amount},
    )

    db.commit()
    db.refresh(submission)

    return serialize_submission(submission, db)


# ============================================================
# EVALUATE SUBMISSION
# ============================================================

@router.post("/submissions/{submission_id}/evaluate")
def evaluate(
    submission_id: int,
    payload: EvaluationIn,
    db: Session = Depends(get_db),
    user: OfficialUser = Depends(require_roles("PROCUREMENT_OFFICER", "GOVERNMENT_REVIEWER")),
):
    submission = db.get(TenderSubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    tender = db.get(Tender, submission.tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found.")

    # Auto-transition to EVALUATION if bidding hasn't been explicitly closed yet
    if tender.status == "PUBLISHED":
        tender.status = "EVALUATION"
    elif tender.status != "EVALUATION":
        raise HTTPException(
            status_code=409,
            detail=f"Tender must be published or in evaluation (current: {tender.status}).",
        )

    final_score = round(
        payload.technical_score * 0.45
        + payload.compliance_score * 0.30
        + payload.commercial_score * 0.25,
        2,
    )

    submission.technical_score = payload.technical_score
    submission.commercial_score = payload.commercial_score
    submission.final_score = final_score
    submission.status = payload.decision

    evaluation = EvaluationRecord(
        tender_id=tender.id,
        submission_id=submission.id,
        evaluator_id=user.id,
        technical_score=payload.technical_score,
        compliance_score=payload.compliance_score,
        commercial_score=payload.commercial_score,
        notes=payload.notes,
        decision=payload.decision,
    )
    db.add(evaluation)

    audit(db, user, "SUBMISSION_EVALUATED", "TENDER_SUBMISSION", submission.id, {"final_score": final_score})

    db.commit()
    db.refresh(submission)

    return serialize_submission(submission, db)


# ============================================================
# AWARD
# ============================================================

@router.post("/tenders/{tender_id}/award")
def award(
    tender_id: int,
    payload: AwardIn,
    db: Session = Depends(get_db),
    user: OfficialUser = Depends(require_roles("ORGANIZATION_ADMIN", "PROCUREMENT_OFFICER")),
):
    tender = db.get(Tender, tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found.")

    if tender.issuing_org_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Tender belongs to another organization.")

    if tender.status != "EVALUATION":
        raise HTTPException(status_code=409, detail="Tender is not currently under evaluation.")

    submission = db.get(TenderSubmission, payload.submission_id)
    if not submission or submission.tender_id != tender.id:
        raise HTTPException(status_code=400, detail="Invalid submission selected for this tender.")

    if submission.status not in {"SHORTLISTED", "RECOMMENDED"}:
        raise HTTPException(status_code=409, detail="Only shortlisted submissions can be awarded.")

    submission.status = "AWARDED"

    other_submissions = (
        db.query(TenderSubmission)
        .filter(TenderSubmission.tender_id == tender.id, TenderSubmission.id != submission.id)
        .all()
    )

    for other in other_submissions:
        if other.status not in {"AWARDED", "REJECTED"}:
            other.status = "REJECTED"

    tender.status = "AWARDED"

    audit(db, user, "TENDER_AWARDED", "TENDER", tender.id, {"submission_id": submission.id})

    db.commit()
    db.refresh(tender)

    return serialize_tender(tender, db, user)


# ============================================================
# AUDIT LOG
# ============================================================

@router.get("/audit")
def audit_log(
    db: Session = Depends(get_db),
    user: OfficialUser = Depends(require_roles("AUDITOR", "ADMIN")),
):
    rows = db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(100).all()

    return [
        {
            "id": r.id,
            "action": r.action,
            "entity_type": r.entity_type,
            "entity_id": r.entity_id,
            "details": r.details,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]