import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from app.graph.state import ArchMindState
from app.graph.nodes import (
    evidence_extraction_node,
    requirements_engineering_node,
    conflict_intelligence_node,
    clarification_generation_node,
    architecture_reasoning_node,
    security_intelligence_node,
    architecture_validation_node,
    traceability_node
)
from app.graph.routing import should_clarify, should_refine_architecture

logger = logging.getLogger("archmind.graph.workflow")

def human_approval_checkpoint_node(state: ArchMindState) -> Dict[str, Any]:
    """Node where workflow halts to wait for human stakeholder input."""
    logger.info("Human approval checkpoint reached. Workflow paused awaiting stakeholder clarification.")
    return {
        "workflow_status": "clarifying",
        "is_paused_for_human": True,
        "current_step": "human_approval_checkpoint"
    }

def architecture_refinement_node(state: ArchMindState) -> Dict[str, Any]:
    """Automated refinement node if validation flags critical flaws."""
    logger.info("Executing architecture_refinement_node")
    # Mark refinement applied
    return {
        "current_step": "architecture_refinement"
    }

def build_archmind_graph():
    """
    Constructs the end-to-end LangGraph StateGraph pipeline:
    Evidence Extraction
        ↓
    Requirement Extraction
        ↓
    Conflict Detection
        ↓
    Clarification Generation
        ↓
    Clarification Required?
        ├── Yes → Human Approval Checkpoint → END (resumes on user submit)
        └── No → Architecture Design
                        ↓
                 Security Intelligence
                        ↓
                 Architecture Validation
                        ↓
                 Validation Successful?
                    ├── No → Architecture Refinement → Architecture Design
                    └── Yes → Traceability
                                  ↓
                             Final Results (END)
    """
    workflow = StateGraph(ArchMindState)

    # 1. Register Nodes
    workflow.add_node("evidence_extraction", evidence_extraction_node)
    workflow.add_node("requirements_engineering", requirements_engineering_node)
    workflow.add_node("conflict_intelligence", conflict_intelligence_node)
    workflow.add_node("clarification_generation", clarification_generation_node)
    workflow.add_node("human_approval_checkpoint", human_approval_checkpoint_node)
    workflow.add_node("architecture_design", architecture_reasoning_node)
    workflow.add_node("security_intelligence", security_intelligence_node)
    workflow.add_node("architecture_validation", architecture_validation_node)
    workflow.add_node("architecture_refinement", architecture_refinement_node)
    workflow.add_node("traceability", traceability_node)

    # 2. Add Transitions
    workflow.add_edge(START, "evidence_extraction")
    workflow.add_edge("evidence_extraction", "requirements_engineering")
    workflow.add_edge("requirements_engineering", "conflict_intelligence")
    workflow.add_edge("conflict_intelligence", "clarification_generation")

    # Conditional Clarification Branch
    workflow.add_conditional_edges(
        "clarification_generation",
        should_clarify,
        {
            "human_approval_checkpoint": "human_approval_checkpoint",
            "architecture_design": "architecture_design"
        }
    )

    workflow.add_edge("human_approval_checkpoint", END)

    # Architecture Design & Security
    workflow.add_edge("architecture_design", "security_intelligence")
    workflow.add_edge("security_intelligence", "architecture_validation")

    # Conditional Validation Branch
    workflow.add_conditional_edges(
        "architecture_validation",
        should_refine_architecture,
        {
            "architecture_refinement": "architecture_refinement",
            "traceability": "traceability"
        }
    )

    workflow.add_edge("architecture_refinement", "architecture_design")
    workflow.add_edge("traceability", END)

    return workflow.compile()

# Pre-compiled workflow graph instance
archmind_app = build_archmind_graph()

def run_workflow_pipeline(initial_state: ArchMindState) -> ArchMindState:
    """Executes the LangGraph compiled stategraph from the initial state."""
    logger.info(f"Invoking ArchMind LangGraph workflow for project {initial_state.get('project_id')}")
    final_state = archmind_app.invoke(initial_state)
    return final_state

