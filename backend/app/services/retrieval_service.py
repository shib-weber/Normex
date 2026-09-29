import re
from sqlalchemy import or_
from app.db.models import Standard


def tokens(text):
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


def normalize_is(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().upper()).replace(" : ", ": ")


def score_standard(query, standard):
    q = tokens(query)
    hay = tokens(" ".join([
        standard.standard_number or "",
        standard.title or "",
        standard.scope or "",
        standard.domain or "",
        standard.description or "",
    ]))
    overlap = len(q & hay)
    score = 20 + overlap * 5
    ql = (query or "").lower()
    title = (standard.title or "").lower()
    number = (standard.standard_number or "").lower()

    if any(x in ql for x in ["led", "luminaire", "street light", "streetlight"]):
        if "lighting" in title or "luminaire" in title or "led" in title or "lighting" in (standard.scope or "").lower():
            score += 18
    if "street" in ql and "street" in (standard.scope or "").lower():
        score += 16
    if "ip66" in ql or "ip65" in ql or re.search(r"\bip\d{2}\b", ql):
        if "ip" in title or "ingress" in (standard.scope or "").lower() or "60529" in number:
            score += 14
    if "cable" in ql and "cable" in title:
        score += 14
    if "solar" in ql or "photovoltaic" in ql or "pv" in ql:
        if "photovoltaic" in title or "pv" in title.lower() or "solar" in title.lower():
            score += 22
    if "pump" in ql or "submersible" in ql:
        if "pump" in title.lower() or "submersible" in title.lower():
            score += 22
    if "steel" in ql or "structural" in ql:
        if "steel" in title.lower() or "structural" in title.lower():
            score += 20
    if "concrete" in ql and "concrete" in title:
        score += 18
    if "emc" in ql or "harmonic" in ql:
        if "emc" in title.lower() or "harmonic" in title.lower():
            score += 15
    if re.search(r"\bis\s*\d", ql) and any(t in ql for t in number.split()):
        score += 10

    if standard.source_type == "AUTHORITY_CURATED":
        score += 4
    return min(100, round(score, 1))


def search_standards(db, query, domain=None, limit=10):
    query = query or "standard"
    q = f"%{query.lower()}%"
    base = db.query(Standard)
    if domain and domain != "General":
        base = base.filter(Standard.domain.ilike(f"%{domain}%"))
    rows = base.filter(
        or_(
            Standard.title.ilike(q),
            Standard.scope.ilike(q),
            Standard.domain.ilike(q),
            Standard.standard_number.ilike(q),
            Standard.description.ilike(q),
        )
    ).limit(100).all()
    if not rows:
        rows = base.limit(100).all()
    ranked = sorted(rows, key=lambda s: score_standard(query, s), reverse=True)
    return [(s, score_standard(query, s)) for s in ranked[:limit]]
