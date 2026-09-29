from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Standard
from app.services.retrieval_service import search_standards

router=APIRouter(prefix="/standards", tags=["standards"])

@router.get("/search")
def search(q:str="", domain:str|None=None, limit:int=20, db:Session=Depends(get_db)):
    rows=search_standards(db,q or "standard",domain,limit)
    return [{"id":s.id,"standard_number":s.standard_number,"title":s.title,"domain":s.domain,"scope":s.scope,"status":s.status,"edition":s.edition,"source_type":s.source_type,"relevance":score} for s,score in rows]

@router.get("/{standard_id}")
def detail(standard_id:int, db:Session=Depends(get_db)):
    s=db.get(Standard,standard_id)
    if not s: raise HTTPException(404,"Standard not found")
    return {"id":s.id,"standard_number":s.standard_number,"title":s.title,"short_title":s.short_title,"domain":s.domain,"subdomain":s.subdomain,"scope":s.scope,"description":s.description,"edition":s.edition,"publication_date":s.publication_date,"status":s.status,"revision":s.revision,"source_url":s.source_url,"source_name":s.source_name,"source_type":s.source_type,"last_verified":s.last_verified,"versions":[{"version":v.version,"edition":v.edition,"publication_date":v.publication_date,"status":v.status,"supersedes_version":v.supersedes_version} for v in s.versions]}
