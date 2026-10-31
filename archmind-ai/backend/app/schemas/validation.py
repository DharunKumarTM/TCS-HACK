from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ValidationItem(BaseModel):
    id: Optional[str] = None
    rule_name: str
    category: str  # Requirement Coverage, Security, Scalability, Component Completeness, Circular Dependencies
    status: str  # Pass, Warn, Fail
    score: float = 100.0
    details: str
    recommendation: Optional[str] = None
    is_deterministic: bool = True

    class Config:
        from_attributes = True

class RiskItem(BaseModel):
    id: Optional[str] = None
    risk_code: str
    title: str
    category: str
    likelihood: str  # Low, Medium, High, Critical
    impact: str  # Low, Medium, High, Critical
    severity: str  # Low, Medium, High, Critical
    risk_score: float = 7.0
    related_req_codes: List[str] = Field(default_factory=list)
    affected_components: List[str] = Field(default_factory=list)
    mitigation_strategy: str

    class Config:
        from_attributes = True

class ValidationOverview(BaseModel):
    overall_health_score: float
    status: str  # Passed, Warning, Failed
    passed_rules_count: int
    warned_rules_count: int
    failed_rules_count: int
    validations: List[ValidationItem]
    risks: List[RiskItem]

