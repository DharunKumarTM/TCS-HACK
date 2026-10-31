from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ClarificationQuestionItem(BaseModel):
    id: Optional[str] = None
    conflict_id: Optional[str] = None
    question_code: str
    title: str
    question: str
    context_reasoning: Optional[str] = None
    related_req_codes: List[str] = Field(default_factory=list)
    suggested_options: List[str] = Field(default_factory=list)
    status: str = "Pending"  # Pending, Answered, Dismissed
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class StakeholderResponseSubmit(BaseModel):
    selected_option: Optional[str] = None
    custom_answer: Optional[str] = None
    submitted_by: Optional[str] = "Human Architect"

class ClarificationWithResponse(BaseModel):
    question: ClarificationQuestionItem
    response: Optional[Dict[str, Any]] = None

