from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.db.models import BasketItem, Standard

router=APIRouter(prefix="/standards-basket",tags=["basket"])

class BasketIn(BaseModel):
    standard_id:int

@router.get("")
def get_basket(db:Session=Depends(get_db)):
    rows=db.query(BasketItem).all()
    return [{"id":r.id,"standard":db.get(Standard,r.standard_id)} for r in rows]

@router.post("")
def add(item:BasketIn,db:Session=Depends(get_db)):
    if not db.get(Standard,item.standard_id): raise HTTPException(404,"Standard not found")
    if not db.query(BasketItem).filter_by(standard_id=item.standard_id).first():
        db.add(BasketItem(standard_id=item.standard_id)); db.commit()
    return {"ok":True}

@router.delete("/{standard_id}")
def remove(standard_id:int,db:Session=Depends(get_db)):
    row=db.query(BasketItem).filter_by(standard_id=standard_id).first()
    if row: db.delete(row); db.commit()
    return {"ok":True}
