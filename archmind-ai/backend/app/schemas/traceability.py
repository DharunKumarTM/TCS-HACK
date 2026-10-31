from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class TraceabilityItem(BaseModel):
    id: Optional[str] = None
    req_code: str
    req_description: str
    req_category: str
    evidence_codes: List[str] = Field(default_factory=list)
    mapped_component_codes: List[str] = Field(default_factory=list)
    related_api_ids: List[str] = Field(default_factory=list)
    related_adr_codes: List[str] = Field(default_factory=list)
    validation_status: str = "Pass"
    coverage_status: str = "Fully Covered"  # Fully Covered, Partially Covered, Not Covered, Blocked
    coverage_score: float = 1.0

    class Config:
        from_attributes = True

class TraceabilityMatrixResponse(BaseModel):
    total_requirements: int
    fully_covered: int
    partially_covered: int
    not_covered: int
    blocked: int
    overall_coverage_pct: float
    items: List[TraceabilityItem]

