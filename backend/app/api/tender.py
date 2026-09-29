from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.analysis_service import analyze
from app.schemas.common import AnalyzeRequest

router=APIRouter(prefix="/tender",tags=["tender"])

@router.post("/analyze")
def tender_analyze(payload:AnalyzeRequest, db:Session=Depends(get_db)):
    result=analyze(db,payload.text,payload.language)
    issues=[]
    lower=payload.text.lower()
    if "high quality" in lower or "good quality" in lower:
        issues.append({"severity":"HIGH","type":"AMBIGUOUS_REQUIREMENT","evidence":"Non-measurable quality language detected","suggestion":"Replace it with measurable grade, performance, test method, tolerance or acceptance criteria."})
    if not any(x in lower for x in ["test","testing","test method","laboratory"]):
        issues.append({"severity":"MEDIUM","type":"MISSING_TEST_METHOD","evidence":"No test method identified","suggestion":"For LED luminaires, review applicable BIS requirements and associated test methods before finalising the tender."})
    if "installation" not in lower and "install" not in lower:
        issues.append({"severity":"MEDIUM","type":"MISSING_INSTALLATION","evidence":"No installation requirement identified","suggestion":"Define mounting, electrical connection, environmental installation and commissioning requirements where applicable."})
    if "acceptance" not in lower and "commissioning" not in lower:
        issues.append({"severity":"MEDIUM","type":"MISSING_ACCEPTANCE_CRITERIA","evidence":"No acceptance criteria identified","suggestion":"Define objective acceptance measurements, inspection records and rejection thresholds."})
    if "inspection" not in lower:
        issues.append({"severity":"LOW","type":"MISSING_INSPECTION","evidence":"No inspection requirement identified","suggestion":"Define incoming inspection, document review and site acceptance steps where applicable."})
    if result["extraction"].get("domain")=="Lighting" and not result["extraction"].get("existing_standards"):
        issues.append({"severity":"MEDIUM","type":"MISSING_EXPLICIT_STANDARD_REFERENCE","evidence":"No IS reference appears in the tender text","suggestion":"NORMEX found BIS-indexed lighting standards; review the recommendations and explicitly state only the standards verified as applicable."})
    return {"issues":issues,"analysis":result,"source_policy":"Recommendations are metadata-based; authoritative BIS documents remain controlling."}
