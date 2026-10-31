import os
import glob
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.models import (
    Project, Document, DocumentChunk, Evidence, Requirement, Conflict,
    ClarificationQuestion, StakeholderResponse, ArchitectureComponent,
    APIEndpoint, DataFlow, ArchitectureDecision, TraceabilityMapping,
    ArchitectureRisk, ValidationResult, ChangeImpactAnalysis, WorkflowCheckpoint
)
from app.rag.document_parser import document_parser
from app.rag.chunking import semantic_chunker
from app.rag.embeddings import embedding_service
from app.graph.workflow import archmind_app, run_workflow_pipeline
from app.graph.state import ArchMindState
from app.agents.clarification_agent import clarification_agent
from app.agents.traceability_agent import traceability_agent

logger = logging.getLogger("archmind.services.project")

class ProjectService:
    """Orchestrates database persistence, document ingestion, and LangGraph workflow executions."""

    def create_project(self, db: Session, name: str, description: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Project:
        project = Project(
            name=name,
            description=description or "AI-Assisted Architecture Project",
            status="draft",
            metadata_json=metadata or {}
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    def load_demo_smartbank_project(self, db: Session) -> Project:
        """
        Creates or resets the SmartBank Demonstration Project using real PRD, meeting transcripts, and policies.
        """
        # Check if already exists
        existing = db.query(Project).filter(Project.name.like("%SmartBank%")).first()
        if existing:
            return existing

        project = self.create_project(
            db,
            name="SmartBank 2.0 - Next-Gen Digital Banking Platform",
            description="TCS AI Hackathon Challenge 02 Reference Project: Transforming conflicting, fragmented requirements into sovereign hybrid architecture.",
            metadata={"demo": True, "category": "FinTech / Retail Banking"}
        )

        # Ingest sample files
        sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../sample_data"))
        sample_files = [
            os.path.join(sample_dir, "smartbank", "smartbank_prd.md"),
            os.path.join(sample_dir, "meeting_transcripts", "architecture_alignment_meeting.txt"),
            os.path.join(sample_dir, "policies", "infosec_and_compliance_policy.md"),
        ]

        for filepath in sample_files:
            if os.path.exists(filepath):
                self.ingest_document(db, project.id, filepath, os.path.basename(filepath))

        # Run pipeline
        self.execute_pipeline(db, project.id, pause_for_clarification=True)
        return project

    def ingest_document(self, db: Session, project_id: str, file_path: str, filename: str) -> Document:
        """Parses, chunks, and indexes an uploaded or sample document."""
        parsed = document_parser.parse_file(file_path, filename)
        doc = Document(
            project_id=project_id,
            filename=filename,
            file_type=parsed["file_type"],
            file_size_bytes=os.path.getsize(file_path) if os.path.exists(file_path) else len(parsed["raw_text"]),
            raw_content=parsed["raw_text"],
            parsed_metadata={
                "sections": parsed.get("sections", []),
                "quotes_count": len(parsed.get("stakeholder_quotes", []))
            },
            status="parsed"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # Generate semantic chunks and embeddings
        chunks_data = semantic_chunker.chunk_text(parsed["raw_text"], doc.id, filename)
        for c in chunks_data:
            emb = embedding_service.get_embedding(c["content"])
            chunk_obj = DocumentChunk(
                document_id=doc.id,
                chunk_index=c["chunk_index"],
                content=c["content"],
                token_count=c["token_count"],
                page_number=c["page_number"],
                embedding=emb
            )
            db.add(chunk_obj)

        db.commit()
        return doc

    def ingest_raw_text(self, db: Session, project_id: str, text: str, title: str = "Pasted_Requirements.md") -> Document:
        """Parses, chunks, and indexes user-written or pasted requirements text."""
        sections = document_parser._extract_sections(text)
        quotes = document_parser._extract_stakeholder_quotes(text)

        doc = Document(
            project_id=project_id,
            filename=title,
            file_type="md",
            file_size_bytes=len(text.encode("utf-8")),
            raw_content=text,
            parsed_metadata={
                "sections": sections,
                "quotes_count": len(quotes)
            },
            status="parsed"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # Generate semantic chunks and embeddings
        chunks_data = semantic_chunker.chunk_text(text, doc.id, title)
        for c in chunks_data:
            emb = embedding_service.get_embedding(c["content"])
            chunk_obj = DocumentChunk(
                document_id=doc.id,
                chunk_index=c["chunk_index"],
                content=c["content"],
                token_count=c["token_count"],
                page_number=c["page_number"],
                embedding=emb
            )
            db.add(chunk_obj)

        db.commit()
        return doc

    def create_and_analyze_input(
        self,
        db: Session,
        project_name: Optional[str] = None,
        description: Optional[str] = None,
        file_path: Optional[str] = None,
        filename: Optional[str] = None,
        text_content: Optional[str] = None,
        pause_for_clarification: bool = False
    ) -> Dict[str, Any]:
        """
        Creates a new project from either an uploaded document or pasted text,
        ingests the requirements, and executes the complete agentic pipeline.
        """
        name = project_name
        if not name:
            if filename:
                name = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title() + " Architecture"
            elif text_content:
                first_line = text_content.strip().split("\n")[0][:45]
                name = first_line.lstrip("#*•- ").strip() or "Custom Requirements Project"
            else:
                name = "Custom Requirements Project"

        project = self.create_project(
            db,
            name=name,
            description=description or f"Architecture synthesized by ArchMind AI from {filename or 'custom text input'}",
            metadata={"source": "upload" if file_path else "text_input"}
        )

        # Ingest file if uploaded
        if file_path and filename:
            self.ingest_document(db, project.id, file_path, filename)

        # Ingest pasted text if provided
        if text_content and text_content.strip():
            self.ingest_raw_text(db, project.id, text_content.strip(), title=f"{name[:30]}_Spec.md")

        # Execute the 8-agent LangGraph workflow
        final_state = self.execute_pipeline(db, project.id, pause_for_clarification=pause_for_clarification)
        stats = self.get_project_stats(db, project.id)

        return {
            "project_id": project.id,
            "project_name": project.name,
            "status": project.status,
            "stats": stats,
            "state": final_state
        }

    def execute_pipeline(self, db: Session, project_id: str, pause_for_clarification: bool = True) -> Dict[str, Any]:
        """
        Executes LangGraph pipeline for the project and persists state to database tables.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Load documents and chunks
        docs = db.query(Document).filter(Document.project_id == project_id).all()
        doc_payloads = []
        for doc in docs:
            chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).all()
            doc_payloads.append({
                "id": doc.id,
                "filename": doc.filename,
                "raw_text": doc.raw_content or "",
                "sections": doc.parsed_metadata.get("sections", []) if doc.parsed_metadata else [],
                "stakeholder_quotes": [],
                "chunks": [{"content": c.content, "page_number": c.page_number} for c in chunks]
            })

        # Check existing stakeholder responses to see if human already answered
        existing_responses = (
            db.query(StakeholderResponse)
            .join(ClarificationQuestion, StakeholderResponse.question_id == ClarificationQuestion.id)
            .filter(ClarificationQuestion.project_id == project_id)
            .all()
        )
        response_dicts = [
            {"question_id": r.question_id, "selected_option": r.selected_option, "custom_answer": r.custom_answer}
            for r in existing_responses
        ]

        # Check existing conflicts in DB to preserve resolution status
        db_conflicts = db.query(Conflict).filter(Conflict.project_id == project_id).all()
        resolved_dict = {c.conflict_code: c for c in db_conflicts if c.status == "Resolved"}

        initial_state: ArchMindState = {
            "project_id": project_id,
            "documents": doc_payloads,
            "extracted_evidence": [],
            "requirements": [],
            "conflicts": [],
            "clarification_questions": [],
            "stakeholder_responses": response_dicts,
            "architecture_recommendations": {},
            "components": [],
            "apis": [],
            "data_flows": [],
            "adrs": [],
            "validation_results": {},
            "traceability_mappings": {},
            "risks": [],
            "workflow_status": "analyzing",
            "current_step": "start",
            "error_information": None,
            "iteration_count": 0,
            "is_paused_for_human": pause_for_clarification and len(response_dicts) == 0
        }

        # Invoke LangGraph workflow
        final_state = run_workflow_pipeline(initial_state)

        # Restore resolved status for previously resolved conflicts
        for conf in final_state.get("conflicts", []):
            if conf["conflict_code"] in resolved_dict:
                conf["status"] = "Resolved"
                conf["resolution_notes"] = resolved_dict[conf["conflict_code"]].resolution_notes

        # Persist results to DB
        self._persist_state_to_db(db, project_id, final_state)
        return final_state

    def _persist_state_to_db(self, db: Session, project_id: str, state: ArchMindState):
        """Saves generated entities from state into PostgreSQL / SQLite relational models."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.status = state.get("workflow_status", "completed")
            project.updated_at = datetime.utcnow()

        # 1. Evidence
        for ev in state.get("extracted_evidence", []):
            exists = db.query(Evidence).filter(Evidence.project_id == project_id, Evidence.evidence_code == ev["evidence_code"]).first()
            if not exists:
                db.add(Evidence(
                    project_id=project_id,
                    evidence_code=ev["evidence_code"],
                    source_filename=ev["source_filename"],
                    statement=ev["statement"],
                    category=ev["category"],
                    original_excerpt=ev["original_excerpt"],
                    location_reference=ev.get("location_reference"),
                    confidence_score=ev.get("confidence_score", 1.0),
                    quality_grade=ev.get("quality_grade", "High"),
                    is_duplicate=ev.get("is_duplicate", False)
                ))

        # 2. Requirements
        for req in state.get("requirements", []):
            exists = db.query(Requirement).filter(Requirement.project_id == project_id, Requirement.req_code == req["req_code"]).first()
            if not exists:
                db.add(Requirement(
                    project_id=project_id,
                    req_code=req["req_code"],
                    title=req["title"],
                    description=req["description"],
                    req_type=req["req_type"],
                    category=req["category"],
                    priority=req["priority"],
                    source_evidence_codes=req.get("source_evidence_codes", []),
                    confidence=req.get("confidence", 0.95),
                    verification_method=req.get("verification_method", "Automated Test"),
                    ambiguity_status=req.get("ambiguity_status", "Clear"),
                    approval_status=req.get("approval_status", "Pending"),
                    rationale=req.get("rationale")
                ))

        # 3. Conflicts
        for conf in state.get("conflicts", []):
            exists = db.query(Conflict).filter(Conflict.project_id == project_id, Conflict.conflict_code == conf["conflict_code"]).first()
            if not exists:
                db.add(Conflict(
                    project_id=project_id,
                    conflict_code=conf["conflict_code"],
                    conflicting_req_codes=conf.get("conflicting_req_codes", []),
                    conflict_type=conf["conflict_type"],
                    explanation=conf["explanation"],
                    evidence_excerpts=conf.get("evidence_excerpts", []),
                    severity=conf.get("severity", "High"),
                    business_impact=conf.get("business_impact", ""),
                    technical_impact=conf.get("technical_impact", ""),
                    suggested_resolution=conf.get("suggested_resolution", ""),
                    clarification_question=conf.get("clarification_question", ""),
                    confidence=conf.get("confidence", 0.9),
                    status=conf.get("status", "Detected")
                ))
            else:
                exists.status = conf.get("status", exists.status)
                exists.resolution_notes = conf.get("resolution_notes", exists.resolution_notes)

        # 4. Clarifications
        for q in state.get("clarification_questions", []):
            exists = db.query(ClarificationQuestion).filter(ClarificationQuestion.project_id == project_id, ClarificationQuestion.question_code == q["question_code"]).first()
            if not exists:
                db.add(ClarificationQuestion(
                    project_id=project_id,
                    question_code=q["question_code"],
                    title=q["title"],
                    question=q["question"],
                    context_reasoning=q.get("context_reasoning"),
                    related_req_codes=q.get("related_req_codes", []),
                    suggested_options=q.get("suggested_options", []),
                    status=q.get("status", "Pending")
                ))

        # 5. Components
        for comp in state.get("components", []):
            exists = db.query(ArchitectureComponent).filter(ArchitectureComponent.project_id == project_id, ArchitectureComponent.component_code == comp["component_code"]).first()
            if not exists:
                db.add(ArchitectureComponent(
                    project_id=project_id,
                    component_code=comp["component_code"],
                    name=comp["name"],
                    layer=comp["layer"],
                    responsibility=comp["responsibility"],
                    technology_stack=comp["technology_stack"],
                    deployment_target=comp.get("deployment_target", "Container"),
                    scaling_strategy=comp.get("scaling_strategy", "Horizontal"),
                    security_controls=comp.get("security_controls", []),
                    related_req_codes=comp.get("related_req_codes", []),
                    dependencies=comp.get("dependencies", []),
                    status=comp.get("status", "Proposed")
                ))

        # 6. APIs
        for api in state.get("apis", []):
            exists = db.query(APIEndpoint).filter(APIEndpoint.project_id == project_id, APIEndpoint.path == api["path"], APIEndpoint.method == api["method"]).first()
            if not exists:
                db.add(APIEndpoint(
                    project_id=project_id,
                    component_code=api["component_code"],
                    method=api["method"],
                    path=api["path"],
                    summary=api["summary"],
                    auth_requirement=api.get("auth_requirement", "Bearer JWT"),
                    rate_limit=api.get("rate_limit", "1000 req/min"),
                    related_req_codes=api.get("related_req_codes", [])
                ))

        # 7. Data Flows
        for flow in state.get("data_flows", []):
            exists = db.query(DataFlow).filter(DataFlow.project_id == project_id, DataFlow.flow_code == flow["flow_code"]).first()
            if not exists:
                db.add(DataFlow(
                    project_id=project_id,
                    flow_code=flow["flow_code"],
                    title=flow["title"],
                    source=flow["source"],
                    target=flow["target"],
                    protocol=flow.get("protocol", "HTTPS"),
                    payload_type=flow.get("payload_type", "JSON"),
                    encryption=flow.get("encryption", "TLS 1.3"),
                    step_sequence=flow.get("step_sequence", 1),
                    description=flow.get("description")
                ))

        # 8. ADRs
        for adr in state.get("adrs", []):
            exists = db.query(ArchitectureDecision).filter(ArchitectureDecision.project_id == project_id, ArchitectureDecision.adr_code == adr["adr_code"]).first()
            if not exists:
                db.add(ArchitectureDecision(
                    project_id=project_id,
                    adr_code=adr["adr_code"],
                    title=adr["title"],
                    status=adr.get("status", "Proposed"),
                    context=adr["context"],
                    problem=adr["problem"],
                    decision=adr["decision"],
                    alternatives=adr.get("alternatives", []),
                    advantages=adr.get("advantages", []),
                    disadvantages=adr.get("disadvantages", []),
                    trade_offs=adr["trade_offs"],
                    supporting_req_codes=adr.get("supporting_req_codes", []),
                    evidence_references=adr.get("evidence_references", []),
                    assumptions=adr.get("assumptions", []),
                    consequences=adr["consequences"],
                    confidence=adr.get("confidence", 0.95)
                ))

        # 9. Traceability Mappings
        trace_data = state.get("traceability_mappings", {})
        for item in trace_data.get("items", []):
            exists = db.query(TraceabilityMapping).filter(TraceabilityMapping.project_id == project_id, TraceabilityMapping.req_code == item["req_code"]).first()
            if not exists:
                db.add(TraceabilityMapping(
                    project_id=project_id,
                    req_code=item["req_code"],
                    req_description=item["req_description"],
                    req_category=item["req_category"],
                    evidence_codes=item.get("evidence_codes", []),
                    mapped_component_codes=item.get("mapped_component_codes", []),
                    related_api_ids=item.get("related_api_ids", []),
                    related_adr_codes=item.get("related_adr_codes", []),
                    validation_status=item.get("validation_status", "Pass"),
                    coverage_status=item.get("coverage_status", "Fully Covered"),
                    coverage_score=item.get("coverage_score", 1.0)
                ))
            else:
                exists.mapped_component_codes = item.get("mapped_component_codes", [])
                exists.related_api_ids = item.get("related_api_ids", [])
                exists.related_adr_codes = item.get("related_adr_codes", [])
                exists.validation_status = item.get("validation_status", "Pass")
                exists.coverage_status = item.get("coverage_status", "Fully Covered")
                exists.coverage_score = item.get("coverage_score", 1.0)

        # 10. Risks
        for risk in state.get("risks", []):
            exists = db.query(ArchitectureRisk).filter(ArchitectureRisk.project_id == project_id, ArchitectureRisk.risk_code == risk["risk_code"]).first()
            if not exists:
                db.add(ArchitectureRisk(
                    project_id=project_id,
                    risk_code=risk["risk_code"],
                    title=risk["title"],
                    category=risk["category"],
                    likelihood=risk.get("likelihood", "Medium"),
                    impact=risk.get("impact", "High"),
                    severity=risk.get("severity", "High"),
                    risk_score=risk.get("risk_score", 7.0),
                    related_req_codes=risk.get("related_req_codes", []),
                    affected_components=risk.get("affected_components", []),
                    mitigation_strategy=risk["mitigation_strategy"]
                ))

        # 11. Validations
        val_data = state.get("validation_results", {})
        for v in val_data.get("validations", []):
            exists = db.query(ValidationResult).filter(ValidationResult.project_id == project_id, ValidationResult.rule_name == v["rule_name"]).first()
            if not exists:
                db.add(ValidationResult(
                    project_id=project_id,
                    rule_name=v["rule_name"],
                    category=v["category"],
                    status=v["status"],
                    score=v.get("score", 100.0),
                    details=v["details"],
                    recommendation=v.get("recommendation"),
                    is_deterministic=v.get("is_deterministic", True)
                ))

        # 12. Checkpoint
        db.add(WorkflowCheckpoint(
            project_id=project_id,
            step_name=state.get("current_step", "completed"),
            state_payload={"status": state.get("workflow_status"), "step": state.get("current_step")},
            is_paused_for_human=state.get("is_paused_for_human", False)
        ))

        db.commit()

    def get_project_stats(self, db: Session, project_id: str) -> Dict[str, Any]:
        """Calculates live project metrics directly from database."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {}

        total_docs = db.query(Document).filter(Document.project_id == project_id).count()
        total_ev = db.query(Evidence).filter(Evidence.project_id == project_id).count()
        total_reqs = db.query(Requirement).filter(Requirement.project_id == project_id).count()
        total_conf = db.query(Conflict).filter(Conflict.project_id == project_id).count()
        resolved_conf = db.query(Conflict).filter(Conflict.project_id == project_id, Conflict.status == "Resolved").count()
        pending_clarifications = db.query(ClarificationQuestion).filter(ClarificationQuestion.project_id == project_id, ClarificationQuestion.status == "Pending").count()
        total_comp = db.query(ArchitectureComponent).filter(ArchitectureComponent.project_id == project_id).count()
        total_adrs = db.query(ArchitectureDecision).filter(ArchitectureDecision.project_id == project_id).count()

        # Compute coverage
        trace_items = db.query(TraceabilityMapping).filter(TraceabilityMapping.project_id == project_id).all()
        fully_covered = len([t for t in trace_items if t.coverage_status == "Fully Covered"])
        coverage_score = round((fully_covered / max(1, len(trace_items))) * 100.0, 1) if trace_items else 0.0

        # Risk score average
        risks = db.query(ArchitectureRisk).filter(ArchitectureRisk.project_id == project_id).all()
        risk_score = round(sum(r.risk_score for r in risks) / max(1, len(risks)), 1) if risks else 0.0

        # Validations
        validations = db.query(ValidationResult).filter(ValidationResult.project_id == project_id).all()
        has_failures = any(v.status == "Fail" for v in validations)

        return {
            "project_id": project.id,
            "project_name": project.name,
            "status": project.status,
            "total_documents": total_docs,
            "total_evidence": total_ev,
            "total_requirements": total_reqs,
            "total_conflicts": total_conf,
            "resolved_conflicts": resolved_conf,
            "pending_clarifications": pending_clarifications,
            "total_components": total_comp,
            "total_adrs": total_adrs,
            "coverage_score": coverage_score,
            "risk_score": risk_score,
            "validation_passed": not has_failures
        }

project_service = ProjectService()
