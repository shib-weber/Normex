from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Analysis
from app.schemas.common import AnalyzeRequest
from app.services.analysis_service import analyze

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("")
def create_analysis(payload: AnalyzeRequest, db: Session = Depends(get_db)):
    result = analyze(db, payload.text, payload.language)
    row = Analysis(input_text=payload.text, language=result["extraction"]["language"], product=result["extraction"]["product"], domain=result["extraction"]["domain"], result=result)
    db.add(row); db.commit(); db.refresh(row)
    return {"analysis_id": row.id, **result}

@router.get("")
def list_analyses(db: Session = Depends(get_db)):
    rows = db.query(Analysis).order_by(Analysis.created_at.desc()).limit(50).all()
    return [{"id":r.id,"product":r.product,"domain":r.domain,"language":r.language,"created_at":r.created_at.isoformat()} for r in rows]

@router.get("/{analysis_id}")
def get_analysis(analysis_id:int, db:Session=Depends(get_db)):
    row = db.get(Analysis, analysis_id)
    if not row: raise HTTPException(404, "Analysis not found")
    return {"analysis_id":row.id, **row.result}
