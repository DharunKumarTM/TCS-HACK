from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Detailed project description")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    metadata_json: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class ProjectStats(BaseModel):
    project_id: str
    project_name: str
    status: str
    total_documents: int = 0
    total_evidence: int = 0
    total_requirements: int = 0
    total_conflicts: int = 0
    resolved_conflicts: int = 0
    pending_clarifications: int = 0
    total_components: int = 0
    total_adrs: int = 0
    coverage_score: float = 0.0
    risk_score: float = 0.0
    validation_passed: bool = True

