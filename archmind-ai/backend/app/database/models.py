import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.database.connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="draft")  # draft, ingesting, analyzing, clarifying, architecting, validated, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_json = Column(JSON, default=dict)

    # Relationships
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    stakeholders = relationship("Stakeholder", back_populates="project", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="project", cascade="all, delete-orphan")
    requirements = relationship("Requirement", back_populates="project", cascade="all, delete-orphan")
    conflicts = relationship("Conflict", back_populates="project", cascade="all, delete-orphan")
    clarifications = relationship("ClarificationQuestion", back_populates="project", cascade="all, delete-orphan")
    components = relationship("ArchitectureComponent", back_populates="project", cascade="all, delete-orphan")
    apis = relationship("APIEndpoint", back_populates="project", cascade="all, delete-orphan")
    data_flows = relationship("DataFlow", back_populates="project", cascade="all, delete-orphan")
    adrs = relationship("ArchitectureDecision", back_populates="project", cascade="all, delete-orphan")
    traceability = relationship("TraceabilityMapping", back_populates="project", cascade="all, delete-orphan")
    risks = relationship("ArchitectureRisk", back_populates="project", cascade="all, delete-orphan")
    validations = relationship("ValidationResult", back_populates="project", cascade="all, delete-orphan")
    impact_analyses = relationship("ChangeImpactAnalysis", back_populates="project", cascade="all, delete-orphan")
    checkpoints = relationship("WorkflowCheckpoint", back_populates="project", cascade="all, delete-orphan")

class Stakeholder(Base):
    __tablename__ = "stakeholders"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    influence_level = Column(String(50), default="high")  # high, medium, low
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="stakeholders")

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, txt, md
    file_size_bytes = Column(Integer, default=0)
    raw_content = Column(Text, nullable=True)
    parsed_metadata = Column(JSON, default=dict)
    status = Column(String(50), default="uploaded")  # uploaded, parsed, indexed, failed
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    evidence_items = relationship("Evidence", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    page_number = Column(Integer, nullable=True)
    embedding = Column(JSON, nullable=True)  # JSON array for cross-DB compatibility
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    evidence_code = Column(String(50), nullable=False)  # e.g., EV-001
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    source_filename = Column(String(255), nullable=False)
    stakeholder_id = Column(String(36), ForeignKey("stakeholders.id", ondelete="SET NULL"), nullable=True)
    statement = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)  # Functional, Non-Functional, Constraint, Policy, Architecture Preference
    original_excerpt = Column(Text, nullable=False)
    location_reference = Column(String(255), nullable=True)  # Section 3.2, Page 4
    confidence_score = Column(Float, default=1.0)
    quality_grade = Column(String(20), default="High")  # High, Medium, Low
    is_duplicate = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="evidence")
    document = relationship("Document", back_populates="evidence_items")

class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    req_code = Column(String(50), nullable=False)  # e.g., REQ-001
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    req_type = Column(String(50), nullable=False)  # Functional, Non-Functional, Technical Constraint, Business Constraint
    category = Column(String(100), nullable=False)  # Security, Performance, Scalability, Compliance, Integration, Core
    priority = Column(String(20), default="Medium")  # Critical, High, Medium, Low
    source_evidence_codes = Column(JSON, default=list)  # ["EV-001", "EV-004"]
    confidence = Column(Float, default=0.95)
    verification_method = Column(String(100), default="Automated Test")  # Test, Inspection, Demonstration, Analysis
    ambiguity_status = Column(String(50), default="Clear")  # Clear, Ambiguous, Incomplete
    approval_status = Column(String(50), default="Pending")  # Fact, Inferred, Assumption, Clarified, Approved, Rejected
    rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="requirements")

