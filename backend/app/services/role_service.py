from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import OfficialUser
from app.services.auth_service import decode_token
ROLE_LABELS={"ORGANIZATION_ADMIN":"Organization Administrator","PROCUREMENT_OFFICER":"Procurement Officer","GOVERNMENT_REVIEWER":"Government Reviewer","STANDARDS_OFFICER":"Standards Officer","COMPLIANCE_OFFICER":"Compliance Officer","VENDOR":"Vendor / Supplier","AUDITOR":"Audit Officer","ADMIN":"Platform Administrator"}
def current_user(request: Request, db: Session = Depends(get_db)) -> OfficialUser:
    auth=request.headers.get("Authorization","")
    if not auth.startswith("Bearer "): raise HTTPException(401,"Authentication required")
    try: user=db.get(OfficialUser,int(decode_token(auth.split(" ",1)[1])["sub"]))
    except Exception: user=None
    if not user or not user.active: raise HTTPException(401,"Invalid or inactive session")
    return user
def require_roles(*roles):
    def dep(user: OfficialUser=Depends(current_user)):
        if user.role not in roles and user.role!="ADMIN": raise HTTPException(403,f"Role {user.role} is not permitted for this action")
        return user
    return dep
