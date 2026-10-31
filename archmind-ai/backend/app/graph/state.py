from typing import List, Dict, Any, Optional, TypedDict

class ArchMindState(TypedDict, total=False):
    project_id: str
    documents: List[Dict[str, Any]]
    extracted_evidence: List[Dict[str, Any]]
    requirements: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    clarification_questions: List[Dict[str, Any]]
    stakeholder_responses: List[Dict[str, Any]]
    architecture_recommendations: Dict[str, Any]
    components: List[Dict[str, Any]]
    apis: List[Dict[str, Any]]
    data_flows: List[Dict[str, Any]]
    adrs: List[Dict[str, Any]]
    validation_results: Dict[str, Any]
    traceability_mappings: Dict[str, Any]
    risks: List[Dict[str, Any]]
    workflow_status: str  # draft, ingesting, analyzing, clarifying, architecting, validated, completed, failed
    current_step: str
    error_information: Optional[str]
    iteration_count: int
    is_paused_for_human: bool