class Conflict(Base):
    __tablename__ = "conflicts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conflict_code = Column(String(50), nullable=False)  # e.g., CONF-001
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    conflicting_req_codes = Column(JSON, default=list)  # ["REQ-001", "REQ-002"]
    conflict_type = Column(String(100), nullable=False)  # Direct Contradiction, Semantic Incompatibility, Deployment Conflict, Missing Metric, Assumption
    explanation = Column(Text, nullable=False)
    evidence_excerpts = Column(JSON, default=list)
    severity = Column(String(20), default="High")  # Critical, High, Medium, Low
    business_impact = Column(Text, nullable=False)
    technical_impact = Column(Text, nullable=False)
    suggested_resolution = Column(Text, nullable=False)
    clarification_question = Column(Text, nullable=False)
    confidence = Column(Float, default=0.9)
    status = Column(String(50), default="Detected")  # Detected, Clarifying, Resolved, Overridden
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="conflicts")

class ClarificationQuestion(Base):
    __tablename__ = "clarification_questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    conflict_id = Column(String(36), ForeignKey("conflicts.id", ondelete="SET NULL"), nullable=True)
    question_code = Column(String(50), nullable=False)  # e.g., Q-001
    title = Column(String(255), nullable=False)
    question = Column(Text, nullable=False)
    context_reasoning = Column(Text, nullable=True)
    related_req_codes = Column(JSON, default=list)
    suggested_options = Column(JSON, default=list)  # ["Option A", "Option B", "Option C"]
    status = Column(String(50), default="Pending")  # Pending, Answered, Dismissed
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="clarifications")
    responses = relationship("StakeholderResponse", back_populates="question", cascade="all, delete-orphan")

class StakeholderResponse(Base):
    __tablename__ = "stakeholder_responses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    question_id = Column(String(36), ForeignKey("clarification_questions.id", ondelete="CASCADE"), nullable=False)
    selected_option = Column(String(255), nullable=True)
    custom_answer = Column(Text, nullable=True)
    submitted_by = Column(String(255), default="Human Architect")
    architectural_effect = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    question = relationship("ClarificationQuestion", back_populates="responses")

class ArchitectureComponent(Base):
    __tablename__ = "architecture_components"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    component_code = Column(String(50), nullable=False)  # e.g., COMP-001
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    layer = Column(String(100), nullable=False)  # Frontend / API Gateway / Core Domain / Data Layer / Security / Event Broker
    responsibility = Column(Text, nullable=False)
    technology_stack = Column(String(255), nullable=False)  # e.g., FastAPI, Next.js, Redis, PostgreSQL
    deployment_target = Column(String(100), default="Container / Kubernetes")
    scaling_strategy = Column(String(100), default="Horizontal Auto-scaling")
    security_controls = Column(JSON, default=list)  # ["mTLS", "JWT Validation", "KMS Encryption"]
    related_req_codes = Column(JSON, default=list)  # ["REQ-001", "REQ-004"]
    dependencies = Column(JSON, default=list)  # ["COMP-002", "COMP-005"]
    status = Column(String(50), default="Proposed")  # Proposed, Approved, Superseded
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="components")

class ComponentDependency(Base):
    __tablename__ = "component_dependencies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_component_id = Column(String(36), ForeignKey("architecture_components.id", ondelete="CASCADE"), nullable=False)
    target_component_id = Column(String(36), ForeignKey("architecture_components.id", ondelete="CASCADE"), nullable=False)
    interaction_type = Column(String(100), default="Synchronous REST")  # REST, gRPC, Event Publish, DB Query
    is_critical_path = Column(Boolean, default=False)

class APIEndpoint(Base):
    __tablename__ = "api_endpoints"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    component_code = Column(String(50), nullable=False)
    method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE
    path = Column(String(255), nullable=False)
    summary = Column(String(255), nullable=False)
    auth_requirement = Column(String(100), default="Bearer JWT + RBAC")
    rate_limit = Column(String(100), default="1000 req/min")
    related_req_codes = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="apis")

