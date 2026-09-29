from app.services.extraction_service import extract_requirements
from app.services.recommendation_service import recommend
from app.services.compliance_service import check_certification
from app.db.models import StandardRelationship

def analyze(db, text, language=None):
    extracted = extract_requirements(text)
    if language:
        extracted["language"] = language
    recs = recommend(db, extracted)
    covered = sum(1 for r in extracted["requirements"] if r["covered"])
    total = len(extracted["requirements"])
    gaps = [r for r in extracted["requirements"] if not r["covered"]]
    version_alerts = []
    for s in recs:
        if s["status"] != "CURRENT":
            version_alerts.append({
                "standard_number": s["standard_number"],
                "message": "Potential version review required.",
                "action": "Review the evidence and applicable dated/undated reference before changing the tender."
            })
    return {
        "extraction": extracted,
        "recommendations": recs,
        "coverage": {"covered": covered, "total": total, "ratio": round(covered/total*100) if total else 0},
        "gaps": gaps,
        "version_alerts": version_alerts,
        "certification": check_certification(db, extracted),
        "risks": build_risks(extracted, gaps, version_alerts),
        "disclaimer": "Prototype Knowledge Base — verify against authoritative source before actual procurement.",
    }

def build_risks(extracted, gaps, version_alerts):
    return [
        {"category":"Completeness risk","level":"HIGH" if len(gaps)>=2 else "MEDIUM","reason":f"{len(gaps)} identified requirement(s) need additional specification."},
        {"category":"Version risk","level":"MEDIUM" if version_alerts else "LOW","reason":"Potential version review is required." if version_alerts else "No version alert identified in the prototype knowledge base."},
        {"category":"Testing risk","level":"MEDIUM","reason":"Confirm applicable test methods before procurement."},
        {"category":"Safety risk","level":"MEDIUM","reason":"Confirm product-specific safety requirements against authoritative sources."},
        {"category":"Certification risk","level":"MEDIUM","reason":"Certification rules are evidence-dependent and must be verified."},
        {"category":"Ambiguity risk","level":"MEDIUM" if gaps else "LOW","reason":"Use measurable acceptance criteria instead of generic wording."},
    ]
