import re
import logging
from typing import List, Dict, Any
from app.services.gemini_service import gemini_service

logger = logging.getLogger("archmind.agents.requirements")

SYSTEM_PROMPT = """You are the Requirements Engineering Agent of ArchMind AI.
Transform unstructured evidence and stakeholder statements into normalized software requirements.
Classify each item as:
- Functional (FR)
- Non-Functional (NFR)
- Technical Constraint (TC)
- Business Constraint (BC)
Detect ambiguity status: "Clear", "Ambiguous", or "Incomplete".
Preserve provenance by citing source evidence codes.
Never silently promote an unverified assumption or preference to a confirmed Fact without evidence."""

class RequirementsEngineeringAgent:
    """Agent 2: Generates structured, classified, normalized software requirements from evidence."""

    def analyze_requirements(self, evidence_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        requirements = []
        req_counter = 1

        # Try Gemini structured extraction first if live
        if gemini_service.is_live():
            evidence_summary = "\n".join([
                f"[{ev['evidence_code']}] ({ev['source_filename']}) {ev['statement']}"
                for ev in evidence_list[:25]
            ])
            prompt = f"""From the following extracted evidence statements, synthesize a comprehensive set of normalized software requirements:
---
{evidence_summary}
---
For each requirement, return:
- title: concise title
- description: formal IEEE-style specification statement ("The system shall...")
- req_type: "Functional", "Non-Functional", "Technical Constraint", or "Business Constraint"
- category: "Security", "Performance", "Scalability", "Compliance", "Infrastructure", or "Core"
- priority: "Critical", "High", "Medium", or "Low"
- source_evidence_codes: array of string codes (e.g. ["EV-001", "EV-003"])
- confidence: float (0.85 - 0.99)
- verification_method: "Automated Test", "Inspection", "Performance Benchmark", or "Security Audit"
- ambiguity_status: "Clear", "Ambiguous", or "Incomplete"
- approval_status: "Fact" (if backed by PRD/policy), "Inferred" (if derived), or "Assumption" (if unverified)
- rationale: brief explanation of why this requirement is formulated
"""
            result = gemini_service.generate_structured(prompt, SYSTEM_PROMPT)
            if result and isinstance(result, list):
                for item in result:
                    requirements.append({
                        "req_code": f"REQ-{req_counter:03d}",
                        "title": item.get("title", f"Requirement {req_counter}"),
                        "description": item.get("description", ""),
                        "req_type": item.get("req_type", "Functional"),
                        "category": item.get("category", "Core"),
                        "priority": item.get("priority", "Medium"),
                        "source_evidence_codes": item.get("source_evidence_codes", []),
                        "confidence": float(item.get("confidence", 0.92)),
                        "verification_method": item.get("verification_method", "Automated Test"),
                        "ambiguity_status": item.get("ambiguity_status", "Clear"),
                        "approval_status": item.get("approval_status", "Fact"),
                        "rationale": item.get("rationale", "Derived from project evidence.")
                    })
                    req_counter += 1

        if not requirements:
            requirements = self._deterministic_requirements(evidence_list)

        return requirements

    def _deterministic_requirements(self, evidence_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deterministic requirements generator mapping evidence items to standardized requirements.
        Supports both SmartBank reference cases and arbitrary user-uploaded documents/text.
        """
        requirements = []
        req_counter = 1

        for ev in evidence_list:
            stmt = ev["statement"].lower()
            code = ev["evidence_code"]
            matched = False

            # SmartBank Rule 1: SMS OTP Authentication
            if ("sms otp" in stmt or "sms-based otp" in stmt) and not matched:
                requirements.append({
                    "req_code": f"REQ-{req_counter:03d}",
                    "title": "SMS OTP Retail Authentication",
                    "description": "The digital banking system shall provide SMS-based One-Time Password (OTP) verification for retail customer login and onboarding.",
                    "req_type": "Functional",
                    "category": "Security",
                    "priority": "High",
                    "source_evidence_codes": [code],
                    "confidence": 0.95,
                    "verification_method": "Automated End-to-End Test",
                    "ambiguity_status": "Ambiguous",
                    "approval_status": "Inferred",
                    "rationale": "Requested by Mobile Product Lead for tier-2/tier-3 reach, but conflicts with security policies."
                })
                req_counter += 1
                matched = True

            # SmartBank Rule 2: Biometric & Passwordless Login
            elif ("passwordless" in stmt or "fido2" in stmt or "webauthn" in stmt) and not matched:
                requirements.append({
                    "req_code": f"REQ-{req_counter:03d}",
                    "title": "FIDO2 / WebAuthn Biometric Passwordless Login",
                    "description": "The client applications shall support FIDO2/WebAuthn compliant passwordless biometric authentication across iOS, Android, and modern web browsers.",
                    "req_type": "Functional",
                    "category": "Security",
                    "priority": "High",
                    "source_evidence_codes": [code],
                    "confidence": 0.96,
                    "verification_method": "Security Compliance Audit",
                    "ambiguity_status": "Clear",
                    "approval_status": "Inferred",
                    "rationale": "Demanded by CX Head to eliminate password friction and credential phishing."
                })
                req_counter += 1
                matched = True

            # SmartBank Rule 3: PCI-DSS MFA Policy
            elif ("pci-dss" in stmt or ("mfa" in stmt and "fund transfer" in stmt) or "$250" in stmt) and not matched:
                requirements.append({
                    "req_code": f"REQ-{req_counter:03d}",
                    "title": "PCI-DSS 4.0 Transaction MFA Enforcement",
                    "description": "The transaction orchestration service shall mandate cryptographic, phishing-resistant Multi-Factor Authentication (MFA) for all funds transfers exceeding $250.",
                    "req_type": "Business Constraint",
                    "category": "Compliance",
                    "priority": "Critical",
                    "source_evidence_codes": [code],
                    "confidence": 0.99,
                    "verification_method": "Automated Compliance Test",
                    "ambiguity_status": "Clear",
                    "approval_status": "Fact",
                    "rationale": "Mandated by CISO and PCI-DSS 4.0 regulatory standards."
                })
                req_counter += 1
                matched = True

            # SmartBank Rule 4: Authentication Latency (< 2.0s)
            elif ("2.0 second" in stmt or "2.0s" in stmt or "sub-2.0" in stmt) and not matched:
                requirements.append({
                    "req_code": f"REQ-{req_counter:03d}",
                    "title": "Sub-2.0s P99 Authentication Latency",
                    "description": "The end-to-end authentication and token issuance handshake must complete within 2.0 seconds at the 99th percentile under peak concurrent user load.",
                    "req_type": "Non-Functional",
                    "category": "Performance",
                    "priority": "Critical",
                    "source_evidence_codes": [code],
                    "confidence": 0.98,
                    "verification_method": "Performance Load Benchmark",
                    "ambiguity_status": "Clear",
                    "approval_status": "Fact",
                    "rationale": "Defined in Product PRD to prevent login abandonment."
                })
                req_counter += 1
                matched = True

            # SmartBank Rule 5: Concurrency (100,000 Concurrent Users)
            elif ("100,000" in stmt or "8,500 tps" in stmt) and not matched:
                requirements.append({
                    "req_code": f"REQ-{req_counter:03d}",
                    "title": "100,000 Peak Concurrent Sessions & 8,500 TPS",
                    "description": "The core banking backend services and database connection tier must sustain 100,000 active concurrent sessions and 8,500 transactions per second.",
                    "req_type": "Non-Functional",
                    "category": "Scalability",
                    "priority": "Critical",
                    "source_evidence_codes": [code],
                    "confidence": 0.97,
                    "verification_method": "Stress & Spike Load Test",
                    "ambiguity_status": "Clear",
                    "approval_status": "Fact",
                    "rationale": "Engineering capacity target for promotional and seasonal peaks."
                })
                req_counter += 1
                matched = True

            # SmartBank Rule 6: Sovereign Data Residency
            elif ("sovereign" in stmt or "data residency" in stmt or "national borders" in stmt or "pii" in stmt) and not matched:
                requirements.append({
                    "req_code": f"REQ-{req_counter:03d}",
                    "title": "Sovereign Banking Data Residency",
                    "description": "All customer PII, ledger records, account balances, and encryption keys must reside strictly within domestic national boundaries; cross-border data transfer is prohibited.",
                    "req_type": "Technical Constraint",
                    "category": "Compliance",
                    "priority": "Critical",
                    "source_evidence_codes": [code],
                    "confidence": 0.99,
                    "verification_method": "Inspection & Architecture Review",
                    "ambiguity_status": "Clear",
                    "approval_status": "Fact",
                    "rationale": "Mandatory compliance with Central Bank Data Protection directive."
                })
                req_counter += 1
                matched = True

            # SmartBank Rule 7: On-Premises Tier-IV Core Ledger
            elif ("on-prem" in stmt or "tier-iv" in stmt or "mainframe" in stmt or "pol-infra-09" in stmt) and not matched:
                requirements.append({
                    "req_code": f"REQ-{req_counter:03d}",
                    "title": "Tier-IV On-Premises Core Ledger Deployment",
                    "description": "The primary financial ledger database and transaction clearing engine shall be hosted within the enterprise Tier-IV on-premises private datacenter.",
                    "req_type": "Technical Constraint",
                    "category": "Infrastructure",
                    "priority": "Critical",
                    "source_evidence_codes": [code],
                    "confidence": 0.95,
                    "verification_method": "Deployment Validation",
                    "ambiguity_status": "Clear",
                    "approval_status": "Fact",
                    "rationale": "Infrastructure policy POL-INFRA-09 for mainframe ledger connectivity."
                })
                req_counter += 1
                matched = True

            # SmartBank Rule 8: AWS Cloud-Native Deployment Proposal
            elif ("aws" in stmt or "eks" in stmt or "serverless" in stmt) and not matched:
                requirements.append({
                    "req_code": f"REQ-{req_counter:03d}",
                    "title": "AWS Elastic Container Cloud Architecture",
                    "description": "The banking platform services shall be containerized and orchestrated on AWS Managed Kubernetes (EKS) with serverless elasticity to optimize scaling costs.",
                    "req_type": "Technical Constraint",
                    "category": "Infrastructure",
                    "priority": "High",
                    "source_evidence_codes": [code],
                    "confidence": 0.90,
                    "verification_method": "Deployment Validation",
                    "ambiguity_status": "Ambiguous",
                    "approval_status": "Assumption",
                    "rationale": "Cloud Architect proposal to solve 100k scaling, but conflicts with on-prem mandate."
                })
                req_counter += 1
                matched = True

            # SmartBank Rule 9: Tamper-Evident Financial Audit Trail
            elif ("audit" in stmt or "merkle" in stmt or "tamper-evident" in stmt or "7 years" in stmt) and not matched:
                requirements.append({
                    "req_code": f"REQ-{req_counter:03d}",
                    "title": "7-Year Immutable Cryptographic Audit Trail",
                    "description": "The platform shall log 100% of financial transactions and administrative mutations into an append-only, tamper-evident cryptographic hash chain retained for 7 years.",
                    "req_type": "Non-Functional",
                    "category": "Compliance",
                    "priority": "Critical",
                    "source_evidence_codes": [code],
                    "confidence": 0.98,
                    "verification_method": "Cryptographic Integrity Check",
                    "ambiguity_status": "Clear",
                    "approval_status": "Fact",
                    "rationale": "Regulatory Infosec policy SEC-03 compliance."
                })
                req_counter += 1
                matched = True

            # SmartBank Rule 10: 99.99% Availability & RPO=0
            elif ("99.99%" in stmt or "rto" in stmt or "rpo = 0" in stmt) and not matched:
                requirements.append({
                    "req_code": f"REQ-{req_counter:03d}",
                    "title": "High Availability (99.99%) & Zero Data Loss (RPO=0)",
                    "description": "The system shall maintain 99.99% annualized uptime with active-active clustering, failover RTO under 5 minutes, and strict RPO=0 for financial state.",
                    "req_type": "Non-Functional",
                    "category": "Reliability",
                    "priority": "Critical",
                    "source_evidence_codes": [code],
                    "confidence": 0.98,
                    "verification_method": "Disaster Recovery Simulation",
                    "ambiguity_status": "Clear",
                    "approval_status": "Fact",
                    "rationale": "SLA defined in PRD Section 4 and Infosec Policy SEC-04."
                })
                req_counter += 1
                matched = True

            # Universal Fallback for ANY custom user input (Healthcare, E-Commerce, IoT, etc.)
            if not matched and len(ev["statement"]) > 15:
                stmt_clean = ev["statement"].replace("\n", " ").strip()
                req_type = "Functional"
                cat = "Core"
                prio = "Medium"

                if any(w in stmt for w in ["latency", "speed", "sla", "throughput", "tps", "response time", "ms", "p99", "sub-"]):
                    req_type = "Non-Functional"
                    cat = "Performance"
                    prio = "Critical" if "ms" in stmt or "latency" in stmt else "High"
                elif any(w in stmt for w in ["concurrent", "scale", "volume", "users", "capacity", "load", "surge", "elastic"]):
                    req_type = "Non-Functional"
                    cat = "Scalability"
                    prio = "Critical" if any(num in stmt for num in ["000", "million", "k"]) else "High"
                elif any(w in stmt for w in ["encrypt", "auth", "token", "jwt", "mtls", "hipaa", "pci", "gdpr", "permission", "security", "protect", "pii", "hsm"]):
                    req_type = "Technical Constraint" if "encrypt" in stmt or "mtls" in stmt else "Functional"
                    cat = "Security"
                    prio = "Critical"
                elif any(w in stmt for w in ["cloud", "aws", "azure", "gcp", "docker", "k8s", "kubernetes", "on-prem", "host", "datacenter", "serverless"]):
                    req_type = "Technical Constraint"
                    cat = "Infrastructure"
                    prio = "High"
                elif any(w in stmt for w in ["comply", "policy", "audit", "retention", "regulation", "law", "sovereign", "standard"]):
                    req_type = "Business Constraint"
                    cat = "Compliance"
                    prio = "Critical"
                elif any(w in stmt for w in ["avail", "uptime", "rto", "rpo", "disaster", "failover", "recovery"]):
                    req_type = "Non-Functional"
                    cat = "Reliability"
                    prio = "Critical"

                # Generate clean normalized title
                title = re.sub(r'^(the system shall|the platform must|the application will|must|shall|provide|support|enable)\s+', '', stmt_clean, flags=re.IGNORECASE)
                words = title.split()
                title_clean = " ".join(words[:6]).strip().title()
                if not title_clean or len(title_clean) < 5:
                    title_clean = f"System Requirement {req_counter}"

                norm_desc = stmt_clean
                if not norm_desc.lower().startswith("the "):
                    norm_desc = f"The system shall {norm_desc[0].lower()}{norm_desc[1:]}"

                requirements.append({
                    "req_code": f"REQ-{req_counter:03d}",
                    "title": title_clean,
                    "description": norm_desc,
                    "req_type": req_type,
                    "category": cat,
                    "priority": prio,
                    "source_evidence_codes": [code],
                    "confidence": 0.94,
                    "verification_method": "Automated Test" if req_type == "Functional" else "Performance Benchmark & Inspection",
                    "ambiguity_status": "Clear",
                    "approval_status": "Fact" if ev.get("quality_grade") == "High" else "Inferred",
                    "rationale": f"Derived from {ev.get('source_filename', 'user input')} ({ev.get('category', 'General')})"
                })
                req_counter += 1

        # Deduplicate requirements by title
        unique_reqs = []
        seen_titles = set()
        for r in requirements:
            if r["title"] not in seen_titles:
                seen_titles.add(r["title"])
                unique_reqs.append(r)

        return unique_reqs

requirements_agent = RequirementsEngineeringAgent()
