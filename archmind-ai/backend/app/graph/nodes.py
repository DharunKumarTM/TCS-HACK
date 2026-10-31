import logging
from typing import Dict, Any
from app.graph.state import ArchMindState
from app.agents.evidence_agent import evidence_agent
from app.agents.requirements_agent import requirements_agent
from app.agents.conflict_agent import conflict_agent
from app.agents.clarification_agent import clarification_agent
from app.agents.architecture_agent import architecture_agent
from app.agents.security_agent import security_agent
from app.agents.validation_agent import validation_agent
from app.agents.traceability_agent import traceability_agent

logger = logging.getLogger("archmind.graph.nodes")

def evidence_extraction_node(state: ArchMindState) -> Dict[str, Any]:
    """Agent 1: Evidence Intelligence Node."""
    logger.info("Executing evidence_extraction_node")
    docs = state.get("documents", [])
    chunks = []
    for doc in docs:
        chunks.extend(doc.get("chunks", []))

    extracted = evidence_agent.extract_evidence(docs, chunks)
    return {
        "extracted_evidence": extracted,
        "workflow_status": "analyzing",
        "current_step": "evidence_extraction"
    }

def requirements_engineering_node(state: ArchMindState) -> Dict[str, Any]:
    """Agent 2: Requirements Engineering Node."""
    logger.info("Executing requirements_engineering_node")
    evidence_list = state.get("extracted_evidence", [])
    reqs = requirements_agent.analyze_requirements(evidence_list)
    return {
        "requirements": reqs,
        "workflow_status": "analyzing",
        "current_step": "requirements_engineering"
    }

def conflict_intelligence_node(state: ArchMindState) -> Dict[str, Any]:
    """Agent 3: Conflict Intelligence Node."""
    logger.info("Executing conflict_intelligence_node")
    reqs = state.get("requirements", [])
    evidence_list = state.get("extracted_evidence", [])
    conflicts = conflict_agent.detect_conflicts(reqs, evidence_list)

    # If stakeholder responses already exist, mark affected conflicts as Resolved
    responses = state.get("stakeholder_responses", [])
    for r in responses:
        ans = r.get("selected_option") or r.get("custom_answer") or ""
        if ans:
            for conf in conflicts:
                if any(k in ans for k in ["Adaptive", "Step-Up", "SMS"]) and "Authentication" in conf.get("conflict_type", ""):
                    conf["status"] = "Resolved"
                    conf["resolution_notes"] = f"Resolved via stakeholder clarification: {ans}"
                elif any(k in ans for k in ["Sovereign", "Hybrid", "Tier-IV"]) and ("Deployment" in conf.get("conflict_type", "") or "Sovereignty" in conf.get("conflict_type", "")):
                    conf["status"] = "Resolved"
                    conf["resolution_notes"] = f"Resolved via stakeholder clarification: {ans}"
                elif any(k in ans for k in ["Edge", "Redis", "Stateless"]) and "Performance" in conf.get("conflict_type", ""):
                    conf["status"] = "Resolved"
                    conf["resolution_notes"] = f"Resolved via stakeholder clarification: {ans}"

    return {
        "conflicts": conflicts,
        "workflow_status": "analyzing",
        "current_step": "conflict_intelligence"
    }

def clarification_generation_node(state: ArchMindState) -> Dict[str, Any]:
    """Agent 4: Clarification Generation Node."""
    logger.info("Executing clarification_generation_node")
    conflicts = state.get("conflicts", [])
    reqs = state.get("requirements", [])
    questions = clarification_agent.generate_questions(conflicts, reqs)
    
    # Check if pause is requested by caller and if unresolved questions exist
    pause_requested = state.get("is_paused_for_human", True)
    unanswered = [q for q in questions if q.get("status") == "Pending"]
    needs_pause = pause_requested and len(unanswered) > 0 and not state.get("stakeholder_responses", [])

    return {
        "clarification_questions": questions,
        "workflow_status": "clarifying" if needs_pause else "architecting",
        "current_step": "clarification_generation",
        "is_paused_for_human": needs_pause
    }

def architecture_reasoning_node(state: ArchMindState) -> Dict[str, Any]:
    """Agent 5: Architecture Reasoning Node."""
    logger.info("Executing architecture_reasoning_node")
    reqs = state.get("requirements", [])
    conflicts = state.get("conflicts", [])
    evidence_list = state.get("extracted_evidence", [])

    arch_result = architecture_agent.design_architecture(reqs, conflicts, evidence_list)
    components = arch_result.get("components", [])
    apis = arch_result.get("apis", [])
    data_flows = arch_result.get("data_flows", [])
    adrs = arch_result.get("adrs", [])

    return {
        "architecture_recommendations": arch_result,
        "components": components,
        "apis": apis,
        "data_flows": data_flows,
        "adrs": adrs,
        "workflow_status": "architecting",
        "current_step": "architecture_reasoning"
    }

def security_intelligence_node(state: ArchMindState) -> Dict[str, Any]:
    """Agent 6: Security Intelligence Node."""
    logger.info("Executing security_intelligence_node")
    components = state.get("components", [])
    reqs = state.get("requirements", [])
    sec_analysis = security_agent.analyze_security(components, reqs)

    # Attach security controls to components if needed
    return {
        "security_analysis": sec_analysis,
        "current_step": "security_intelligence"
    }

def architecture_validation_node(state: ArchMindState) -> Dict[str, Any]:
    """Agent 7: Architecture Validation Node."""
    logger.info("Executing architecture_validation_node")
    components = state.get("components", [])
    reqs = state.get("requirements", [])
    adrs = state.get("adrs", [])
    conflicts = state.get("conflicts", [])

    val_result = validation_agent.validate_architecture(components, reqs, adrs, conflicts)
    risks = val_result.get("risks", [])

    iteration = state.get("iteration_count", 0) + 1

    return {
        "validation_results": val_result,
        "risks": risks,
        "iteration_count": iteration,
        "workflow_status": "validated",
        "current_step": "architecture_validation"
    }

def traceability_node(state: ArchMindState) -> Dict[str, Any]:
    """Agent 8: Traceability and Change Impact Node."""
    logger.info("Executing traceability_node")
    reqs = state.get("requirements", [])
    components = state.get("components", [])
    apis = state.get("apis", [])
    adrs = state.get("adrs", [])
    conflicts = state.get("conflicts", [])

    trace_result = traceability_agent.build_traceability_matrix(
        reqs, components, apis, adrs, conflicts
    )

    return {
        "traceability_mappings": trace_result,
        "workflow_status": "completed",
        "current_step": "traceability"
    }
