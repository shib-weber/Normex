
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Standard, StandardRelationship, CertificationRule, EvidenceRecord, DemoScenario, Analysis

router=APIRouter(prefix="/demo",tags=["synthetic-demo"])

@router.get("/overview")
def overview(db:Session=Depends(get_db)):
    return {
      "synthetic":True,
      "analyses":db.query(Analysis).count(),
      "standards":db.query(Standard).count(),
      "relationships":db.query(StandardRelationship).count(),
      "evidence":db.query(EvidenceRecord).count(),
      "certification_rules":db.query(CertificationRule).count(),
      "scenarios":db.query(DemoScenario).count(),
      "coverage":82,
      "confidence":91,
      "open_gaps":14
    }

@router.get("/evidence")
def evidence(limit:int=50, db:Session=Depends(get_db)):
    rows=db.query(EvidenceRecord).order_by(EvidenceRecord.id).limit(limit).all()
    return [{"id":r.id,"code":r.evidence_code,"title":r.title,"type":r.evidence_type,"source":r.source_name,"reference":r.source_reference,"excerpt":r.excerpt,"strength":r.strength,"standard_number":r.standard_number,"requirement_code":r.requirement_code,"synthetic":r.synthetic} for r in rows]

@router.get("/scenarios")
def scenarios(db:Session=Depends(get_db)):
    rows=db.query(DemoScenario).all()
    return [{"id":r.id,"code":r.scenario_code,"title":r.title,"category":r.category,"description":r.description,"risk_level":r.risk_level,"requirements":r.requirements,"synthetic":r.synthetic} for r in rows]
