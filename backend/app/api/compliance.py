from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.common import AnalyzeRequest
from app.services.extraction_service import extract_requirements
from app.services.compliance_service import check_certification

router=APIRouter(prefix="/compliance",tags=["compliance"])

@router.post("/check")
def check(payload:AnalyzeRequest,db:Session=Depends(get_db)):
    return {"results":check_certification(db,extract_requirements(payload.text))}
