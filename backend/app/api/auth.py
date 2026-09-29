
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import OfficialUser
from app.services.auth_service import verify_password, create_access_token, decode_token

router=APIRouter(prefix="/auth", tags=["authentication"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(payload: LoginRequest, db: Session=Depends(get_db)):
    user=db.query(OfficialUser).filter_by(email=payload.email.lower()).first()
    if not user or not user.active or not verify_password(payload.password,user.password_hash):
        raise HTTPException(401,"Invalid official credentials")
    return {"access_token":create_access_token(user),"token_type":"bearer","user":{"id":user.id,"email":user.email,"name":user.full_name,"role":user.role,"organization":user.organization,"organization_id":user.organization_id}}

@router.get("/me")
def me(token: str, db: Session=Depends(get_db)):
    try: data=decode_token(token)
    except Exception: raise HTTPException(401,"Invalid token")
    user=db.get(OfficialUser,int(data["sub"]))
    if not user or not user.active: raise HTTPException(401,"User inactive")
    return {"id":user.id,"email":user.email,"name":user.full_name,"role":user.role,"organization":user.organization,"organization_id":user.organization_id}
