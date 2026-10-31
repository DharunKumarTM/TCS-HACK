from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ImpactAnalysisRequest(BaseModel):
    target_req_code: str
    modified_description: str
    rationale: Optional[str] = None

class ChangeImpactResult(BaseModel):
    id: Optional[str] = None
    target_req_code: str
    original_description: str
    modified_description: str
    affected_components: List[str] = Field(default_factory=list)
    affected_apis: List[str] = Field(default_factory=list)
    affected_adrs: List[str] = Field(default_factory=list)
    infrastructure_changes: List[str] = Field(default_factory=list)
    performance_risks: List[str] = Field(default_factory=list)
    database_implications: Optional[str] = None
    scaling_requirements: Optional[str] = None
    new_clarification_questions: List[str] = Field(default_factory=list)
    comparison_summary: str
    status: str = "Proposed"

    class Config:
        from_attributes = True

class ChangeImpactApplyRequest(BaseModel):
    analysis_id: str
    apply_to_architecture: bool = True

