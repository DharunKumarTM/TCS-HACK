import os
import shutil
import tempfile
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import (
    Project, Document, Evidence, Requirement, Conflict, ClarificationQuestion,
    StakeholderResponse, ArchitectureComponent, APIEndpoint, DataFlow,
    ArchitectureDecision, TraceabilityMapping, ArchitectureRisk, ValidationResult,
    ChangeImpactAnalysis
)
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectStats
from app.schemas.evidence import EvidenceItem, DocumentResponse
from app.schemas.requirement import RequirementItem, RequirementUpdate
from app.schemas.conflict import ConflictItem, ConflictResolveRequest
from app.schemas.clarification import ClarificationQuestionItem, StakeholderResponseSubmit
from app.schemas.architecture import (
    ComponentItem, APIEndpointItem, DataFlowItem, ADRItem, ADRStatusUpdate,
    ArchitectureRecommendation, ArchitectureComparison, ArchitectureConfirmationRequest,
    TechStackItem, ArchitectureEvolutionModel
)
from app.schemas.traceability import TraceabilityMatrixResponse, TraceabilityItem
from app.schemas.validation import ValidationOverview, ValidationItem, RiskItem
from app.schemas.impact import ImpactAnalysisRequest, ChangeImpactResult, ChangeImpactApplyRequest
from app.services.project_service import project_service
from app.services.report_service import report_service
from app.agents.clarification_agent import clarification_agent
from app.agents.architecture_agent import architecture_agent
from app.agents.traceability_agent import traceability_agent

router = APIRouter(prefix="/api", tags=["ArchMind Core API"])

# --- 1. Projects ---
@router.post("/projects", response_model=ProjectResponse)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    proj = project_service.create_project(db, payload.name, payload.description, payload.metadata)
    return proj

@router.get("/projects", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.created_at.desc()).all()

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return proj

