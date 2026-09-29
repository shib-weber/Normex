from pydantic import BaseModel, Field
class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=5, max_length=50000)
    language: str | None = None
class StandardOut(BaseModel):
    id: int
    standard_number: str
    title: str
    domain: str
    scope: str
    status: str
    edition: str | None
    source_type: str
    model_config = {"from_attributes": True}
