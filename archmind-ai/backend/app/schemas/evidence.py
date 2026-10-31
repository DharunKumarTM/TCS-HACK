from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class EvidenceItem(BaseModel):
    id: Optional[str] = None
    evidence_code: str
    source_filename: str
    statement: str
    category: str  # Functional, Non-Functional, Constraint, Policy, Architecture Preference
    original_excerpt: str
    location_reference: Optional[str] = None
    confidence_score: float = 1.0
    quality_grade: str = "High"
    is_duplicate: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size_bytes: int
    status: str
    created_at: datetime
    evidence_count: int = 0

    class Config:
        from_attributes = True

