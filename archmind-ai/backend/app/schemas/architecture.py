from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ComponentItem(BaseModel):
    id: Optional[str] = None
    component_code: str
    name: str
    layer: str  # Frontend / API Gateway / Core Domain / Data Layer / Security / Event Broker
    responsibility: str
    technology_stack: str
    deployment_target: str = "Container / Kubernetes"
    scaling_strategy: str = "Horizontal Auto-scaling"
    security_controls: List[str] = Field(default_factory=list)
    related_req_codes: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    status: str = "Proposed"

    class Config:
        from_attributes = True

class APIEndpointItem(BaseModel):
    id: Optional[str] = None
    component_code: str
    method: str
    path: str
    summary: str
    auth_requirement: str = "Bearer JWT + RBAC"
    rate_limit: str = "1000 req/min"
    related_req_codes: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True

class DataFlowItem(BaseModel):
    id: Optional[str] = None
    flow_code: str
    title: str
    source: str
    target: str
    protocol: str = "HTTPS / REST"
    payload_type: str = "JSON"
    encryption: str = "TLS 1.3 in-transit"
    step_sequence: int = 1
    description: Optional[str] = None

    class Config:
        from_attributes = True

class ADRItem(BaseModel):
    id: Optional[str] = None
    adr_code: str
    title: str
    status: str = "Proposed"  # Proposed, Accepted, Rejected, Superseded
    context: str
    problem: str
    decision: str
    alternatives: List[Dict[str, str]] = Field(default_factory=list)
    advantages: List[str] = Field(default_factory=list)
    disadvantages: List[str] = Field(default_factory=list)
    trade_offs: str
    supporting_req_codes: List[str] = Field(default_factory=list)
    evidence_references: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    consequences: str
    confidence: float = 0.92

    class Config:
        from_attributes = True

class ADRStatusUpdate(BaseModel):
    status: str  # Accepted, Rejected, Superseded
    review_notes: Optional[str] = None

class TechStackAlternative(BaseModel):
    name: str
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    why_rejected: str
    trade_offs: str

class TechStackItem(BaseModel):
    category: str
    selected: str
    reason_why: str
    requirements_supported: List[str] = Field(default_factory=list)
    alternatives: List[TechStackAlternative] = Field(default_factory=list)
    is_overridden: bool = False
    overridden_by: Optional[str] = None

class ArchitectureMetrics(BaseModel):
    latency_p99: str
    throughput_tps: str
    availability: str
    rpo_rto: str
    security_posture: str
    scalability_ceiling: str

class ArchitectureEvolutionModel(BaseModel):
    name: str
    style: str
    description: str
    characteristics: List[str] = Field(default_factory=list)
    metrics: ArchitectureMetrics
    mermaid_diagram: str

class ArchitectureComparison(BaseModel):
    project_id: str
    old_architecture: ArchitectureEvolutionModel
    new_architecture: ArchitectureEvolutionModel
    comparison_matrix: List[Dict[str, Any]] = Field(default_factory=list)
    tech_stack_recommendations: List[TechStackItem] = Field(default_factory=list)
    confirmation_status: str = "Pending Review"  # "Pending Review" | "Confirmed" | "Customized" | "Revisions Requested"
    confirmed_by: Optional[str] = None
    confirmed_at: Optional[str] = None
    architect_notes: Optional[str] = None
    overrides: Dict[str, str] = Field(default_factory=dict)

class ArchitectureConfirmationRequest(BaseModel):
    action: str = "confirm"  # "confirm" | "request_revision" | "customize"
    architect_name: Optional[str] = "Lead Enterprise Architect"
    notes: Optional[str] = None
    overrides: Optional[Dict[str, str]] = None

class ArchitectureRecommendation(BaseModel):
    architecture_style: str  # e.g., Modular Monolith with Event-Driven Integration
    style_justification: str
    components: List[ComponentItem] = Field(default_factory=list)
    apis: List[APIEndpointItem] = Field(default_factory=list)
    data_flows: List[DataFlowItem] = Field(default_factory=list)
    adrs: List[ADRItem] = Field(default_factory=list)
    mermaid_diagrams: Dict[str, str] = Field(default_factory=dict)
    tech_stack_recommendations: List[TechStackItem] = Field(default_factory=list)
    old_architecture: Optional[ArchitectureEvolutionModel] = None
    new_architecture: Optional[ArchitectureEvolutionModel] = None
    comparison_matrix: List[Dict[str, Any]] = Field(default_factory=list)
    confirmation_status: str = "Pending Review"
    confirmed_by: Optional[str] = None
    confirmed_at: Optional[str] = None
    architect_notes: Optional[str] = None