class DataFlow(Base):
    __tablename__ = "data_flows"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    flow_code = Column(String(50), nullable=False)  # FLOW-001
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    source = Column(String(100), nullable=False)
    target = Column(String(100), nullable=False)
    protocol = Column(String(50), default="HTTPS / REST")
    payload_type = Column(String(100), default="JSON")
    encryption = Column(String(100), default="TLS 1.3 in-transit")
    step_sequence = Column(Integer, default=1)
    description = Column(Text, nullable=True)

    project = relationship("Project", back_populates="data_flows")

class ArchitectureDecision(Base):
    __tablename__ = "architecture_decisions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    adr_code = Column(String(50), nullable=False)  # ADR-001
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(String(50), default="Proposed")  # Proposed, Accepted, Rejected, Superseded
    context = Column(Text, nullable=False)
    problem = Column(Text, nullable=False)
    decision = Column(Text, nullable=False)
    alternatives = Column(JSON, default=list)  # [{"option": "...", "trade_off": "..."}]
    advantages = Column(JSON, default=list)
    disadvantages = Column(JSON, default=list)
    trade_offs = Column(Text, nullable=False)
    supporting_req_codes = Column(JSON, default=list)
    evidence_references = Column(JSON, default=list)
    assumptions = Column(JSON, default=list)
    consequences = Column(Text, nullable=False)
    confidence = Column(Float, default=0.92)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="adrs")

class TraceabilityMapping(Base):
    __tablename__ = "traceability_mappings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    req_code = Column(String(50), nullable=False)
    req_description = Column(Text, nullable=False)
    req_category = Column(String(100), nullable=False)
    evidence_codes = Column(JSON, default=list)
    mapped_component_codes = Column(JSON, default=list)
    related_api_ids = Column(JSON, default=list)
    related_adr_codes = Column(JSON, default=list)
    validation_status = Column(String(50), default="Pass")  # Pass, Warn, Fail, Unverified
    coverage_status = Column(String(50), default="Fully Covered")  # Fully Covered, Partially Covered, Not Covered, Blocked
    coverage_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="traceability")

class ArchitectureRisk(Base):
    __tablename__ = "architecture_risks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    risk_code = Column(String(50), nullable=False)  # RISK-001
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # Security, Scalability, Performance, Operational, Compliance
    likelihood = Column(String(20), default="Medium")  # Low, Medium, High, Critical
    impact = Column(String(20), default="High")  # Low, Medium, High, Critical
    severity = Column(String(20), default="High")  # Low, Medium, High, Critical
    risk_score = Column(Float, default=7.5)
    related_req_codes = Column(JSON, default=list)
    affected_components = Column(JSON, default=list)
    mitigation_strategy = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="risks")

class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    rule_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # Requirement Coverage, Security, Scalability, Component Completeness, Circular Dependencies
    status = Column(String(20), nullable=False)  # Pass, Warn, Fail
    score = Column(Float, default=100.0)
    details = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=True)
    is_deterministic = Column(Boolean, default=True)  # True = deterministic python logic, False = LLM semantic check
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="validations")

class ChangeImpactAnalysis(Base):
    __tablename__ = "change_impact_analyses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    target_req_code = Column(String(50), nullable=False)
    original_description = Column(Text, nullable=False)
    modified_description = Column(Text, nullable=False)
    affected_components = Column(JSON, default=list)
    affected_apis = Column(JSON, default=list)
    affected_adrs = Column(JSON, default=list)
    infrastructure_changes = Column(JSON, default=list)
    performance_risks = Column(JSON, default=list)
    database_implications = Column(Text, nullable=True)
    scaling_requirements = Column(Text, nullable=True)
    new_clarification_questions = Column(JSON, default=list)
    comparison_summary = Column(Text, nullable=False)
    status = Column(String(50), default="Proposed")  # Proposed, Approved, Discarded
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="impact_analyses")

class WorkflowCheckpoint(Base):
    __tablename__ = "workflow_checkpoints"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    step_name = Column(String(100), nullable=False)  # evidence_extraction, requirements_engineering, conflict_intelligence, clarification, architecture_design, validation, traceability
    state_payload = Column(JSON, nullable=False)
    is_paused_for_human = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="checkpoints")

