from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ConflictItem(BaseModel):
    id: Optional[str] = None
    conflict_code: str
    conflicting_req_codes: List[str]
    conflict_type: str  # Direct Contradiction, Semantic Incompatibility, Deployment Conflict, Missing Metric, Assumption
    explanation: str
    evidence_excerpts: List[str] = Field(default_factory=list)
    severity: str = "High"  # Critical, High, Medium, Low
    business_impact: str
    technical_impact: str
    suggested_resolution: str
    clarification_question: str
    confidence: float = 0.90
    status: str = "Detected"  # Detected, Clarifying, Resolved, Overridden
    resolution_notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ConflictResolveRequest(BaseModel):
    resolution_notes: str
    status: str = "Resolved"  # Resolved or Overridden
    override_reason: Optional[str] = None

