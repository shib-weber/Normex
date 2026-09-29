from fastapi import APIRouter, Response
from app.services.report_service import make_pdf, make_docx
from pydantic import BaseModel

router=APIRouter(prefix="/reports",tags=["reports"])
class ReportPayload(BaseModel):
    result: dict

@router.post("/pdf")
def pdf(payload:ReportPayload):
    bio=make_pdf(payload.result)
    return Response(bio.read(),media_type="application/pdf",headers={"Content-Disposition":"attachment; filename=normex-report.pdf"})

@router.post("/docx")
def docx(payload:ReportPayload):
    bio=make_docx(payload.result)
    return Response(bio.read(),media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",headers={"Content-Disposition":"attachment; filename=normex-report.docx"})