@router.get("/projects/{project_id}/stats", response_model=ProjectStats)
def get_project_stats(project_id: str, db: Session = Depends(get_db)):
    stats = project_service.get_project_stats(db, project_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Project not found")
    return stats

@router.post("/projects/analyze-input")
async def analyze_input(
    project_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    input_mode: str = Form("text"),  # "file" or "text"
    text_content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    pause_for_clarification: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Unified input module: Ingests uploaded PDF/DOC/TXT OR pasted requirements text,
    runs the AI agentic analysis pipeline, and produces architecture and diagrams.
    """
    tmp_path = None
    filename = None

    if file and file.filename:
        filename = file.filename
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

    try:
        result = project_service.create_and_analyze_input(
            db=db,
            project_name=project_name,
            description=description,
            file_path=tmp_path,
            filename=filename,
            text_content=text_content if (input_mode == "text" or not file) else None,
            pause_for_clarification=pause_for_clarification
        )
        return {
            "success": True,
            "project_id": result["project_id"],
            "project_name": result["project_name"],
            "status": result["status"],
            "stats": result["stats"]
        }
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.post("/projects/{project_id}/ingest-text", response_model=DocumentResponse)
def ingest_text_document(
    project_id: str,
    payload: dict,
    run_pipeline: bool = Query(True),
    pause_for_clarification: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Adds raw requirements text to an existing project and runs the analysis pipeline."""
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    text = payload.get("text", "")
    title = payload.get("title", "Requirements_Specification.md")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text content cannot be empty")

    doc = project_service.ingest_raw_text(db, project_id, text, title)
    if run_pipeline:
        project_service.execute_pipeline(db, project_id, pause_for_clarification=pause_for_clarification)

    return doc

@router.post("/projects/demo/smartbank", response_model=ProjectResponse)
def load_smartbank_demo(db: Session = Depends(get_db)):
    """Initializes and executes the SmartBank 2.0 reference project pipeline."""
    proj = project_service.load_demo_smartbank_project(db)
    return proj

@router.post("/projects/{project_id}/run-pipeline")
def trigger_pipeline(project_id: str, pause_for_clarification: bool = True, db: Session = Depends(get_db)):
    state = project_service.execute_pipeline(db, project_id, pause_for_clarification)
    return {
        "status": state.get("workflow_status"),
        "current_step": state.get("current_step"),
        "is_paused_for_human": state.get("is_paused_for_human")
    }

# --- 2. Documents & Evidence ---
@router.post("/projects/{project_id}/documents", response_model=DocumentResponse)
async def upload_document(
    project_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        doc = project_service.ingest_document(db, project_id, tmp_path, file.filename)
        return doc
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.get("/projects/{project_id}/documents", response_model=List[DocumentResponse])
def list_documents(project_id: str, db: Session = Depends(get_db)):
    return db.query(Document).filter(Document.project_id == project_id).all()

@router.get("/projects/{project_id}/evidence", response_model=List[EvidenceItem])
def list_evidence(
    project_id: str,
    category: Optional[str] = None,
    quality: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(Evidence).filter(Evidence.project_id == project_id)
    if category:
        q = q.filter(Evidence.category == category)
    if quality:
        q = q.filter(Evidence.quality_grade == quality)
    return q.all()

# --- 3. Requirements ---
@router.get("/projects/{project_id}/requirements", response_model=List[RequirementItem])
def list_requirements(
    project_id: str,
    req_type: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(Requirement).filter(Requirement.project_id == project_id)
    if req_type:
        q = q.filter(Requirement.req_type == req_type)
    if priority:
        q = q.filter(Requirement.priority == priority)
    if status:
        q = q.filter(Requirement.approval_status == status)
    return q.all()

@router.patch("/requirements/{requirement_id}", response_model=RequirementItem)
def update_requirement(
    requirement_id: str,
    payload: RequirementUpdate,
    db: Session = Depends(get_db)
):
    req = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")

    if payload.title is not None:
        req.title = payload.title
    if payload.description is not None:
        req.description = payload.description
    if payload.priority is not None:
        req.priority = payload.priority
    if payload.approval_status is not None:
        req.approval_status = payload.approval_status
    if payload.ambiguity_status is not None:
        req.ambiguity_status = payload.ambiguity_status

    db.commit()
    db.refresh(req)
    return req

# --- 4. Conflicts ---
@router.get("/projects/{project_id}/conflicts", response_model=List[ConflictItem])
def list_conflicts(
    project_id: str,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(Conflict).filter(Conflict.project_id == project_id)
    if severity:
        q = q.filter(Conflict.severity == severity)
    if status:
        q = q.filter(Conflict.status == status)
    return q.all()

@router.post("/conflicts/{conflict_id}/resolve", response_model=ConflictItem)
def resolve_conflict(
    conflict_id: str,
    payload: ConflictResolveRequest,
    db: Session = Depends(get_db)
):
    conf = db.query(Conflict).filter(Conflict.id == conflict_id).first()
    if not conf:
        raise HTTPException(status_code=404, detail="Conflict not found")

    conf.status = payload.status
    conf.resolution_notes = payload.resolution_notes
    db.commit()
    db.refresh(conf)
    return conf

# --- 5. Clarifications & Human-In-The-Loop ---
@router.get("/projects/{project_id}/clarifications", response_model=List[ClarificationQuestionItem])
def list_clarifications(
    project_id: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(ClarificationQuestion).filter(ClarificationQuestion.project_id == project_id)
    if status:
        q = q.filter(ClarificationQuestion.status == status)
    return q.all()

@router.post("/clarifications/{question_id}/respond")
def submit_clarification_response(
    question_id: str,
    payload: StakeholderResponseSubmit,
    db: Session = Depends(get_db)
):
    q = db.query(ClarificationQuestion).filter(ClarificationQuestion.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    resp = StakeholderResponse(
        question_id=question_id,
        selected_option=payload.selected_option,
        custom_answer=payload.custom_answer,
        submitted_by=payload.submitted_by or "Human Architect"
    )
    db.add(resp)
    q.status = "Answered"
    db.commit()

    # Re-evaluate affected conflicts and requirements
    conflicts = db.query(Conflict).filter(Conflict.project_id == q.project_id).all()
    requirements = db.query(Requirement).filter(Requirement.project_id == q.project_id).all()

    conf_dicts = [{"conflict_code": c.conflict_code, "conflict_type": c.conflict_type, "clarification_question": c.clarification_question, "status": c.status} for c in conflicts]
    req_dicts = [{"req_code": r.req_code, "title": r.title, "ambiguity_status": r.ambiguity_status, "approval_status": r.approval_status} for r in requirements]

    result = clarification_agent.apply_clarification(
        q.question_code,
        payload.selected_option,
        payload.custom_answer,
        conf_dicts,
        req_dicts
    )

    # Sync back resolved conflicts in DB
    for conf_code in result.get("resolved_conflicts", []):
        c_db = db.query(Conflict).filter(Conflict.project_id == q.project_id, Conflict.conflict_code == conf_code).first()
        if c_db:
            c_db.status = "Resolved"
            c_db.resolution_notes = f"Resolved via Clarification response: '{payload.selected_option or payload.custom_answer}'"

    for r_code in result.get("clarified_requirements", []):
        r_db = db.query(Requirement).filter(Requirement.project_id == q.project_id, Requirement.req_code == r_code).first()
        if r_db:
            r_db.ambiguity_status = "Clear"
            r_db.approval_status = "Clarified"

    db.commit()

    # Automatically resume architecture reasoning pipeline now that human input is recorded!
    project_service.execute_pipeline(db, q.project_id, pause_for_clarification=False)

    return {
        "status": "Response accepted and pipeline resumed",
        "question_code": q.question_code,
        "resolved_conflicts": result.get("resolved_conflicts", [])
    }

# --- 6. Architecture & Diagrams ---
@router.get("/projects/{project_id}/architecture", response_model=ArchitectureRecommendation)
def get_architecture(project_id: str, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    comps = db.query(ArchitectureComponent).filter(ArchitectureComponent.project_id == project_id).all()
    apis = db.query(APIEndpoint).filter(APIEndpoint.project_id == project_id).all()
    flows = db.query(DataFlow).filter(DataFlow.project_id == project_id).all()
    adrs = db.query(ArchitectureDecision).filter(ArchitectureDecision.project_id == project_id).all()
    reqs = db.query(Requirement).filter(Requirement.project_id == project_id).all()

    req_dicts = [{"req_code": r.req_code, "title": r.title, "description": r.description} for r in reqs]
    is_smartbank = any("smartbank" in r.title.lower() or "sovereign" in r.title.lower() or "sms otp" in r.title.lower() for r in reqs) or not reqs

    comp_dicts = [ComponentItem.from_orm(c).dict() for c in comps]
    flow_dicts = [DataFlowItem.from_orm(f).dict() for f in flows]

    mermaid_diagrams = architecture_agent._generate_mermaid_diagrams(comp_dicts, flow_dicts)
    evolution = architecture_agent._generate_architecture_evolution(req_dicts, is_smartbank=is_smartbank)
    tech_stacks = architecture_agent._generate_tech_stack_recommendations(req_dicts, is_smartbank=is_smartbank)

    meta = proj.metadata_json or {}
    overrides = meta.get("tech_stack_overrides", {})
    for ts in tech_stacks:
        if ts["category"] in overrides:
            ts["selected"] = overrides[ts["category"]]
            ts["is_overridden"] = True
            ts["overridden_by"] = "Architect Override"

    confirmation = meta.get("architecture_confirmation", {})
    conf_status = confirmation.get("status", "Pending Review")

    return ArchitectureRecommendation(
        architecture_style=evolution["new_architecture"]["style"],
        style_justification=evolution["new_architecture"]["description"],
        components=comps,
        apis=apis,
        data_flows=flows,
        adrs=adrs,
        mermaid_diagrams=mermaid_diagrams,
        tech_stack_recommendations=tech_stacks,
        old_architecture=evolution["old_architecture"],
        new_architecture=evolution["new_architecture"],
        comparison_matrix=evolution["comparison_matrix"],
        confirmation_status=conf_status,
        confirmed_by=confirmation.get("confirmed_by"),
        confirmed_at=confirmation.get("confirmed_at"),
        architect_notes=confirmation.get("notes")
    )

@router.get("/projects/{project_id}/architecture/comparison", response_model=ArchitectureComparison)
def get_architecture_comparison(project_id: str, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    reqs = db.query(Requirement).filter(Requirement.project_id == project_id).all()
    req_dicts = [{"req_code": r.req_code, "title": r.title, "description": r.description} for r in reqs]
    is_smartbank = any("smartbank" in r.title.lower() or "sovereign" in r.title.lower() or "sms otp" in r.title.lower() for r in reqs) or not reqs

    evolution = architecture_agent._generate_architecture_evolution(req_dicts, is_smartbank=is_smartbank)
    tech_stacks = architecture_agent._generate_tech_stack_recommendations(req_dicts, is_smartbank=is_smartbank)

    meta = proj.metadata_json or {}
    overrides = meta.get("tech_stack_overrides", {})
    for ts in tech_stacks:
        if ts["category"] in overrides:
            ts["selected"] = overrides[ts["category"]]
            ts["is_overridden"] = True
            ts["overridden_by"] = "Architect Override"

    confirmation = meta.get("architecture_confirmation", {})

    return ArchitectureComparison(
        project_id=project_id,
        old_architecture=evolution["old_architecture"],
        new_architecture=evolution["new_architecture"],
        comparison_matrix=evolution["comparison_matrix"],
        tech_stack_recommendations=tech_stacks,
        confirmation_status=confirmation.get("status", "Pending Review"),
        confirmed_by=confirmation.get("confirmed_by"),
        confirmed_at=confirmation.get("confirmed_at"),
        architect_notes=confirmation.get("notes"),
        overrides=overrides
    )

@router.post("/projects/{project_id}/architecture/confirm")
def confirm_architecture(
    project_id: str,
    payload: ArchitectureConfirmationRequest,
    db: Session = Depends(get_db)
):
    from datetime import datetime
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    meta = dict(proj.metadata_json or {})

    if payload.action == "confirm":
        meta["architecture_confirmation"] = {
            "status": "Confirmed",
            "confirmed_by": payload.architect_name or "Lead Enterprise Architect",
            "confirmed_at": datetime.utcnow().isoformat(),
            "notes": payload.notes or "Target architecture and tech stack approved for implementation."
        }
        # Update all ADRs in project to Accepted
        adrs = db.query(ArchitectureDecision).filter(ArchitectureDecision.project_id == project_id).all()
        for adr in adrs:
            if adr.status == "Proposed":
                adr.status = "Accepted"
        proj.status = "completed"

    elif payload.action == "customize":
        existing_overrides = meta.get("tech_stack_overrides", {})
        if payload.overrides:
            existing_overrides.update(payload.overrides)
        meta["tech_stack_overrides"] = existing_overrides
        meta["architecture_confirmation"] = {
            "status": "Customized",
            "confirmed_by": payload.architect_name or "Lead Enterprise Architect",
            "confirmed_at": datetime.utcnow().isoformat(),
            "notes": payload.notes or "Tech stack customized by architect."
        }

    elif payload.action == "request_revision":
        meta["architecture_confirmation"] = {
            "status": "Revisions Requested",
            "confirmed_by": payload.architect_name or "Lead Enterprise Architect",
            "confirmed_at": datetime.utcnow().isoformat(),
            "notes": payload.notes or "Revisions requested by architect."
        }
        proj.status = "analyzing"

    proj.metadata_json = meta
    db.commit()
    db.refresh(proj)

    return {
        "success": True,
        "project_id": project_id,
        "action": payload.action,
        "confirmation": meta.get("architecture_confirmation"),
        "overrides": meta.get("tech_stack_overrides", {})
    }

@router.get("/projects/{project_id}/components", response_model=List[ComponentItem])
def list_components(project_id: str, db: Session = Depends(get_db)):
    return db.query(ArchitectureComponent).filter(ArchitectureComponent.project_id == project_id).all()

@router.get("/projects/{project_id}/diagrams")
def get_diagrams(project_id: str, db: Session = Depends(get_db)):
    comps = db.query(ArchitectureComponent).filter(ArchitectureComponent.project_id == project_id).all()
    flows = db.query(DataFlow).filter(DataFlow.project_id == project_id).all()
    comp_dicts = [ComponentItem.from_orm(c).dict() for c in comps]
    flow_dicts = [DataFlowItem.from_orm(f).dict() for f in flows]
    return architecture_agent._generate_mermaid_diagrams(comp_dicts, flow_dicts)

# --- 7. ADRs ---
@router.get("/projects/{project_id}/adrs", response_model=List[ADRItem])
def list_adrs(project_id: str, status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(ArchitectureDecision).filter(ArchitectureDecision.project_id == project_id)
    if status:
        q = q.filter(ArchitectureDecision.status == status)
    return q.all()

@router.patch("/adrs/{adr_id}", response_model=ADRItem)
def update_adr_status(adr_id: str, payload: ADRStatusUpdate, db: Session = Depends(get_db)):
    adr = db.query(ArchitectureDecision).filter(ArchitectureDecision.id == adr_id).first()
    if not adr:
        raise HTTPException(status_code=404, detail="ADR not found")

    adr.status = payload.status
    db.commit()
    db.refresh(adr)
    return adr

# --- 8. Traceability Matrix ---
@router.get("/projects/{project_id}/traceability", response_model=TraceabilityMatrixResponse)
def get_traceability(project_id: str, db: Session = Depends(get_db)):
    reqs = db.query(Requirement).filter(Requirement.project_id == project_id).all()
    comps = db.query(ArchitectureComponent).filter(ArchitectureComponent.project_id == project_id).all()
    apis = db.query(APIEndpoint).filter(APIEndpoint.project_id == project_id).all()
    adrs = db.query(ArchitectureDecision).filter(ArchitectureDecision.project_id == project_id).all()
    conflicts = db.query(Conflict).filter(Conflict.project_id == project_id).all()

    matrix = traceability_agent.build_traceability_matrix(
        [RequirementItem.from_orm(r).dict() for r in reqs],
        [ComponentItem.from_orm(c).dict() for c in comps],
        [APIEndpointItem.from_orm(a).dict() for a in apis],
        [ADRItem.from_orm(a).dict() for a in adrs],
        [ConflictItem.from_orm(c).dict() for c in conflicts]
    )
    return matrix

# --- 9. Validation & Risk Engine ---
@router.get("/projects/{project_id}/validation", response_model=ValidationOverview)
def get_validation_overview(project_id: str, db: Session = Depends(get_db)):
    validations = db.query(ValidationResult).filter(ValidationResult.project_id == project_id).all()
    risks = db.query(ArchitectureRisk).filter(ArchitectureRisk.project_id == project_id).all()

    passed = len([v for v in validations if v.status == "Pass"])
    warned = len([v for v in validations if v.status == "Warn"])
    failed = len([v for v in validations if v.status == "Fail"])

    avg_score = sum(v.score for v in validations) / max(1, len(validations)) if validations else 100.0
    status = "Passed" if failed == 0 and avg_score >= 80 else ("Warning" if failed == 0 else "Failed")

    return ValidationOverview(
        overall_health_score=round(avg_score, 1),
        status=status,
        passed_rules_count=passed,
        warned_rules_count=warned,
        failed_rules_count=failed,
        validations=validations,
        risks=risks
    )

# --- 10. Change Impact Simulator ---
@router.post("/projects/{project_id}/impact-analysis", response_model=ChangeImpactResult)
def simulate_change_impact(
    project_id: str,
    payload: ImpactAnalysisRequest,
    db: Session = Depends(get_db)
):
    reqs = db.query(Requirement).filter(Requirement.project_id == project_id).all()
    comps = db.query(ArchitectureComponent).filter(ArchitectureComponent.project_id == project_id).all()
    apis = db.query(APIEndpoint).filter(APIEndpoint.project_id == project_id).all()
    adrs = db.query(ArchitectureDecision).filter(ArchitectureDecision.project_id == project_id).all()
    risks = db.query(ArchitectureRisk).filter(ArchitectureRisk.project_id == project_id).all()

    result = traceability_agent.simulate_change_impact(
        payload.target_req_code,
        payload.modified_description,
        [RequirementItem.from_orm(r).dict() for r in reqs],
        [ComponentItem.from_orm(c).dict() for c in comps],
        [APIEndpointItem.from_orm(a).dict() for a in apis],
        [ADRItem.from_orm(a).dict() for a in adrs],
        [RiskItem.from_orm(r).dict() for r in risks]
    )

    # Persist analysis
    analysis_record = ChangeImpactAnalysis(
        project_id=project_id,
        target_req_code=payload.target_req_code,
        original_description=result["original_description"],
        modified_description=result["modified_description"],
        affected_components=result["affected_components"],
        affected_apis=result["affected_apis"],
        affected_adrs=result["affected_adrs"],
        infrastructure_changes=result["infrastructure_changes"],
        performance_risks=result["performance_risks"],
        database_implications=result.get("database_implications"),
        scaling_requirements=result.get("scaling_requirements"),
        new_clarification_questions=result["new_clarification_questions"],
        comparison_summary=result["comparison_summary"],
        status="Proposed"
    )
    db.add(analysis_record)
    db.commit()
    db.refresh(analysis_record)

    result["id"] = analysis_record.id
    return result

@router.post("/impact-analysis/apply")
def apply_change_impact(payload: ChangeImpactApplyRequest, db: Session = Depends(get_db)):
    record = db.query(ChangeImpactAnalysis).filter(ChangeImpactAnalysis.id == payload.analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found")

    record.status = "Approved"
    # Update requirement text
    req = db.query(Requirement).filter(Requirement.project_id == record.project_id, Requirement.req_code == record.target_req_code).first()
    if req:
        req.description = record.modified_description
        req.approval_status = "Approved"

    db.commit()
    return {"status": "Change applied to requirement. Proposed architecture revision flagged for next cycle."}

# --- 11. Reports ---
@router.get("/projects/{project_id}/report", response_class=PlainTextResponse)
def get_markdown_report(project_id: str, db: Session = Depends(get_db)):
    return report_service.generate_markdown_report(db, project_id)

