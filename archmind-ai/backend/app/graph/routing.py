import logging
from typing import Literal
from app.graph.state import ArchMindState

logger = logging.getLogger("archmind.graph.routing")

def should_clarify(state: ArchMindState) -> Literal["human_approval_checkpoint", "architecture_design"]:
    """
    Decides whether workflow requires human-in-the-loop clarification before proceeding to architecture.
    """
    # If there are pending clarification questions and no responses, pause for human approval
    is_paused = state.get("is_paused_for_human", False)
    questions = state.get("clarification_questions", [])
    pending = [q for q in questions if q.get("status") == "Pending"]

    if is_paused and len(pending) > 0:
        logger.info(f"Routing to human_approval_checkpoint ({len(pending)} pending questions)")
        return "human_approval_checkpoint"
    
    logger.info("No human pause required; routing to architecture_design")
    return "architecture_design"

def should_refine_architecture(state: ArchMindState) -> Literal["architecture_refinement", "traceability"]:
    """
    Evaluates whether architecture validation passed or requires automated refinement.
    """
    val_results = state.get("validation_results", {})
    health_score = val_results.get("overall_health_score", 100.0)
    status = val_results.get("status", "Passed")
    iteration = state.get("iteration_count", 0)

    # Allow up to 2 refinement attempts if critical validation failed
    if status == "Failed" and iteration < 2:
        logger.warning(f"Validation failed (score: {health_score}); routing to architecture_refinement (iteration {iteration})")
        return "architecture_refinement"

    logger.info("Validation acceptable or max iterations reached; proceeding to traceability")
    return "traceability"

