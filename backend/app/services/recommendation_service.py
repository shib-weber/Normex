from app.services.retrieval_service import search_standards
from app.db.models import StandardRelationship


def recommend(db, extracted):
    query = extracted["original_input"]
    ranked = search_standards(db, query, extracted.get("domain"), 12)
    requested = {x.replace(" ", "").lower() for x in extracted.get("existing_standards", [])}
    results = []
    for index, (standard, relevance) in enumerate(ranked):
        relations = db.query(StandardRelationship).filter(
            StandardRelationship.source_standard_id == standard.id
        ).all()
        exact = standard.standard_number.replace(" ", "").lower() in requested
        category = "EXPLICIT_REFERENCE" if exact else ("PRIMARY" if index == 0 else "SUPPORTING")
        evidence = [
            "Requirement terminology matched against the NORMEX indexed metadata",
            f"Retrieval relevance: {relevance}%",
        ]
        if standard.source_type == "AUTHORITY_CURATED":
            evidence.append("Authority-curated BIS metadata; open the linked BIS source for the controlling document.")
        else:
            evidence.append("Synthetic demonstration record; not an official standard.")
        if standard.status != "CURRENT":
            evidence.append("Status requires verification before use.")
        results.append({
            "id": standard.id,
            "standard_number": standard.standard_number,
            "title": standard.title,
            "domain": standard.domain,
            "status": standard.status,
            "edition": standard.edition,
            "relevance": relevance,
            "confidence": "HIGH" if relevance >= 65 else ("MEDIUM" if relevance >= 45 else "LOW"),
            "category": category,
            "source_type": standard.source_type,
            "source_name": standard.source_name,
            "source_url": standard.source_url,
            "scope": standard.scope,
            "evidence": evidence,
            "graph_relationships": [
                {"type": r.relationship_type, "target_id": r.target_standard_id, "confidence": r.confidence}
                for r in relations
            ],
        })
    return results
