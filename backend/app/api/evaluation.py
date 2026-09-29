from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Analysis

router=APIRouter(prefix="/evaluation",tags=["evaluation"])

@router.get("/metrics")
def metrics(db:Session=Depends(get_db)):
    cases=db.query(Analysis).count()
    return {"benchmark_cases":cases,"metrics_available":False,"message":"Metrics are calculated only from actual benchmark cases. No fake evaluation scores are returned."}
