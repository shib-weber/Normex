from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import get_db
from app.services.document_service import extract_text
from app.services.analysis_service import analyze

router=APIRouter(prefix="/documents",tags=["documents"])

@router.post("/upload")
async def upload(file:UploadFile=File(...), db:Session=Depends(get_db)):
    ext=Path(file.filename or "").suffix.lower()
    if ext not in {".pdf",".docx",".txt"}: raise HTTPException(400,"Only PDF, DOCX and TXT are supported")
    data=await file.read()
    if len(data)>settings.upload_max_size: raise HTTPException(413,"File exceeds configured upload limit")
    Path(settings.storage_path).mkdir(parents=True,exist_ok=True)
    path=Path(settings.storage_path)/(f"{uuid4().hex}{ext}")
    path.write_bytes(data)
    try: text=extract_text(str(path))
    except Exception as exc: raise HTTPException(422,"Unable to extract readable text from this document.") from exc
    if not text.strip(): raise HTTPException(422,"Unable to extract readable text from this document.")
    return {"filename":file.filename,"text":text,"analysis":analyze(db,text)}
