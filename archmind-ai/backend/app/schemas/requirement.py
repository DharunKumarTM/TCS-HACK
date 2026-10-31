from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class RequirementItem(BaseModel):
    id: Optional[str] = None
    req_code: str
    title: str
    description: str
    req_type: str  # Functional, Non-Functional, Technical Constraint, Business Constraint
    category: str  # Security, Performance, Scalability, Compliance, Integration, Core
    priority: str = "Medium"  # Critical, High, Medium, Low
    source_evidence_codes: List[str] = Field(default_factory=list)
    confidence: float = 0.95
    verification_method: str = "Automated Test"
    ambiguity_status: str = "Clear"  # Clear, Ambiguous, Incomplete
    approval_status: str = "Pending"  # Fact, Inferred, Assumption, Clarified, Approved, Rejected
    rationale: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RequirementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    approval_status: Optional[str] = None
    ambiguity_status: Optional[str] = None

