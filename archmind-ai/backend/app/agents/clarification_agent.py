import logging
from typing import List, Dict, Any, Optional
from app.services.gemini_service import gemini_service

logger = logging.getLogger("archmind.agents.clarification")

SYSTEM_PROMPT = """You are the Clarification Agent of ArchMind AI.
Formulate clear, highly architectural, multiple-choice questions for engineering stakeholders.
Each question must target an unverified assumption, contradiction, or missing SLA threshold.
Provide 3-4 distinct architectural trade-off options so stakeholders can make definitive decisions."""

class ClarificationAgent:
    """Agent 4: Generates stakeholder clarification questions and re-evaluates conflicts upon resolution."""

    def generate_questions(
        self,
        conflicts: List[Dict[str, Any]],
        requirements: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        questions = []
        q_idx = 1

        # Generate a question for each detected conflict
        for conflict in conflicts:
            conflict_code = conflict["conflict_code"]
            conf_type = conflict["conflict_type"]
            req_codes = conflict.get("conflicting_req_codes", [])

            if "Authentication" in conf_type or "SMS OTP" in conflict["explanation"]:
                questions.append({
                    "question_code": f"Q-{q_idx:03d}",
                    "conflict_code": conflict_code,
                    "title": "Authentication Strategy & Regulatory Step-Up Alignment",
                    "question": (
                        "How should SmartBank reconcile the CX demand for FIDO2 passwordless login with "
                        "the Mobile team's requirement for SMS OTP onboarding and CISO's PCI-DSS 4.0 mandate prohibiting SMS for funds transfers?"
                    ),
                    "context_reasoning": (
                        "Direct collision between accessibility (SMS OTP for 65% of users), modern user experience (FIDO2), "
                        "and mandatory banking compliance (PCI-DSS 4.0 prohibiting SMS OTP for privileged operations)."
                    ),
                    "related_req_codes": req_codes,
                    "suggested_options": [
                        "Adopt Adaptive Step-Up: SMS/WhatsApp OTP for low-risk retail onboarding; mandatory FIDO2/biometrics or TOTP for transfers > $250.",
                        "Strict FIDO2 Only: Enforce biometric / WebAuthn passwordless universally; deprecate SMS OTP entirely.",
                        "SMS OTP as Primary: Retain SMS OTP across all workflows and seek regulatory exception for PCI-DSS 4.0 (High Risk)."
                    ],
                    "status": "Pending"
                })
                q_idx += 1

            elif "Deployment" in conf_type or "Cloud" in conflict["explanation"] or "Sovereignty" in conflict["explanation"]:
                questions.append({
                    "question_code": f"Q-{q_idx:03d}",
                    "conflict_code": conflict_code,
                    "title": "Hybrid Cloud Topology & Sovereign Data Residency Strategy",
                    "question": (
                        "How should the architecture resolve the conflict between the AWS Cloud scalability proposal "
                        "and the Tier-IV On-Premises Core Ledger mandate governed by Sovereign Banking Data Residency laws?"
                    ),
                    "context_reasoning": (
                        "Public cloud multi-region replication violates Central Bank sovereign data residency directives, "
                        "yet remaining exclusively on legacy on-prem infrastructure jeopardizes 100,000 concurrent user scaling."
                    ),
                    "related_req_codes": req_codes,
                    "suggested_options": [
                        "Sovereign Hybrid Architecture: Core ledger, HSM keys, and PII remain in Tier-IV Private DC; stateless edge gateways & caching run in domestic cloud AWS Local Zone.",
                        "Pure On-Premises Private Cloud: Deploy an on-premises OpenShift / Kubernetes bare-metal cluster with localized hardware expansion.",
                        "Full Cloud Migration with Sovereign Enclave: Host entirely on AWS within a single domestic sovereign region using AWS Nitro Enclaves and dedicated HSMs."
                    ],
                    "status": "Pending"
                })
                q_idx += 1

            elif "Performance" in conf_type or "Latency" in conflict["explanation"]:
                questions.append({
                    "question_code": f"Q-{q_idx:03d}",
                    "conflict_code": conflict_code,
                    "title": "Sub-2.0s Login P99 Latency under 100,000 Concurrent User Load",
                    "question": (
                        "What architectural pattern should be used to guarantee sub-2.0s login latency during peak 100,000 concurrent sessions "
                        "across hybrid network boundaries without overwhelming the database?"
                    ),
                    "context_reasoning": (
                        "Direct database queries for authentication at 8,500 TPS across hybrid network hops will introduce latency spikes above the 2.0s SLA."
                    ),
                    "related_req_codes": req_codes,
                    "suggested_options": [
                        "Stateless JWT with Edge Distributed Redis Cluster: Edge gateways validate signatures locally and cache non-sensitive session states.",
                        "Centralized Database Session Check: Force all login queries through the central on-prem database with connection pool tuning (Risk of thread starvation).",
                        "Async Event-Driven Auth Pipeline: Decouple audit logging and telemetry from the critical login response path using Apache Kafka / RabbitMQ."
                    ],
                    "status": "Pending"
                })
                q_idx += 1

        # Check for any ambiguous requirements without questions
        for req in requirements:
            if req.get("ambiguity_status") == "Ambiguous" and not any(req["req_code"] in q.get("related_req_codes", []) for q in questions):
                questions.append({
                    "question_code": f"Q-{q_idx:03d}",
                    "conflict_code": None,
                    "title": f"Specification Clarification for {req['title']}",
                    "question": f"Requirement '{req['title']}' is currently marked Ambiguous. What is the precise operational criteria for: {req['description']}?",
                    "context_reasoning": f"Need concrete SLA / protocol specification for {req['req_code']}.",
                    "related_req_codes": [req["req_code"]],
                    "suggested_options": [
                        "Option A: Prioritize standard enterprise SLA with automated fallback.",
                        "Option B: Enforce strict synchronous validation with 99.99% circuit breaker.",
                        "Option C: Defer to secondary release phase."
                    ],
                    "status": "Pending"
                })
                q_idx += 1

        return questions

    def apply_clarification(
        self,
        question_code: str,
        selected_option: Optional[str],
        custom_answer: Optional[str],
        conflicts: List[Dict[str, Any]],
        requirements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Re-evaluates conflicts and requirements when a human response is submitted.
        Updates status from 'Detected' to 'Resolved' or modifies requirement specifications.
        """
        answer_text = selected_option or custom_answer or "No answer provided"
        affected_conflicts = []
        affected_requirements = []

        # Find questions matching question_code
        for conf in conflicts:
            if question_code in conf.get("clarification_question", "") or conf.get("conflict_code") in question_code:
                conf["status"] = "Resolved"
                conf["resolution_notes"] = f"Resolved via human stakeholder clarification: '{answer_text}'"
                affected_conflicts.append(conf["conflict_code"])

        # Also search by keywords in the answer to resolve corresponding conflicts
        if "Adaptive" in answer_text or "Step-Up" in answer_text:
            for conf in conflicts:
                if any("CONF-001" in conf.get("conflict_code", "") or "Authentication" in conf.get("conflict_type", "") for c in [conf]):
                    conf["status"] = "Resolved"
                    conf["resolution_notes"] = f"Resolved via human approval: '{answer_text}'"
                    affected_conflicts.append(conf["conflict_code"])

        if "Sovereign Hybrid" in answer_text or "Hybrid Cloud" in answer_text:
            for conf in conflicts:
                if any("CONF-002" in conf.get("conflict_code", "") or "Deployment" in conf.get("conflict_type", "") for c in [conf]):
                    conf["status"] = "Resolved"
                    conf["resolution_notes"] = f"Resolved via human approval: '{answer_text}'"
                    affected_conflicts.append(conf["conflict_code"])

        if "Edge" in answer_text or "Redis" in answer_text or "Stateless" in answer_text:
            for conf in conflicts:
                if any("CONF-003" in conf.get("conflict_code", "") or "Performance" in conf.get("conflict_type", "") for c in [conf]):
                    conf["status"] = "Resolved"
                    conf["resolution_notes"] = f"Resolved via human approval: '{answer_text}'"
                    affected_conflicts.append(conf["conflict_code"])

        # Mark ambiguous requirements as Clarified
        for req in requirements:
            if req.get("ambiguity_status") == "Ambiguous":
                req["ambiguity_status"] = "Clear"
                req["approval_status"] = "Clarified"
                affected_requirements.append(req["req_code"])

        return {
            "question_code": question_code,
            "answer_applied": answer_text,
            "resolved_conflicts": list(set(affected_conflicts)),
            "clarified_requirements": list(set(affected_requirements))
        }

clarification_agent = ClarificationAgent()

