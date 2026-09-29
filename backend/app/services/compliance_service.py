from app.db.models import CertificationRule

def check_certification(db, extracted):
    product = (extracted.get("product") or "").lower()
    rules = db.query(CertificationRule).all()
    matches = []
    for r in rules:
        if r.product_category.lower() in product or product in r.product_category.lower():
            matches.append({
                "scheme": r.scheme,
                "authority": r.authority,
                "mandatory": r.mandatory,
                "conditions": r.conditions,
                "source": r.source,
                "verification_date": r.verification_date,
                "source_type": r.source_type,
                "status": "RED" if r.mandatory and r.source else "YELLOW",
            })
    return matches or [{
        "status":"GREEN",
        "scheme":"No identified rule in prototype knowledge base",
        "authority":"—",
        "mandatory":False,
        "conditions":"Manual verification required.",
        "source":None,
        "source_type":"SYNTHETIC_WORKFLOW",
    }]
