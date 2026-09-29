from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Standard, StandardRelationship

router=APIRouter(prefix="/graph",tags=["graph"])

@router.get("/standard/{standard_id}")
def graph(standard_id:int, db:Session=Depends(get_db)):
    s=db.get(Standard,standard_id)
    if not s: return {"nodes":[],"edges":[]}
    ids={s.id}; rels=[]
    for r in db.query(StandardRelationship).filter(StandardRelationship.source_standard_id==s.id).all():
        ids.add(r.target_standard_id); rels.append(r)
    standards={x.id:x for x in db.query(Standard).filter(Standard.id.in_(ids)).all()}
    nodes=[{"id":str(x.id),"data":{"label":x.standard_number+"\n"+x.title},"position":{"x":i*260,"y":120+(i%2)*150}} for i,x in enumerate(standards.values())]
    edges=[{"id":f"e{r.id}","source":str(r.source_standard_id),"target":str(r.target_standard_id),"label":r.relationship_type} for r in rels]
    return {"nodes":nodes,"edges":edges}
