from typing import Annotated

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from app.services.document_service import (
    extract_document_text,
)

router = APIRouter(
    prefix="/api/analysis",
    tags=["Procurement Analysis"],
)


def analyze_requirements(text: str):

    lower = text.lower()

    requirements = []

    keywords = {
        "quantity": [
            "quantity",
            "units",
            "nos",
            "number of",
        ],
        "power": [
            "power",
            "watt",
            "kw",
            "kva",
        ],
        "safety": [
            "safety",
            "safe",
            "protection",
        ],
        "testing": [
            "test",
            "testing",
            "laboratory",
            "inspection",
        ],
        "certification": [
            "certificate",
            "certification",
            "conformity",
        ],
        "warranty": [
            "warranty",
            "guarantee",
        ],
        "standard": [
            "standard",
            "iso",
            "iec",
            "bis",
            "astm",
            "en ",
        ],
        "delivery": [
            "delivery",
            "deliver",
            "completion",
        ],
    }

    for category, terms in keywords.items():

        found = [
            term
            for term in terms
            if term in lower
        ]

        requirements.append({
            "category": category,
            "detected": bool(found),
            "matched_terms": found,
        })

    missing = [
        item["category"]
        for item in requirements
        if not item["detected"]
    ]

    detected = len(requirements) - len(missing)

    coverage = round(
        detected / len(requirements) * 100,
        1
    )

    return {
        "requirements": requirements,
        "missing_categories": missing,
        "coverage_percent": coverage,
        "character_count": len(text),
    }


@router.post("/document")
async def analyze_document(
    file: Annotated[
        UploadFile,
        File(...)
    ]
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file supplied.",
        )

    try:

        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        text = extract_document_text(
            data=content,
            filename=file.filename,
            content_type=file.content_type,
        )

        if not text:
            raise HTTPException(
                status_code=422,
                detail=(
                    "No readable text was extracted. "
                    "This PDF may be scanned/image-only."
                ),
            )

        analysis = analyze_requirements(text)

        return {
            "success": True,
            "filename": file.filename,
            "content_type": file.content_type,
            "extracted_text": text,
            "analysis": analysis,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Document analysis failed: {exc}",
        )
