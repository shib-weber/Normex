from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Organization, OfficialUser
from app.services.role_service import current_user, require_roles
router=APIRouter(prefix="/organizations",tags=["organizations"])
class OrgCreate(BaseModel):
    name:str=Field(min_length=3,max_length=250); org_type:str="PUBLIC_SECTOR"; registration_code:str=Field(min_length=3,max_length=80); jurisdiction:str="India"
@router.get("")
def list_orgs(db:Session=Depends(get_db),user:OfficialUser=Depends(current_user)):
    rows=db.query(Organization).order_by(Organization.name).all(); return [{"id":r.id,"name":r.name,"org_type":r.org_type,"registration_code":r.registration_code,"jurisdiction":r.jurisdiction,"status":r.status,"synthetic":r.synthetic} for r in rows]
@router.post("")
def create_org(payload:OrgCreate,db:Session=Depends(get_db),user:OfficialUser=Depends(require_roles("ADMIN"))):
    if db.query(Organization).filter_by(registration_code=payload.registration_code).first(): raise HTTPException(409,"Registration code already exists")
    o=Organization(**payload.model_dump()); db.add(o); db.commit(); db.refresh(o); return {"id":o.id,"name":o.name,"registration_code":o.registration_code}
