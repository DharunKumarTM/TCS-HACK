import logging
from typing import List, Dict, Any
from app.services.gemini_service import gemini_service

logger = logging.getLogger("archmind.agents.architecture")

SYSTEM_PROMPT = """You are the Principal Architecture Reasoning Agent of ArchMind AI.
Design an enterprise-grade software architecture tailored to validated requirements and real constraints.
Carefully evaluate architectural styles: Modular Monolith vs Microservices vs Event-Driven vs Sovereign Hybrid.
DO NOT recommend microservices blindly or by default. Justify choices through trade-offs.
Generate structured component breakdowns, APIs, data flows, and formal Architecture Decision Records (ADRs).
Ensure all components trace back to concrete requirement codes."""

class ArchitectureReasoningAgent:
    """Agent 5: Generates architectural decomposition, communication patterns, ADRs, and diagrams."""

    def design_architecture(
        self,
        requirements: List[Dict[str, Any]],
        conflicts: List[Dict[str, Any]],
        evidence_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesizes architecture design, components, APIs, data flows, ADRs, and Mermaid diagrams.
        """
        # Try Gemini structured architecture synthesis if live
        if gemini_service.is_live():
            req_summary = "\n".join([
                f"[{r['req_code']}] {r['title']} ({r['req_type']}, {r['priority']}): {r['description']}"
                for r in requirements
            ])
            prompt = f"""Based on the following approved banking requirements, produce a comprehensive enterprise architecture:
---
{req_summary}
---
Provide:
1. Architecture Style (e.g. "Sovereign Hybrid Architecture: Edge API Mesh with Resilient Core Domain")
2. Style Justification comparing Modular Monolith vs Microservices vs Hybrid
3. 6 to 8 Core Components with:
   - component_code (e.g. COMP-001)
   - name, layer, responsibility, technology_stack, deployment_target, scaling_strategy, security_controls, related_req_codes, dependencies
4. Key APIs (HTTP Method, path, summary, auth_requirement, related_req_codes)
5. Data Flows (flow_code, title, source, target, protocol, encryption, description)
6. 3 to 4 formal ADRs (adr_code, title, context, problem, decision, alternatives, advantages, disadvantages, trade_offs, supporting_req_codes, consequences)
"""
            result = gemini_service.generate_structured(prompt, SYSTEM_PROMPT)
            if result and isinstance(result, dict) and "components" in result and result.get("components"):
                # Inject mermaid diagrams
                result["mermaid_diagrams"] = self._generate_mermaid_diagrams(
                    result.get("components", []),
                    result.get("data_flows", [])
                )
                return result

        # Deterministic Architecture Reasoning
        return self._deterministic_architecture(requirements, conflicts, evidence_list)

    def _deterministic_architecture(
        self,
        requirements: List[Dict[str, Any]],
        conflicts: List[Dict[str, Any]],
        evidence_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generates an enterprise architecture tailored to the analyzed requirements.
        Uses specialized Sovereign Hybrid for SmartBank, or dynamic modular mesh for custom user inputs.
        """
        is_smartbank = any(
            "smartbank" in r.get("title", "").lower() or
            "sms otp" in r.get("title", "").lower() or
            "tier-iv" in r.get("title", "").lower() or
            "sovereign banking" in r.get("title", "").lower()
            for r in requirements
        )

        if not is_smartbank and requirements:
            return self._dynamic_custom_architecture(requirements, conflicts, evidence_list)

        architecture_style = "Sovereign Hybrid Architecture with Event-Driven Ledger Settlement"
        style_justification = (
            "A pure microservices architecture on public cloud is rejected due to Sovereign Banking Data Residency "
            "and on-premises mainframe ledger constraints. Conversely, a pure legacy monolith fails the 100,000 "
            "concurrent user elastic scalability target. Therefore, ArchMind AI prescribes a Sovereign Hybrid Architecture: "
            "stateless edge API gateways, risk-based authentication, and distributed Redis caching deploy on elastic "
            "domestic cloud containers, while the Core Ledger Domain, HSM key storage, and immutable audit logs "
            "remain isolated within the secure Tier-IV Private On-Premises Datacenter."
        )

        components = [
            {
                "component_code": "COMP-001",
                "name": "Edge Omni-Channel API Gateway",
                "layer": "API Gateway & Edge",
                "responsibility": "Reverse proxy, rate limiting, TLS 1.3 termination, distributed DDoS mitigation, and request routing.",
                "technology_stack": "Envoy Proxy / Kong Gateway on Domestic AWS Local Zone",
                "deployment_target": "Elastic Kubernetes (EKS) Multi-AZ",
                "scaling_strategy": "Horizontal Auto-scaling (HPA) up to 100,000 active sessions",
                "security_controls": ["mTLS", "WAF Ruleset", "DDoS Shield", "Strict Rate Limiting (1000 req/min)"],
                "related_req_codes": ["REQ-004", "REQ-005", "REQ-010"],
                "dependencies": ["COMP-002", "COMP-003", "COMP-004"],
                "status": "Proposed"
            },
            {
                "component_code": "COMP-002",
                "name": "Adaptive Identity & Step-Up Auth Service",
                "layer": "Security & Identity",
                "responsibility": "FIDO2/WebAuthn biometric verification, SMS/TOTP fallback issuance, risk-based step-up evaluation, and JWT signing.",
                "technology_stack": "FastAPI, PyCryptodome, Redis Session Store",
                "deployment_target": "Kubernetes Microservice",
                "scaling_strategy": "Auto-scaling based on CPU & connection metrics",
                "security_controls": ["RS256 JWT Signing", "WebAuthn Hardware Attestation", "Brute-force lockout", "Anti-SIM Swap verification"],
                "related_req_codes": ["REQ-001", "REQ-002", "REQ-003", "REQ-004"],
                "dependencies": ["COMP-003", "COMP-006"],
                "status": "Proposed"
            },
            {
                "component_code": "COMP-003",
                "name": "Distributed Edge Redis Session Cache",
                "layer": "Data Caching Layer",
                "responsibility": "Sub-millisecond session validation, read-heavy account caching, and distributed token blacklist to satisfy sub-2.0s login SLA.",
                "technology_stack": "Redis Cluster 7.2 with in-memory persistence and TLS",
                "deployment_target": "Multi-AZ Dedicated Cluster",
                "scaling_strategy": "Memory sharding with read replicas",
                "security_controls": ["Redis ACLs", "TLS In-Transit Encryption", "Zero PII long-term persistence"],
                "related_req_codes": ["REQ-004", "REQ-005"],
                "dependencies": [],
                "status": "Proposed"
            },
            {
                "component_code": "COMP-004",
                "name": "Transaction & Payment Orchestrator",
                "layer": "Core Business Domain",
                "responsibility": "P2P and merchant payment orchestration, balance verification, fraud screening dispatch, and idempotent processing.",
                "technology_stack": "Python FastAPI / Go, gRPC, Event-driven publisher",
                "deployment_target": "Private Cloud Tier-IV Datacenter",
                "scaling_strategy": "Clustered Active-Active nodes behind internal L4 load balancer",
                "security_controls": ["Idempotency Keys", "mTLS inter-service", "Transaction signing with HSM"],
                "related_req_codes": ["REQ-003", "REQ-005", "REQ-007", "REQ-010"],
                "dependencies": ["COMP-005", "COMP-006", "COMP-007"],
                "status": "Proposed"
            },
            {
                "component_code": "COMP-005",
                "name": "Core Banking Ledger & Settlement Engine",
                "layer": "Core Banking System",
                "responsibility": "ACID financial transaction ledger, double-entry bookkeeping, account balance management, and clearinghouse interface.",
                "technology_stack": "PostgreSQL with Patroni HA / CockroachDB Enterprise on Bare-Metal",
                "deployment_target": "Tier-IV Sovereign On-Premises Enclave",
                "scaling_strategy": "Vertical bare-metal clustering with synchronous multi-node hot standby (RPO=0)",
                "security_controls": ["AES-256 Tablespace Encryption", "Strict DB Auditing", "Air-gapped administrative network", "FIPS 140-3 HSM"],
                "related_req_codes": ["REQ-006", "REQ-007", "REQ-010"],
                "dependencies": ["COMP-006", "COMP-007"],
                "status": "Proposed"
            },
            {
                "component_code": "COMP-006",
                "name": "Hardware Security Module (HSM) Cryptographic Key Enclave",
                "layer": "Security & Cryptography",
                "responsibility": "FIPS 140-3 Level 3 certified key storage, PIN block encryption, and cryptographic transaction signature generation.",
                "technology_stack": "Thales Luna / Utimaco Dedicated Hardware Appliances",
                "deployment_target": "On-Premises Dedicated Server Rack",
                "scaling_strategy": "Dual Redundant Hardware Appliances in Failover configuration",
                "security_controls": ["Physical tamper detection", "Dual-custody key ceremony", "Zero key export"],
                "related_req_codes": ["REQ-003", "REQ-006", "REQ-007"],
                "dependencies": [],
                "status": "Proposed"
            },
            {
                "component_code": "COMP-007",
                "name": "Immutable Cryptographic Audit Service",
                "layer": "Compliance & Audit",
                "responsibility": "Append-only cryptographic hash chaining (Merkle tree), 7-year immutable log retention, and audit verification API.",
                "technology_stack": "WORM (Write Once Read Many) Storage + SHA-256 Hash Chain Ledger",
                "deployment_target": "On-Premises Sovereign Storage Array",
                "scaling_strategy": "Partitioned sequential storage by fiscal quarter",
                "security_controls": ["Cryptographic immutability", "WORM hardware enforcement", "SHA-256 chaining"],
                "related_req_codes": ["REQ-009"],
                "dependencies": [],
                "status": "Proposed"
            }
        ]

        apis = [
            {
                "component_code": "COMP-001",
                "method": "POST",
                "path": "/api/v2/auth/login",
                "summary": "Initiate authentication handshake (FIDO2 or SMS OTP challenge)",
                "auth_requirement": "Public with Rate Limit (10 req/min/IP)",
                "rate_limit": "600 req/min",
                "related_req_codes": ["REQ-001", "REQ-002", "REQ-004"]
            },
            {
                "component_code": "COMP-002",
                "method": "POST",
                "path": "/api/v2/auth/step-up",
                "summary": "Submit biometric or TOTP step-up proof for privileged actions",
                "auth_requirement": "Bearer Token + Session Nonce",
                "rate_limit": "120 req/min",
                "related_req_codes": ["REQ-002", "REQ-003"]
            },
            {
                "component_code": "COMP-004",
                "method": "POST",
                "path": "/api/v2/payments/transfer",
                "summary": "Execute P2P or merchant fund transfer with idempotency check",
                "auth_requirement": "Bearer JWT (with Step-Up Claim if > $250)",
                "rate_limit": "300 req/min",
                "related_req_codes": ["REQ-003", "REQ-005"]
            },
            {
                "component_code": "COMP-005",
                "method": "GET",
                "path": "/api/v2/accounts/balance",
                "summary": "Retrieve real-time account balances and ledger snapshot",
                "auth_requirement": "Bearer JWT",
                "rate_limit": "1200 req/min",
                "related_req_codes": ["REQ-004", "REQ-006"]
            },
            {
                "component_code": "COMP-007",
                "method": "GET",
                "path": "/api/v2/audit/verify/{transaction_id}",
                "summary": "Verify cryptographic Merkle hash proof of financial record",
                "auth_requirement": "Admin / Compliance Auditor Role",
                "rate_limit": "60 req/min",
                "related_req_codes": ["REQ-009"]
            }
        ]

        data_flows = [
            {
                "flow_code": "FLOW-001",
                "title": "Low-Latency Customer Login & Token Issuance",
                "source": "Client Application (Web/Mobile)",
                "target": "COMP-001 (Edge API Gateway)",
                "protocol": "HTTPS (TLS 1.3)",
                "payload_type": "JSON Auth Request",
                "encryption": "TLS 1.3 with Forward Secrecy",
                "step_sequence": 1,
                "description": "Client initiates login. Edge gateway validates rate limits and forwards to Adaptive Auth Service."
            },
            {
                "flow_code": "FLOW-002",
                "title": "Fast Token Verification & Caching",
                "source": "COMP-002 (Adaptive Auth Service)",
                "target": "COMP-003 (Redis Session Cache)",
                "protocol": "RESP3 over TLS",
                "payload_type": "Binary Cached Session",
                "encryption": "TLS in-transit",
                "step_sequence": 2,
                "description": "Session claims written to Redis cache in < 1ms to ensure sub-2.0s login response."
            },
            {
                "flow_code": "FLOW-003",
                "title": "Sovereign Payment Execution with Step-Up",
                "source": "COMP-001 (Edge API Gateway)",
                "target": "COMP-004 (Transaction Orchestrator)",
                "protocol": "gRPC over Dedicated Direct Connect",
                "payload_type": "Protobuf Transfer Command",
                "encryption": "mTLS with Certificate Pinning",
                "step_sequence": 3,
                "description": "Transfers > $250 verified for MFA claim, routed across secure private pipe to on-premises orchestrator."
            },
            {
                "flow_code": "FLOW-004",
                "title": "Double-Entry Ledger Mutation & HSM Signing",
                "source": "COMP-004 (Transaction Orchestrator)",
                "target": "COMP-005 (Core Banking Ledger)",
                "protocol": "PostgreSQL Wire Protocol over TLS",
                "payload_type": "ACID Transaction SQL",
                "encryption": "AES-256 Storage & TLS",
                "step_sequence": 4,
                "description": "Ledger executes double-entry debit/credit and invokes COMP-006 HSM for cryptographic signature."
            },
            {
                "flow_code": "FLOW-005",
                "title": "Cryptographic Audit Log Chaining",
                "source": "COMP-005 (Core Banking Ledger)",
                "target": "COMP-007 (Audit Service)",
                "protocol": "Asynchronous Message Queue / Kafka",
                "payload_type": "Audit Event Envelope",
                "encryption": "TLS 1.3",
                "step_sequence": 5,
                "description": "Ledger emits commit receipt. Audit service appends event to SHA-256 Merkle chain in WORM storage."
            }
        ]

        adrs = [
            {
                "adr_code": "ADR-001",
                "title": "Sovereign Hybrid Cloud Architecture over Pure Microservices",
                "status": "Proposed",
                "context": (
                    "SmartBank must scale to 100,000 concurrent active users while strictly complying with "
                    "National Data Sovereignty and enterprise policy POL-INFRA-09 requiring the core ledger to reside in the on-premises Tier-IV private datacenter."
                ),
                "problem": "Public cloud multi-region microservices violate data residency; pure on-premises bare-metal cannot elastically absorb 100k user spikes.",
                "decision": "Deploy an Edge/Core Hybrid Architecture: Stateless Edge API gateways & caching in domestic AWS Local Zones; Core Ledger, HSM, and Sovereign Database in on-premises Tier-IV datacenter.",
                "alternatives": [
                    {"option": "Pure AWS Multi-Region Microservices", "trade_off": "Fails compliance with Central Bank Data Sovereignty directives."},
                    {"option": "Pure On-Premises Monolith", "trade_off": "Cannot handle 100,000 concurrent user spikes elastically; high CapEx."}
                ],
                "advantages": [
                    "Strictly satisfies National Data Residency laws",
                    "Elastic edge absorbs 100,000 concurrent sessions",
                    "Protects core banking mainframe with private HSM enclave"
                ],
                "disadvantages": [
                    "Requires managing hybrid Direct Connect fiber link",
                    "Network latency overhead between edge gateway and on-prem ledger"
                ],
                "trade_offs": "Sacrifices cloud uniformity to achieve full sovereign compliance and enterprise data protection.",
                "supporting_req_codes": ["REQ-005", "REQ-006", "REQ-007", "REQ-008", "REQ-010"],
                "evidence_references": ["EV-005", "EV-006", "EV-007", "EV-008"],
                "assumptions": ["Enterprise has redundant 10Gbps AWS Direct Connect links to private datacenter."],
                "consequences": "All developers must structure services into stateless edge tier and stateful sovereign core domain.",
                "confidence": 0.96
            },
            {
                "adr_code": "ADR-002",
                "title": "Adaptive Step-Up Authentication Reconciling SMS OTP, FIDO2, and PCI-DSS 4.0",
                "status": "Proposed",
                "context": (
                    "Product CX requires frictionless passwordless login; Mobile Product Lead requires SMS OTP for 65% tier-2 users; "
                    "CISO & PCI-DSS 4.0 forbid SMS OTP for privileged money transfers."
                ),
                "problem": "Unifying three conflicting authentication paradigms into a single secure and compliant platform.",
                "decision": "Implement Adaptive Step-Up Authentication: Permit SMS OTP or passwordless biometric for baseline login/enquiries; mandate cryptographic FIDO2/WebAuthn or TOTP step-up for any transfer > $250.",
                "alternatives": [
                    {"option": "Universal SMS OTP", "trade_off": "Directly violates PCI-DSS 4.0; severe SIM-swap vulnerability."},
                    {"option": "Mandatory Universal FIDO2", "trade_off": "Excludes 65% of tier-2 customers lacking biometric hardware."}
                ],
                "advantages": [
                    "100% compliant with PCI-DSS 4.0 Section 1",
                    "Preserves onboarding funnel for regional tier-2 customers",
                    "Delivers modern passwordless experience on capable devices"
                ],
                "disadvantages": [
                    "Requires dynamic risk engine and secondary step-up challenge UX"
                ],
                "trade_offs": "Increases frontend workflow branching in exchange for maximum customer inclusion and regulatory compliance.",
                "supporting_req_codes": ["REQ-001", "REQ-002", "REQ-003", "REQ-004"],
                "evidence_references": ["EV-001", "EV-002", "EV-003"],
                "assumptions": ["Users transferring > $250 have smartphones capable of TOTP or WebAuthn biometrics."],
                "consequences": "Authentication tokens must carry risk-tier and verified authentication factor claims.",
                "confidence": 0.95
            },
            {
                "adr_code": "ADR-003",
                "title": "Distributed In-Memory Session Caching for Sub-2.0s P99 Latency SLA",
                "status": "Proposed",
                "context": (
                    "100,000 concurrent sessions generate up to 8,500 TPS. Querying the on-prem database for session validation "
                    "across the hybrid network link will breach the 2.0-second P99 login SLA."
                ),
                "problem": "Database connection pool exhaustion and hybrid network latency during peak morning login spikes.",
                "decision": "Use an in-memory Redis Cluster at the edge tier to cache stateless JWT claims and session metadata with 15-minute TTL.",
                "alternatives": [
                    {"option": "Synchronous Database Lookups", "trade_off": "Breaches 2.0s latency SLA; causes thread starvation at 8,500 TPS."},
                    {"option": "Client-Only Unvalidated JWT", "trade_off": "Cannot immediately revoke compromised sessions or enforce fraud locks."}
                ],
                "advantages": [
                    "Guarantees < 5ms session validation latency",
                    "Protects core database from 8,500 TPS session read storms",
                    "Enables instant session revocation via distributed blacklist"
                ],
                "disadvantages": [
                    "Introduces distributed cache synchronization complexity"
                ],
                "trade_offs": "Adds operational overhead of Redis Cluster to ensure strict P99 latency guarantees.",
                "supporting_req_codes": ["REQ-004", "REQ-005"],
                "evidence_references": ["EV-004", "EV-005"],
                "assumptions": ["Redis Cluster maintains 99.99% availability with multi-AZ replication."],
                "consequences": "Auth service must write session states to Redis with dual-write invalidation.",
                "confidence": 0.94
            },
            {
                "adr_code": "ADR-004",
                "title": "Append-Only Cryptographic Merkle Hash Chain for 7-Year Tamper-Evident Audit",
                "status": "Proposed",
                "context": (
                    "Infosec policy SEC-03 and banking regulations mandate immutable audit trails retained for 7 years "
                    "with zero capability for administrative alteration or deletion."
                ),
                "problem": "Standard relational database audit tables can be modified or truncated by database administrators.",
                "decision": "Deploy a dedicated Audit Microservice that links each transaction record into a SHA-256 sequential hash chain persisted on WORM-compliant storage.",
                "alternatives": [
                    {"option": "PostgreSQL Trigger Tables", "trade_off": "Vulnerable to superuser tampering or accidental truncation."},
                    {"option": "Public Blockchain Ledger", "trade_off": "High transaction gas fees, public disclosure of transaction metadata."}
                ],
                "advantages": [
                    "Mathematically provable tamper detection via cryptographic chaining",
                    "Satisfies 7-year regulatory retention mandate",
                    "Decoupled from transaction throughput via asynchronous queue"
                ],
                "disadvantages": [
                    "Requires specialized verification tooling for external auditors"
                ],
                "trade_offs": "Slight asynchronous logging lag in exchange for ironclad non-repudiation.",
                "supporting_req_codes": ["REQ-009"],
                "evidence_references": ["EV-009"],
                "assumptions": ["Storage hardware enforces WORM (Write Once Read Many) immutability."],
                "consequences": "Core ledger must asynchronously emit financial mutation events to the audit pipeline.",
                "confidence": 0.97
            }
        ]

        evolution = self._generate_architecture_evolution(requirements, is_smartbank=True)
        tech_stacks = self._generate_tech_stack_recommendations(requirements, is_smartbank=True)
        mermaid_diagrams = self._generate_mermaid_diagrams(components, data_flows)

        return {
            "architecture_style": architecture_style,
            "style_justification": style_justification,
            "components": components,
            "apis": apis,
            "data_flows": data_flows,
            "adrs": adrs,
            "mermaid_diagrams": mermaid_diagrams,
            "tech_stack_recommendations": tech_stacks,
            "old_architecture": evolution["old_architecture"],
            "new_architecture": evolution["new_architecture"],
            "comparison_matrix": evolution["comparison_matrix"],
            "confirmation_status": "Pending Review"
        }

    def _dynamic_custom_architecture(
        self,
        requirements: List[Dict[str, Any]],
        conflicts: List[Dict[str, Any]],
        evidence_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Dynamically synthesizes architecture tailored to ANY custom user uploaded file or pasted text requirements.
        """
        # Distribute requirements across architectural tiers
        all_codes = [r["req_code"] for r in requirements]
        sec_codes = [r["req_code"] for r in requirements if r.get("category") == "Security"]
        perf_codes = [r["req_code"] for r in requirements if r.get("category") in ["Performance", "Scalability"]]
        core_codes = [r["req_code"] for r in requirements if r.get("category") in ["Core", "Functional"]]
        comp_codes = [r["req_code"] for r in requirements if r.get("category") == "Compliance"]
        infra_codes = [r["req_code"] for r in requirements if r.get("category") == "Infrastructure"]

        architecture_style = "Cloud-Native Event-Driven Microservices with Distributed In-Memory Cache"
        style_justification = (
            "Based on the analyzed requirements, a decoupled event-driven microservices architecture "
            "is prescribed. Stateless edge API gateways and horizontal container auto-scaling absorb peak concurrent "
            "requests, while an asynchronous event broker decouples critical-path processing from persistence and audit logging."
        )

        components = [
            {
                "component_code": "COMP-001",
                "name": "Edge API Gateway & Ingress Router",
                "layer": "API Gateway & Edge",
                "responsibility": "TLS 1.3 termination, rate limiting, request validation, authentication token verification, and reverse proxying.",
                "technology_stack": "Envoy Proxy / Kong API Gateway on Kubernetes",
                "deployment_target": "Elastic Kubernetes (EKS / GKE) Multi-AZ",
                "scaling_strategy": "Horizontal Pod Autoscaler (HPA) based on request rate and latency",
                "security_controls": ["mTLS", "WAF Ruleset", "DDoS Shield", "Strict Rate Limiting"],
                "related_req_codes": perf_codes[:2] + infra_codes[:1] if (perf_codes or infra_codes) else all_codes[:2],
                "dependencies": ["COMP-002", "COMP-003", "COMP-004"],
                "status": "Proposed"
            },
            {
                "component_code": "COMP-002",
                "name": "Identity, Authentication & RBAC Service",
                "layer": "Security & Identity",
                "responsibility": "Multi-factor authentication, OAuth2/OIDC token issuance, role-based access control, and user session lifecycle.",
                "technology_stack": "FastAPI, PyJWT, Argon2, Redis Token Store",
                "deployment_target": "Kubernetes Microservice",
                "scaling_strategy": "Auto-scaling based on connection pool saturation",
                "security_controls": ["RS256 Asymmetric JWT", "Brute-force lockout", "Session rotation", "Audit trail"],
                "related_req_codes": sec_codes if sec_codes else all_codes[:2],
                "dependencies": ["COMP-003", "COMP-005"],
                "status": "Proposed"
            },
            {
                "component_code": "COMP-003",
                "name": "Distributed In-Memory Caching Tier",
                "layer": "Data Caching Layer",
                "responsibility": "Low-latency session caching, read-heavy data caching, and distributed rate limiting counters.",
                "technology_stack": "Redis Cluster 7.2 with in-memory persistence and TLS",
                "deployment_target": "Multi-AZ Dedicated Redis Cluster",
                "scaling_strategy": "Memory sharding with read replicas",
                "security_controls": ["TLS in-transit", "Redis ACLs", "Encrypted cache at rest"],
                "related_req_codes": perf_codes if perf_codes else all_codes[1:3],
                "dependencies": [],
                "status": "Proposed"
            },
            {
                "component_code": "COMP-004",
                "name": "Core Domain Business Orchestration Service",
                "layer": "Core Business Domain",
                "responsibility": "Execution of primary application business workflows, state machines, and business rule enforcement.",
                "technology_stack": "Python FastAPI / Go, gRPC, Pydantic",
                "deployment_target": "Clustered Application Containers",
                "scaling_strategy": "Horizontal container scaling behind internal load balancer",
                "security_controls": ["Input sanitization", "mTLS service-to-service", "Transaction idempotency"],
                "related_req_codes": core_codes if core_codes else all_codes,
                "dependencies": ["COMP-005", "COMP-006"],
                "status": "Proposed"
            },
            {
                "component_code": "COMP-005",
                "name": "Primary Database & Persistence Store",
                "layer": "Core Data Layer",
                "responsibility": "ACID relational persistence, transactional integrity, index optimization, and point-in-time recovery.",
                "technology_stack": "PostgreSQL 16 with HA clustering (Patroni / Aurora Serverless)",
                "deployment_target": "Managed Multi-AZ Database Enclave",
                "scaling_strategy": "Connection pooling (PgBouncer), read replicas, automated storage scaling",
                "security_controls": ["AES-256 Storage Encryption", "Strict Database Auditing", "Private VPC Subnets"],
                "related_req_codes": all_codes[:3] if all_codes else ["REQ-001"],
                "dependencies": ["COMP-007"],
                "status": "Proposed"
            },
            {
                "component_code": "COMP-006",
                "name": "Asynchronous Event Broker & Message Pipeline",
                "layer": "Event & Messaging Tier",
                "responsibility": "High-throughput event streaming, asynchronous task distribution, and decoupling critical path from audit.",
                "technology_stack": "Apache Kafka / RabbitMQ with multi-partition topics",
                "deployment_target": "Clustered Message Broker",
                "scaling_strategy": "Partition expansion with consumer group scaling",
                "security_controls": ["SASL/SCRAM authentication", "TLS 1.3 encryption"],
                "related_req_codes": perf_codes[1:] + comp_codes if (perf_codes or comp_codes) else all_codes[2:4],
                "dependencies": ["COMP-007"],
                "status": "Proposed"
            },
            {
                "component_code": "COMP-007",
                "name": "Audit Logging, Compliance & Telemetry Engine",
                "layer": "Compliance & Observability",
                "responsibility": "Centralized immutable audit trail, OpenTelemetry tracing, Prometheus metrics collection, and alerting.",
                "technology_stack": "OpenTelemetry, Prometheus, Grafana, Append-Only Storage",
                "deployment_target": "Monitoring & Logging Enclave",
                "scaling_strategy": "Log partition rotation and time-series retention policies",
                "security_controls": ["WORM storage", "Cryptographic log integrity", "Role-restricted access"],
                "related_req_codes": comp_codes if comp_codes else all_codes[-2:],
                "dependencies": [],
                "status": "Proposed"
            }
        ]

        apis = [
            {
                "component_code": "COMP-001",
                "method": "POST",
                "path": "/api/v1/auth/login",
                "summary": "Authenticate user credentials and issue signed JWT session token",
                "auth_requirement": "Public with Rate Limit",
                "rate_limit": "300 req/min",
                "related_req_codes": all_codes[:1]
            },
            {
                "component_code": "COMP-004",
                "method": "POST",
                "path": "/api/v1/domain/execute",
                "summary": "Execute core business transaction with idempotency verification",
                "auth_requirement": "Bearer JWT + Scoped Role",
                "rate_limit": "1000 req/min",
                "related_req_codes": core_codes[:1] if core_codes else all_codes[:1]
            },
            {
                "component_code": "COMP-004",
                "method": "GET",
                "path": "/api/v1/domain/status/{task_id}",
                "summary": "Query execution state and asynchronous worker status",
                "auth_requirement": "Bearer JWT",
                "rate_limit": "2000 req/min",
                "related_req_codes": all_codes[:2]
            },
            {
                "component_code": "COMP-007",
                "method": "GET",
                "path": "/api/v1/audit/logs",
                "summary": "Retrieve immutable regulatory and administrative audit events",
                "auth_requirement": "Admin / Security Officer Role",
                "rate_limit": "60 req/min",
                "related_req_codes": comp_codes[:1] if comp_codes else all_codes[-1:]
            }
        ]

        data_flows = [
            {
                "flow_code": "FLOW-001",
                "title": "Ingress Request Routing & Token Verification",
                "source": "Client Application (Web / Mobile)",
                "target": "COMP-001 (Edge API Gateway)",
                "protocol": "HTTPS (TLS 1.3)",
                "payload_type": "JSON API Request",
                "encryption": "TLS 1.3 with Perfect Forward Secrecy",
                "step_sequence": 1,
                "description": "Client initiates request. Edge Gateway validates rate limits and verifies JWT signature."
            },
            {
                "flow_code": "FLOW-002",
                "title": "Sub-Millisecond Cache Interception",
                "source": "COMP-001 (Edge API Gateway)",
                "target": "COMP-003 (Redis Cache Tier)",
                "protocol": "RESP3 over TLS",
                "payload_type": "Key-Value Binary Object",
                "encryption": "TLS in-transit",
                "step_sequence": 2,
                "description": "Edge gateway evaluates whether read request can be served from cache, protecting database."
            },
            {
                "flow_code": "FLOW-003",
                "title": "Domain Execution & State Transition",
                "source": "COMP-001 (Edge API Gateway)",
                "target": "COMP-004 (Core Domain Orchestrator)",
                "protocol": "gRPC over HTTP/2",
                "payload_type": "Protobuf Command",
                "encryption": "Mutual TLS (mTLS)",
                "step_sequence": 3,
                "description": "Write and mutate operations routed over internal mTLS service mesh to core domain orchestrator."
            },
            {
                "flow_code": "FLOW-004",
                "title": "ACID Data Commit",
                "source": "COMP-004 (Core Domain Orchestrator)",
                "target": "COMP-005 (Primary Database)",
                "protocol": "PostgreSQL Wire Protocol",
                "payload_type": "SQL Transaction",
                "encryption": "AES-256 Tablespace Encryption",
                "step_sequence": 4,
                "description": "Orchestrator commits state changes atomically with transactional consistency."
            },
            {
                "flow_code": "FLOW-005",
                "title": "Asynchronous Audit & Telemetry Emission",
                "source": "COMP-004 (Core Domain Orchestrator)",
                "target": "COMP-006 (Event Broker)",
                "protocol": "Kafka Binary Protocol",
                "payload_type": "Event Envelope",
                "encryption": "TLS 1.3",
                "step_sequence": 5,
                "description": "Post-commit receipt asynchronously broadcasted to Event Broker for compliance log append."
            }
        ]

        adrs = [
            {
                "adr_code": "ADR-001",
                "title": "Decoupled Event-Driven Microservices Architecture",
                "status": "Proposed",
                "context": "The platform requires elastic scalability, fault isolation, and independent deployability across functional domains.",
                "problem": "A monolithic architecture introduces deployment lockstep and limits selective horizontal scaling.",
                "decision": "Adopt a Cloud-Native Microservices pattern orchestrated via an API Gateway and asynchronous message broker.",
                "alternatives": [
                    {"option": "Monolithic Architecture", "trade_off": "Simpler initially, but creates scaling bottlenecks under high concurrent load."},
                    {"option": "Serverless Functions Only", "trade_off": "Susceptible to cold start latency and vendor lock-in."}
                ],
                "advantages": ["Independent scaling of read vs write tiers", "Resilience against cascade failures", "Technology flexibility per service"],
                "disadvantages": ["Requires distributed tracing and service mesh overhead"],
                "trade_offs": "Accepts distributed systems complexity to guarantee high availability and elastic throughput.",
                "supporting_req_codes": all_codes[:3],
                "evidence_references": ["EV-001", "EV-002"],
                "assumptions": ["Development team maintains container CI/CD automation."],
                "consequences": "All services must communicate via standardized gRPC or REST contracts with mutual TLS.",
                "confidence": 0.94
            },
            {
                "adr_code": "ADR-002",
                "title": "Stateless Asymmetric JWT Authentication with In-Memory Revocation",
                "status": "Proposed",
                "context": "Authentication must be verifiable in sub-millisecond latency across all microservices without bottlenecking the database.",
                "problem": "Stateful database session queries at high request rates saturate connection pools.",
                "decision": "Issue RS256 cryptographically signed JWT tokens with edge distributed Redis token blacklisting for revocation.",
                "alternatives": [
                    {"option": "Centralized Database Session Table", "trade_off": "Creates severe single-point database contention."},
                    {"option": "Unrevocable Client JWTs", "trade_off": "Security vulnerability if credentials are compromised."}
                ],
                "advantages": ["Sub-millisecond verification", "Instant revocation via Redis", "Cryptographically verifiable"],
                "disadvantages": ["Requires managing asymmetric private/public key rotation"],
                "trade_offs": "Minimal Redis memory overhead for high-speed authentication.",
                "supporting_req_codes": sec_codes if sec_codes else all_codes[:2],
                "evidence_references": ["EV-001"],
                "assumptions": ["Clients properly store tokens in secure HTTP-only cookies or device keystores."],
                "consequences": "API Gateway validates tokens before forwarding requests downstream.",
                "confidence": 0.95
            },
            {
                "adr_code": "ADR-003",
                "title": "Multi-Layered Caching Strategy for Latency SLA Enforcement",
                "status": "Proposed",
                "context": "Stringent response-time SLAs mandate that read-heavy requests bypass disk I/O.",
                "problem": "Repetitive database queries degrade performance during peak traffic bursts.",
                "decision": "Deploy a dedicated Multi-AZ Redis Cluster with write-through invalidation and allkeys-lru eviction.",
                "alternatives": [
                    {"option": "In-Process Memory Cache", "trade_off": "Causes memory fragmentation and cache inconsistency across pods."},
                    {"option": "Database Query Cache", "trade_off": "Invalidates frequently on table writes, limited scalability."}
                ],
                "advantages": ["Sub-5ms response times", "Protects primary database from read storms", "Shared across all pods"],
                "disadvantages": ["Cache invalidation logic must be rigorously maintained"],
                "trade_offs": "Adds distributed cache synchronization overhead for guaranteed latency.",
                "supporting_req_codes": perf_codes if perf_codes else all_codes[1:3],
                "evidence_references": ["EV-002"],
                "assumptions": ["Redis cluster maintains 99.99% availability."],
                "consequences": "Domain services must update cache on state changes.",
                "confidence": 0.93
            },
            {
                "adr_code": "ADR-004",
                "title": "Asynchronous Event Chaining for Non-Blocking Audit & Telemetry",
                "status": "Proposed",
                "context": "Compliance policies mandate comprehensive audit logging for administrative mutations without slowing down customer requests.",
                "problem": "Synchronous database audit writes add 30-80ms overhead to user response times.",
                "decision": "Emit audit events asynchronously to an Event Broker topic consumed by a dedicated Compliance Audit Worker.",
                "alternatives": [
                    {"option": "Synchronous Audit Writing", "trade_off": "Directly breaches p99 latency targets."},
                    {"option": "Batch Log Shipping", "trade_off": "Risk of data loss if a node crashes before logs ship."}
                ],
                "advantages": ["Zero latency penalty on critical customer path", "Guaranteed at-least-once delivery", "Decoupled audit store"],
                "disadvantages": ["Eventual consistency for audit query view (sub-second)"],
                "trade_offs": "Slight asynchronous logging lag in exchange for optimal request latency.",
                "supporting_req_codes": comp_codes if comp_codes else all_codes[-2:],
                "evidence_references": ["EV-003"],
                "assumptions": ["Kafka or message broker is provisioned with persistent storage."],
                "consequences": "Compliance audits read from the dedicated audit store rather than production database.",
                "confidence": 0.96
            }
        ]

        evolution = self._generate_architecture_evolution(requirements, is_smartbank=True)
        tech_stacks = self._generate_tech_stack_recommendations(requirements, is_smartbank=True)
        mermaid_diagrams = self._generate_mermaid_diagrams(components, data_flows)

        return {
            "architecture_style": architecture_style,
            "style_justification": style_justification,
            "components": components,
            "apis": apis,
            "data_flows": data_flows,
            "adrs": adrs,
            "mermaid_diagrams": mermaid_diagrams,
            "tech_stack_recommendations": tech_stacks,
            "old_architecture": evolution["old_architecture"],
            "new_architecture": evolution["new_architecture"],
            "comparison_matrix": evolution["comparison_matrix"],
            "confirmation_status": "Pending Review"
        }

    def _generate_tech_stack_recommendations(
        self,
        requirements: List[Dict[str, Any]],
        is_smartbank: bool = True
    ) -> List[Dict[str, Any]]:
        all_text = " ".join([r.get("title", "") + " " + r.get("description", "") for r in requirements]).lower()
        is_telehealth = any(w in all_text for w in ["patient", "doctor", "webrtc", "hipaa", "fhir", "telehealth", "consultation"])
        is_fleet = any(w in all_text for w in ["vehicle", "fleet", "telematics", "gps", "sensor", "fota", "iot"])
        is_ecommerce = any(w in all_text for w in ["ecommerce", "checkout", "cart", "flash sale", "order", "inventory"])

        all_req_codes = [r.get("req_code", f"REQ-{i+1:03d}") for i, r in enumerate(requirements)]

        if is_smartbank:
            return [
                {
                    "category": "API Gateway & Edge Ingress",
                    "selected": "Envoy Proxy / Kong Gateway on Domestic AWS Local Zone",
                    "reason_why": "Provides sub-millisecond TLS 1.3 termination, built-in OpenID Connect plugins, rate-limiting at 100,000 TPS, and supports mTLS zero-trust communication across edge cloud and on-premises enclaves.",
                    "requirements_supported": ["REQ-004", "REQ-005", "REQ-010"] if "REQ-004" in all_req_codes else all_req_codes[:2],
                    "alternatives": [
                        {
                            "name": "NGINX Plus",
                            "pros": ["High raw throughput", "Extremely low memory footprint per connection", "Mature ecosystem"],
                            "cons": ["Lacks native Kubernetes CRD dynamic discovery", "Configuration reloads cause slight latency spikes"],
                            "why_rejected": "Static configuration reloads cause latency jitter under rapid pod autoscaling spikes during morning login surges.",
                            "trade_offs": "Operational familiarity vs Cloud-Native elasticity."
                        },
                        {
                            "name": "AWS API Gateway (Managed Serverless)",
                            "pros": ["Zero infrastructure management", "Automatic AWS IAM integration"],
                            "cons": ["High cost at sustained 100k TPS", "Significant latency penalty bridging to on-premises datacenters"],
                            "why_rejected": "Violates Sovereign Banking Data Residency directives by routing private on-premises ledger traffic through public multi-tenant AWS endpoints.",
                            "trade_offs": "Serverless ease vs Data residency compliance and sustained cost."
                        },
                        {
                            "name": "Traefik Enterprise",
                            "pros": ["Automatic Let's Encrypt SSL", "Clean microservice dashboard"],
                            "cons": ["Lacks enterprise banking plugin ecosystem", "Limited HSM client certificate forwarding"],
                            "why_rejected": "Does not support native mTLS client certificate header attestation for Tier-IV banking hardware enclaves.",
                            "trade_offs": "Developer ergonomics vs Enterprise security hardening."
                        }
                    ],
                    "is_overridden": False,
                    "overridden_by": None
                },
                {
                    "category": "Backend Runtime & Microservices Framework",
                    "selected": "FastAPI (Python 3.12) & Go (Golang 1.22) Microservices",
                    "reason_why": "FastAPI delivers native async I/O, Pydantic type validation for financial contracts, and seamless AI agent/fraud model integration; Go provides compiled microsecond concurrency for high-TPS transaction pipes.",
                    "requirements_supported": ["REQ-003", "REQ-005"] if "REQ-003" in all_req_codes else all_req_codes[:2],
                    "alternatives": [
                        {
                            "name": "Spring Boot 3 (Java 21)",
                            "pros": ["Traditional enterprise banking standard", "Enormous talent pool", "Mature Spring Cloud ecosystem"],
                            "cons": ["Heavy memory footprint (500MB+ per pod)", "JVM warmup latency slows rapid container autoscaling"],
                            "why_rejected": "Slow JVM warmup times undermine Horizontal Pod Autoscaler agility during sudden 8,500 TPS login spikes.",
                            "trade_offs": "Legacy comfort vs Fast container cold-starts and memory efficiency."
                        },
                        {
                            "name": "Node.js (NestJS)",
                            "pros": ["Non-blocking event loop", "Shared TypeScript models across frontend and backend"],
                            "cons": ["Single-threaded event loop blocks on CPU-intensive cryptographic hashing and token signing"],
                            "why_rejected": "Intense cryptographic token signing (RS256) causes event-loop starvation without complex worker threads.",
                            "trade_offs": "Fullstack code sharing vs CPU-bound cryptographic throughput."
                        },
                        {
                            "name": "ASP.NET Core (C# .NET 8)",
                            "pros": ["Outstanding raw benchmark throughput", "Robust enterprise tooling"],
                            "cons": ["Weaker machine learning and AI agent library ecosystem compared to Python"],
                            "why_rejected": "Hinders seamless embedded integration with Python AI agents and vector retrieval libraries.",
                            "trade_offs": "Raw throughput vs Agentic AI & data science interoperability."
                        }
                    ],
                    "is_overridden": False,
                    "overridden_by": None
                },
                {
                    "category": "Primary Database & Persistence Tier",
                    "selected": "PostgreSQL 16 Enterprise with pgvector & Active-Active Multi-AZ Sharding",
                    "reason_why": "Provides strict ACID financial transaction guarantees, Row-Level Security (RLS), JSONB indexing for flexible banking schemas, Foreign Data Wrappers (FDW) for legacy ledger sync, and vector embeddings for fraud similarity search.",
                    "requirements_supported": ["REQ-006", "REQ-007"] if "REQ-006" in all_req_codes else all_req_codes[:2],
                    "alternatives": [
                        {
                            "name": "Oracle 19c Enterprise Database",
                            "pros": ["Traditional core banking benchmark", "RAC clustering reliability"],
                            "cons": ["Exorbitant licensing costs ($47,500/core)", "Proprietary vendor lock-in", "Difficult cloud-native Kubernetes automation"],
                            "why_rejected": "Adds multimillion-dollar licensing overhead without providing modern vector embeddings or open-source agility.",
                            "trade_offs": "Legacy banking comfort vs Open-source TCO and vector intelligence."
                        },
                        {
                            "name": "MongoDB Enterprise (Document DB)",
                            "pros": ["Dynamic schema flexibility", "Built-in sharding across clusters"],
                            "cons": ["Multi-document ACID transactions have high lock overhead and latency under write contention"],
                            "why_rejected": "Double-entry banking ledgers require strict mathematical ACID relational integrity, which relational PostgreSQL handles natively with far lower latency.",
                            "trade_offs": "Document agility vs Strict relational ledger guarantees."
                        },
                        {
                            "name": "CockroachDB (Distributed SQL)",
                            "pros": ["Global distributed transactions", "Multi-region Raft consensus"],
                            "cons": ["Higher write latency for single-region clusters due to Raft consensus roundtrips"],
                            "why_rejected": "Consensus roundtrips add 25-40ms to write latency, directly violating the sub-200ms transaction settlement SLA.",
                            "trade_offs": "Multi-region consensus vs Single-datacenter microsecond write latency."
                        }
                    ],
                    "is_overridden": False,
                    "overridden_by": None
                },
                {
                    "category": "Distributed In-Memory Caching Tier",
                    "selected": "Redis Cluster 7.2 with In-Memory Persistence & TLS",
                    "reason_why": "Guarantees sub-millisecond read/write latency, distributed atomic rate-limiting counters, sliding-window session management, and shields the core database, satisfying the sub-2.0s login SLA for 100,000 concurrent users.",
                    "requirements_supported": ["REQ-004", "REQ-005"] if "REQ-004" in all_req_codes else all_req_codes[:2],
                    "alternatives": [
                        {
                            "name": "Memcached",
                            "pros": ["Multithreaded simple key-value memory store", "Low CPU overhead"],
                            "cons": ["No disk persistence", "No native clustering failover", "Lacks rich data structures (hashes, sorted sets)"],
                            "why_rejected": "Cannot support atomic sliding-window rate limiters, token blacklists, or publish/subscribe notifications.",
                            "trade_offs": "Raw simplicity vs Rich data structure capabilities."
                        },
                        {
                            "name": "Hazelcast In-Memory Data Grid",
                            "pros": ["Distributed Java compute", "Clustered in-memory data processing"],
                            "cons": ["Heavy JVM memory requirements", "Complex cluster topology tuning"],
                            "why_rejected": "Unnecessary architectural complexity and memory footprint compared to cloud-native Redis.",
                            "trade_offs": "Distributed compute vs Lightweight operational simplicity."
                        }
                    ],
                    "is_overridden": False,
                    "overridden_by": None
                },
                {
                    "category": "Event Streaming & Asynchronous Bus",
                    "selected": "Apache Kafka (KRaft mode) with Confluent Schema Registry",
                    "reason_why": "Delivers high-throughput event streaming (>1,000,000 events/sec), durable partitioned commit log for financial event sourcing, regulatory audit replayability, and strict message ordering per account ID.",
                    "requirements_supported": ["REQ-007", "REQ-009"] if "REQ-007" in all_req_codes else all_req_codes[-2:],
                    "alternatives": [
                        {
                            "name": "RabbitMQ",
                            "pros": ["Flexible AMQP routing keys", "Lightweight management web UI", "Low latency under light loads"],
                            "cons": ["Throughput degrades sharply under massive message backlogs", "Lacks distributed log replay for historical audits"],
                            "why_rejected": "Regulatory banking audits require permanent immutable event log replay, which RabbitMQ queues do not natively provide.",
                            "trade_offs": "Flexible routing vs Permanent immutable event sourcing."
                        },
                        {
                            "name": "AWS SQS / SNS (Managed Cloud Messaging)",
                            "pros": ["Serverless zero-ops", "Elastic cloud scaling"],
                            "cons": ["Cloud lock-in", "Cannot bridge to private on-prem Tier-IV datacenter without hybrid WAN bottlenecks"],
                            "why_rejected": "Violates sovereign banking data residency requirements by routing sensitive financial mutations through public cloud queues.",
                            "trade_offs": "Zero ops vs Sovereign private datacenter compatibility."
                        }
                    ],
                    "is_overridden": False,
                    "overridden_by": None
                },
                {
                    "category": "Security, Identity & Hardware Cryptography",
                    "selected": "Thales Luna HSM (Hardware Security Module) + Keycloak OIDC + WebAuthn FIDO2",
                    "reason_why": "FIPS 140-2 Level 3 physical tamper-resistant hardware root of trust for financial keys; biometric FIDO2 prevents phishing and credential theft; adaptive step-up authentication satisfies PCI-DSS 4.0 for transfers > $250.",
                    "requirements_supported": ["REQ-001", "REQ-002", "REQ-008"] if "REQ-001" in all_req_codes else all_req_codes[:2],
                    "alternatives": [
                        {
                            "name": "AWS KMS (Cloud Key Management)",
                            "pros": ["Seamless cloud integration", "Managed key rotation"],
                            "cons": ["Private keys hosted in public cloud multi-tenant infrastructure"],
                            "why_rejected": "Central Bank directives explicitly mandate physical on-premises HSM enclaves for sovereign ledger root keys.",
                            "trade_offs": "Cloud convenience vs Sovereign regulatory compliance."
                        },
                        {
                            "name": "HashiCorp Vault (Software Cryptography)",
                            "pros": ["Unified secrets management API", "Dynamic secrets"],
                            "cons": ["Software-only key storage lacks FIPS 140-2 Level 3 physical tamper-evidence"],
                            "why_rejected": "Does not achieve physical hardware tamper-resistance required for Tier-IV banking certification.",
                            "trade_offs": "Software flexibility vs Hardware cryptographic assurance."
                        }
                    ],
                    "is_overridden": False,
                    "overridden_by": None
                },
                {
                    "category": "Observability, Telemetry & Tracing",
                    "selected": "OpenTelemetry SDK + Prometheus + Grafana + OpenSearch (WORM Audit)",
                    "reason_why": "Vendor-neutral distributed tracing across hybrid cloud and on-prem nodes, correlating HTTP trace IDs with asynchronous Kafka event chains; append-only WORM audit storage meets regulatory 7-year retention.",
                    "requirements_supported": ["REQ-009", "REQ-010"] if "REQ-009" in all_req_codes else all_req_codes[-2:],
                    "alternatives": [
                        {
                            "name": "Datadog / Dynatrace (SaaS APM)",
                            "pros": ["Turnkey dashboards", "AI-driven anomaly detection"],
                            "cons": ["Sending customer banking telemetry to external multi-tenant SaaS violates privacy directives"],
                            "why_rejected": "Sovereign banking policy prohibits third-party APM log exfiltration to external clouds.",
                            "trade_offs": "Pre-built dashboards vs Data sovereignty and privacy."
                        },
                        {
                            "name": "ELK Stack (Elasticsearch / Logstash / Kibana)",
                            "pros": ["Ubiquitous log indexing standard", "Large community"],
                            "cons": ["Restrictive SSPL licensing and heavy JVM memory usage"],
                            "why_rejected": "OpenSearch is 100% open source under Apache 2.0 without licensing restrictions and has better Kubernetes native support.",
                            "trade_offs": "Legacy familiarity vs True open-source compliance."
                        }
                    ],
                    "is_overridden": False,
                    "overridden_by": None
                },
                {
                    "category": "Container Orchestration & Cloud Infrastructure",
                    "selected": "Kubernetes (EKS in Domestic AWS Local Zone + On-Premises VMware Tanzu / OpenShift)",
                    "reason_why": "Enables declarative hybrid infrastructure: stateless edge services scale horizontally on domestic AWS Local Zones, while core stateful workloads run securely in on-premises OpenShift clusters.",
                    "requirements_supported": ["REQ-005", "REQ-006"] if "REQ-005" in all_req_codes else all_req_codes[:2],
                    "alternatives": [
                        {
                            "name": "Docker Swarm",
                            "pros": ["Simple setup", "Minimal control plane overhead"],
                            "cons": ["Lacks advanced traffic routing, horizontal pod autoscaling, and enterprise service mesh"],
                            "why_rejected": "Cannot orchestrate complex multi-zone autoscaling or zero-trust mTLS service meshes at enterprise scale.",
                            "trade_offs": "Simplicity vs Enterprise scalability and mesh capabilities."
                        },
                        {
                            "name": "AWS ECS (Elastic Container Service)",
                            "pros": ["Deep AWS integration", "Simpler than Kubernetes"],
                            "cons": ["AWS proprietary control plane", "Cannot run on-premises in Tier-IV datacenter"],
                            "why_rejected": "Vendor lock-in prevents unified hybrid orchestration across cloud and on-premises datacenters.",
                            "trade_offs": "AWS ease vs Hybrid datacenter portability."
                        }
                    ],
                    "is_overridden": False,
                    "overridden_by": None
                }
            ]
        else:
            db_selected = "TimescaleDB / PostgreSQL 16" if is_fleet else ("PostgreSQL 16 with JSONB (FHIR Schema)" if is_telehealth else "PostgreSQL 16 with Read Replicas")
            msg_selected = "MQTT Broker (EMQX) + Apache Kafka" if is_fleet else ("WebRTC Signaling Mesh + Redis PubSub" if is_telehealth else "Apache Kafka with KRaft Mode")
            sec_selected = "Mutual TLS (mTLS) + PKI Hardware Device Certificates" if is_fleet else ("HIPAA Encrypted Store + OAuth2 / SMART on FHIR + AES-256" if is_telehealth else "PCI-DSS 4.0 Tokenization Vault + OAuth2 / OIDC")

            return [
                {
                    "category": "API Gateway & Ingress Router",
                    "selected": "Kong API Gateway / Envoy Proxy on Kubernetes",
                    "reason_why": "Provides non-blocking reverse proxying, distributed rate limiting, and mTLS security terminating connections at the perimeter with sub-millisecond overhead.",
                    "requirements_supported": all_req_codes[:2],
                    "alternatives": [
                        {
                            "name": "NGINX Open Source",
                            "pros": ["Fast", "Battle-tested"],
                            "cons": ["Requires reload on configuration changes", "Lacks Kubernetes CRD native automation"],
                            "why_rejected": "Lacks dynamic API route registration and real-time JWT verification plugins.",
                            "trade_offs": "Simplicity vs Dynamic cloud-native adaptability."
                        },
                        {
                            "name": "Cloudflare API Shield",
                            "pros": ["Global edge CDN", "Automated DDoS scrubbing"],
                            "cons": ["SaaS third-party dependency", "Latency penalty on private VPC connections"],
                            "why_rejected": "Does not allow on-premises or private VPC edge deployment.",
                            "trade_offs": "Managed CDN vs Private cluster control."
                        }
                    ],
                    "is_overridden": False,
                    "overridden_by": None
                },
                {
                    "category": "Backend Runtime & Microservices Framework",
                    "selected": "Python FastAPI 0.110+ & Go Microservices",
                    "reason_why": "FastAPI guarantees high-speed asynchronous request handling with automatic schema validation (Pydantic), while Go handles compute-heavy microservices with sub-millisecond execution.",
                    "requirements_supported": all_req_codes[:2],
                    "alternatives": [
                        {
                            "name": "Node.js (Express / Fastify)",
                            "pros": ["Fast JavaScript I/O", "Huge npm ecosystem"],
                            "cons": ["Single-threaded CPU limits", "Weaker data science and AI pipeline libraries"],
                            "why_rejected": "Cannot natively host embedded Python ML or agentic verification libraries.",
                            "trade_offs": "Frontend parity vs Python AI and Go concurrency performance."
                        },
                        {
                            "name": "Java Spring Boot",
                            "pros": ["Enterprise maturity", "Robust dependency injection"],
                            "cons": ["Higher RAM footprint", "Slower container startup"],
                            "why_rejected": "Higher container resource cost and slower horizontal autoscaling response.",
                            "trade_offs": "Enterprise legacy vs Container cold-start speed."
                        }
                    ],
                    "is_overridden": False,
                    "overridden_by": None
                },
                {
                    "category": "Primary Persistence & Database Store",
                    "selected": db_selected,
                    "reason_why": "Ensures strict relational consistency, schema flexibility via JSONB, high-throughput indexing, and enterprise compliance guarantees.",
                    "requirements_supported": all_req_codes[1:3] if len(all_req_codes) > 2 else all_req_codes[:1],
                    "alternatives": [
                        {
                            "name": "MongoDB Enterprise",
                            "pros": ["NoSQL document model", "Easy horizontal sharding"],
                            "cons": ["Higher memory usage", "Weaker relational constraints and join performance"],
                            "why_rejected": "Relational constraints and transactional consistency are critical for core data integrity.",
                            "trade_offs": "Schemaless flexibility vs Relational data consistency."
                        },
                        {
                            "name": "MySQL 8.0",
                            "pros": ["Popular", "Read-heavy optimization"],
                            "cons": ["Inferior JSON querying and lacks native vector indexing support"],
                            "why_rejected": "PostgreSQL provides superior JSONB performance, native extensions, and vector support.",
                            "trade_offs": "Simple read replication vs Advanced indexing and vector extension support."
                        }
                    ],
                    "is_overridden": False,
                    "overridden_by": None
                },
                {
                    "category": "Distributed Caching Tier",
                    "selected": "Redis Cluster 7.2 (Multi-AZ with TLS)",
                    "reason_why": "Delivers sub-2ms response times for session states, token revocation lists, and hot entity caching, keeping p99 response times well within strict SLA targets.",
                    "requirements_supported": all_req_codes[:2],
                    "alternatives": [
                        {
                            "name": "Memcached",
                            "pros": ["Fast multi-threaded key-value"],
                            "cons": ["No persistence", "No clustering failover", "No complex data structures"],
                            "why_rejected": "Cannot support atomic sliding-window rate limiters or token blacklists.",
                            "trade_offs": "Raw memory speed vs Data structures and high availability."
                        }
                    ],
                    "is_overridden": False,
                    "overridden_by": None
                },
                {
                    "category": "Event Streaming & Asynchronous Bus",
                    "selected": msg_selected,
                    "reason_why": "Decouples the synchronous user request path from background processing, audit recording, and analytics, preventing cascading timeouts.",
                    "requirements_supported": all_req_codes[-2:] if len(all_req_codes) > 2 else all_req_codes[:1],
                    "alternatives": [
                        {
                            "name": "RabbitMQ",
                            "pros": ["Lightweight", "Flexible AMQP routing"],
                            "cons": ["Throughput drops under massive backlogs", "No permanent event replay log"],
                            "why_rejected": "Event sourcing and replayability are mandatory for compliance auditing and telemetry reconstruction.",
                            "trade_offs": "Routing simplicity vs Scalable event replay."
                        }
                    ],
                    "is_overridden": False,
                    "overridden_by": None
                },
                {
                    "category": "Security, Identity & Privacy Controls",
                    "selected": sec_selected,
                    "reason_why": "Enforces zero-trust defense-in-depth: encrypted data at rest (AES-256), encrypted transit (TLS 1.3), fine-grained RBAC, and strict regulatory compliance.",
                    "requirements_supported": [r for r in all_req_codes if "sec" in r.lower()] or all_req_codes[:2],
                    "alternatives": [
                        {
                            "name": "Basic Session Cookies / API Keys",
                            "pros": ["Simple to implement"],
                            "cons": ["Vulnerable to CSRF, replay attacks, and credential theft"],
                            "why_rejected": "Completely unacceptable for enterprise data privacy and security mandates.",
                            "trade_offs": "Trivial implementation vs Critical vulnerability risk."
                        }
                    ],
                    "is_overridden": False,
                    "overridden_by": None
                },
                {
                    "category": "Observability & Tracing Engine",
                    "selected": "OpenTelemetry + Prometheus + Grafana",
                    "reason_why": "Provides vendor-neutral end-to-end distributed tracing across microservices, custom SLA latency monitors, and proactive error rate alerting.",
                    "requirements_supported": all_req_codes[-1:],
                    "alternatives": [
                        {
                            "name": "Proprietary SaaS (Datadog / New Relic)",
                            "pros": ["Hosted cloud dashboards"],
                            "cons": ["Expensive data egress", "Privacy concerns with sensitive customer telemetry"],
                            "why_rejected": "Open-source OpenTelemetry stack guarantees data privacy and prevents vendor cost escalation.",
                            "trade_offs": "Hosted SaaS vs Open-source privacy and cost control."
                        }
                    ],
                    "is_overridden": False,
                    "overridden_by": None
                }
            ]

    def _generate_architecture_evolution(
        self,
        requirements: List[Dict[str, Any]],
        is_smartbank: bool = True
    ) -> Dict[str, Any]:
        all_text = " ".join([r.get("title", "") + " " + r.get("description", "") for r in requirements]).lower()
        is_telehealth = any(w in all_text for w in ["patient", "doctor", "webrtc", "hipaa", "fhir", "telehealth", "consultation"])
        is_fleet = any(w in all_text for w in ["vehicle", "fleet", "telematics", "gps", "sensor", "fota", "iot"])
        is_ecommerce = any(w in all_text for w in ["ecommerce", "checkout", "cart", "flash sale", "order", "inventory"])

        if is_smartbank:
            old_name = "SmartBank 1.0 Legacy Monolith"
            old_style = "Monolithic Core with Direct Database Coupling & Synchronous Network Bottlenecks"
            old_desc = (
                "The legacy architecture packages mobile banking, web banking, payment authorization, and ledger mutations "
                "into a single monolithic process running on physical servers. All requests connect directly to a centralized "
                "relational database. During morning login storms, database row-locks cause cascading HTTP timeouts, and sessions "
                "stored in sticky local RAM are lost whenever a monolithic node crashes."
            )
            new_name = "SmartBank 2.0 Sovereign Hybrid Architecture"
            new_style = "Sovereign Hybrid Cloud-Edge Mesh with Event-Driven Ledger Settlement"
            new_desc = (
                "The prescribed target architecture decouples public-facing ingress from core financial operations. "
                "Stateless edge API Gateways and distributed Redis clusters deploy in elastic domestic cloud zones to absorb "
                "100,000 concurrent user sessions and enforce sub-2.0s login SLAs. Core ledger mutations and cryptographic keys "
                "are securely isolated within an on-premises Tier-IV datacenter enclave backed by physical Hardware Security Modules (HSM)."
            )
            old_mermaid = """flowchart TD
    Clients["Mobile & Web Banking Clients"] -->|Public Internet| LB["Legacy Hardware Load Balancer"]
    LB -->|Unencrypted HTTP| Mono1["Legacy Monolith Node 1\n(Auth, Ledger, Transfers, Reports)"]
    LB -->|Unencrypted HTTP| Mono2["Legacy Monolith Node 2\n(Auth, Ledger, Transfers, Reports)"]
    Mono1 -->|Direct Synchronous SQL\nHigh Lock Contention| DB[("Centralized Monolithic Database\n(Single Point of Failure)")]
    Mono2 -->|Direct Synchronous SQL\nHigh Lock Contention| DB
    Mono1 -.->|Sticky Local RAM| Session1["Local RAM Sessions\n(Lost on Node Crash)"]
    Mono2 -.->|Sticky Local RAM| Session2["Local RAM Sessions\n(Lost on Node Crash)"]
    DB -.->|Nightly Batch Cron| Batch["Nightly Batch Reporting Script"]
"""
            new_mermaid = """flowchart TD
    Clients["Omni-Channel Clients\n(Web & Mobile Apps)"] -->|TLS 1.3 / mTLS| EdgeGW["COMP-001: Edge API Gateway\n(Envoy / Kong on Kubernetes)"]
    EdgeGW -->|Sub-2ms Cache Hit| RedisCache[("COMP-003: Redis Cluster 7.2\n(Distributed Session Cache)")]
    EdgeGW -->|mTLS Auth| AuthSvc["COMP-002: Adaptive Auth Service\n(WebAuthn FIDO2 / Biometrics)"]
    AuthSvc -.->|Hardware Key Signing| HSM["Hardware Security Module (HSM)\n(FIPS 140-2 Level 3 Enclave)"]
    EdgeGW -->|mTLS| CoreOrch["COMP-004: Transaction Orchestrator\n(FastAPI / Go Microservices)"]
    CoreOrch -->|Async Event Streaming| KafkaBus["COMP-007: Apache Kafka Event Bus\n(KRaft Mode, Replayable Log)"]
    KafkaBus -->|Consumer Pipeline| AuditSvc["COMP-008: Immutable Audit Worker\n(WORM Regulatory Storage)"]
    CoreOrch -->|ACID Ledger Transactions| CoreDB[("COMP-005: PostgreSQL 16 Cluster\n(Active-Active Multi-AZ)")]
"""
            matrix = [
                {"dimension": "Architecture Paradigm", "legacy": "Monolithic Shared Database", "target": "Sovereign Hybrid Event-Driven Mesh", "delta": "+300% Modularity & Decoupling", "impact": "High"},
                {"dimension": "P99 Response Latency", "legacy": "2,400 ms (Peak morning surge)", "target": "< 180 ms (SLA guaranteed)", "delta": "13.3x Latency Reduction", "impact": "Critical"},
                {"dimension": "Peak Concurrency & Throughput", "legacy": "1,200 TPS (Connection pool saturated)", "target": "100,000+ TPS (Elastic HPA)", "delta": "83.3x Throughput Scaling", "impact": "Critical"},
                {"dimension": "System Availability SLA", "legacy": "99.5% (~44 hrs annual downtime)", "target": "99.99% (< 52 mins annual downtime)", "delta": "98% Reduction in Downtime", "impact": "High"},
                {"dimension": "Disaster Recovery (RPO / RTO)", "legacy": "RPO: 4 Hours | RTO: 2 Hours", "target": "RPO: 0 (Zero Loss) | RTO: < 15 sec", "delta": "Instant Zero-Data-Loss Failover", "impact": "Critical"},
                {"dimension": "Security & Cryptography", "legacy": "Perimeter firewall; cleartext internal RPC", "target": "Zero-Trust mTLS + Hardware HSM FIPS 140-2 L3", "delta": "PCI-DSS 4.0 & Hardware Root of Trust", "impact": "Critical"},
                {"dimension": "Deployment & Release Cycle", "legacy": "Fortnightly maintenance downtime", "target": "Continuous zero-downtime canary rollouts", "delta": "Daily zero-downtime releases", "impact": "Medium"},
                {"dimension": "Data Sovereignty & Compliance", "legacy": "Unsegmented on-prem silos", "target": "Tier-IV isolated sovereign data residency", "delta": "100% Central Bank Compliance", "impact": "High"}
            ]
        else:
            dom_name = "Telemedicine Platform" if is_telehealth else ("Fleet Telematics Mesh" if is_fleet else ("E-Commerce Flash Engine" if is_ecommerce else "Custom Software Platform"))
            old_name = f"{dom_name} Legacy Baseline (v1.x)"
            old_style = "Centralized Three-Tier Monolith with Direct DB Coupling"
            old_desc = (
                f"The legacy {dom_name} operates as a centralized three-tier monolith. Synchronous inter-component "
                "calls create cascading latency bottlenecks during traffic spikes. The single database instance suffers "
                "from heavy write contention, and lack of distributed caching causes performance degradation under sustained load."
            )
            new_name = f"{dom_name} Cloud-Native Target (v2.0)"
            new_style = "Decoupled Event-Driven Microservices with Distributed In-Memory Cache"
            new_desc = (
                f"The proposed target architecture transforms the {dom_name} into an elastic, event-driven microservices system. "
                "Stateless Edge Gateways and Redis caching absorb ingress traffic surges, while Kafka event pipelines decouple "
                "time-critical operations from downstream audit, notification, and analytics tasks."
            )
            old_mermaid = """flowchart TD
    Clients["Client Applications / IoT Devices"] -->|Public Internet| LB["Single Load Balancer"]
    LB -->|Synchronous HTTP| Monolith["Legacy Central Monolith\n(Business Logic + Data + Reporting)"]
    Monolith -->|Direct Synchronous SQL| DB[("Single Monolithic Database\n(Lock Contention Bottleneck)")]
    Monolith -.->|Local In-Memory| Cache["Local RAM Cache\n(Lost on Node Crash)"]
"""
            new_mermaid = """flowchart TD
    Clients["Client Applications / Devices"] -->|TLS 1.3 / mTLS| EdgeGW["COMP-001: Edge API Gateway\n(Rate Limiting & Ingress Routing)"]
    EdgeGW -->|Sub-2ms Read| Redis[("COMP-003: Distributed Redis Cache\n(Session & Hot Data Caching)")]
    EdgeGW -->|mTLS Auth| Auth["COMP-002: Identity & Access Service\n(OAuth2 / OIDC + Token Vault)"]
    EdgeGW -->|mTLS| Core["COMP-004: Domain Orchestrator\n(FastAPI / Go Microservices)"]
    Core -->|Async Event Streaming| Kafka["COMP-007: Event Streaming Bus\n(Kafka Event Sourcing)"]
    Core -->|ACID Persistence| DB[("COMP-005: Clustered Database\n(Partitioned with Read Replicas)")]
    Kafka -->|Background Worker| Audit["COMP-008: Compliance Audit & Telemetry\n(Asynchronous Consumer)"]
"""
            matrix = [
                {"dimension": "Architecture Pattern", "legacy": "Three-Tier Monolith", "target": "Cloud-Native Event-Driven Microservices", "delta": "+250% Decoupling & Modularity", "impact": "High"},
                {"dimension": "P99 Response Latency", "legacy": "1,800 ms (Peak surge)", "target": "< 150 ms (Sub-second guaranteed)", "delta": "12x Latency Reduction", "impact": "Critical"},
                {"dimension": "Peak Throughput & Concurrency", "legacy": "800 TPS (Database bottleneck)", "target": "50,000+ TPS (Horizontal Auto-scaling)", "delta": "62.5x Scaling Capacity", "impact": "Critical"},
                {"dimension": "System Availability SLA", "legacy": "99.0% (~87 hrs annual downtime)", "target": "99.99% (< 52 mins annual downtime)", "delta": "99% Availability Improvement", "impact": "High"},
                {"dimension": "Data Loss & Disaster Recovery", "legacy": "Daily backup, RTO: 6 hrs", "target": "Active-Active replication, RTO < 30 sec", "delta": "Zero Data Loss (RPO=0)", "impact": "Critical"},
                {"dimension": "Security & Compliance", "legacy": "Basic perimeter firewall, static credentials", "target": "Zero-Trust mTLS, encrypted at rest & transit", "delta": "End-to-End Encryption & RBAC", "impact": "Critical"},
                {"dimension": "Deployment Cadence", "legacy": "Monthly scheduled downtime", "target": "Continuous rolling zero-downtime deploys", "delta": "Zero-Downtime Deployment", "impact": "Medium"}
            ]

        return {
            "old_architecture": {
                "name": old_name,
                "style": old_style,
                "description": old_desc,
                "characteristics": [
                    "Single monolithic codebase with tight compile-time coupling",
                    "Shared centralized database creating global lock contention",
                    "Synchronous blocking calls causing cascading timeouts",
                    "In-memory sticky sessions with no cross-node failover",
                    "Perimeter-only firewall security with unencrypted internal traffic",
                    "Manual vertical scaling requiring scheduled maintenance windows"
                ],
                "metrics": {
                    "latency_p99": "2,400 ms (Peak load)" if is_smartbank else "1,800 ms (Peak load)",
                    "throughput_tps": "1,200 TPS" if is_smartbank else "800 TPS",
                    "availability": "99.5%" if is_smartbank else "99.0%",
                    "rpo_rto": "RPO: 4 Hours | RTO: 2 Hours",
                    "security_posture": "Perimeter firewall only; cleartext internal traffic; static shared credentials",
                    "scalability_ceiling": "Hard vertical limit on single server instance"
                },
                "mermaid_diagram": old_mermaid
            },
            "new_architecture": {
                "name": new_name,
                "style": new_style,
                "description": new_desc,
                "characteristics": [
                    "Decoupled microservices with domain-driven bounded contexts",
                    "Distributed multi-AZ Redis cache intercepting reads to meet latency SLAs",
                    "Asynchronous Kafka event sourcing eliminating cascading latency",
                    "Zero-Trust mTLS encryption across all internal and cross-zone communications",
                    "Hardware cryptographic security root of trust",
                    "Horizontal Pod Autoscaler (HPA) elastically handling peak traffic bursts"
                ],
                "metrics": {
                    "latency_p99": "< 180 ms (P99 under 100k active sessions)" if is_smartbank else "< 150 ms (SLA guaranteed)",
                    "throughput_tps": "100,000+ TPS (Elastic HPA)" if is_smartbank else "50,000+ TPS (Auto-scaling)",
                    "availability": "99.99% (< 52 minutes downtime/year)",
                    "rpo_rto": "RPO: 0 (Zero Loss) | RTO: < 15 seconds",
                    "security_posture": "Zero-Trust mTLS, FIPS 140-2 L3 HSM, PCI-DSS / HIPAA compliant",
                    "scalability_ceiling": "Horizontal elastic auto-scaling across multi-AZ Kubernetes pods"
                },
                "mermaid_diagram": new_mermaid
            },
            "comparison_matrix": matrix
        }

    def _generate_mermaid_diagrams(self, components: List[Dict[str, Any]], data_flows: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Generates 5 Mermaid.js diagrams: High-level, Component, Data-Flow, Deployment, and Sequence.
        """
        # 1. High-Level Architecture Diagram
        high_level = """graph TD
    subgraph ClientLayer["Omni-Channel Client Tier"]
        Web["Web Banking SPA (FIDO2)"]
        Mobile["Mobile App (iOS / Android)"]
    end

    subgraph EdgeCloud["Domestic Elastic Cloud (Edge Zone)"]
        Gateway["COMP-001: Edge API Gateway (Envoy)"]
        AuthSvc["COMP-002: Adaptive Auth Service"]
        Cache["COMP-003: Redis Session Cache (p99 < 2s)"]
    end

    subgraph PrivateDC["Tier-IV Sovereign Private Datacenter (On-Premises)"]
        TxnOrch["COMP-004: Transaction Orchestrator"]
        Ledger["COMP-005: Core Banking Ledger (ACID / RPO=0)"]
        HSM["COMP-006: Hardware Security Module (FIPS 140-3)"]
        Audit["COMP-007: Cryptographic Audit Service (7-Yr WORM)"]
    end

    Web -->|HTTPS TLS 1.3| Gateway
    Mobile -->|HTTPS TLS 1.3| Gateway
    Gateway --> AuthSvc
    AuthSvc --> Cache
    Gateway -->|Dedicated Direct Connect mTLS| TxnOrch
    TxnOrch --> Ledger
    Ledger --> HSM
    Ledger -.->|Async Event| Audit
"""

        # 2. Component Diagram
        component_diag = """graph LR
    subgraph EdgeMesh["Edge Gateway & Identity"]
        C1["COMP-001: API Gateway"]
        C2["COMP-002: Adaptive Auth"]
        C3["COMP-003: Redis Cache"]
    end

    subgraph CoreEnclave["Core Sovereign Banking Enclave"]
        C4["COMP-004: Txn Orchestrator"]
        C5["COMP-005: Core Ledger"]
        C6["COMP-006: Dedicated HSM"]
        C7["COMP-007: Audit Service"]
    end

    C1 --> C2
    C2 --> C3
    C1 --> C4
    C4 --> C5
    C5 --> C6
    C5 --> C7
"""

        # 3. Data-Flow Diagram
        data_flow_diag = """flowchart TD
    A["1. User Request (Login / Transfer)"] --> B["COMP-001: TLS Termination & Rate Check"]
    B --> C{"Is Auth / Session Read?"}
    C -->|Yes| D["COMP-003: Query Redis Cache (< 2ms)"]
    D --> E["Return Instant Response (< 2.0s SLA)"]
    C -->|No / Transfer > $250| F["COMP-002: Evaluate Step-Up MFA Claim"]
    F --> G["COMP-004: Dispatch to Sovereign Ledger via mTLS"]
    G --> H["COMP-005: Double-Entry ACID Settlement"]
    H --> I["COMP-006: Hardware Cryptographic Signature"]
    H --> J["COMP-007: Append SHA-256 Merkle Audit Log"]
"""

        # 4. Deployment Architecture Diagram
        deployment_diag = """graph TB
    subgraph Internet["Public Internet"]
        ClientApps["Retail & Commercial Users"]
    end

    subgraph AWS_Domestic["Domestic Cloud Region (In-Country)"]
        NLB["AWS Network Load Balancer"]
        subgraph EKS_Cluster["Elastic Kubernetes Cluster"]
            Pods_Gateway["Envoy API Gateway Pods (Auto-scaling 100k)"]
            Pods_Auth["Adaptive Auth Pods"]
        end
        RedisCluster["Managed Multi-AZ Redis Cluster"]
    end

    subgraph DirectConnect["Dedicated 10Gbps Direct Connect (Encrypted IPsec)"]
        FiberPipe["Fiber Pipe with Hardware Redundancy"]
    end

    subgraph TierIV_OnPrem["Tier-IV Sovereign On-Premises Datacenter"]
        InternalLB["High-Availability Internal Load Balancer"]
        subgraph SovereignEnclave["Sovereign Mainframe Enclave"]
            TxnNodes["Txn Orchestrator Clustered Nodes"]
            PostgresHA["Patroni Clustered PostgreSQL (Synchronous Standby)"]
            HSM_Rack["Thales Luna Hardware Security Modules"]
            WORM_SAN["Immutable WORM Storage SAN"]
        end
    end

    ClientApps --> NLB
    NLB --> Pods_Gateway
    Pods_Gateway --> Pods_Auth
    Pods_Auth --> RedisCluster
    Pods_Gateway --> FiberPipe
    FiberPipe --> InternalLB
    InternalLB --> TxnNodes
    TxnNodes --> PostgresHA
    PostgresHA --> HSM_Rack
    PostgresHA --> WORM_SAN
"""

        # 5. Sequence Diagram for High-Value Payment
        sequence_diag = """sequenceDiagram
    autonumber
    actor User as Banking Customer
    participant App as Mobile Banking App
    participant Edge as COMP-001 Edge Gateway
    participant Auth as COMP-002 Adaptive Auth
    participant Txn as COMP-004 Txn Orchestrator
    participant Core as COMP-005 Core Ledger
    participant HSM as COMP-006 HSM Enclave
    participant Audit as COMP-007 Audit Service

    User->>App: Request $500 Fund Transfer
    App->>Edge: POST /api/v2/payments/transfer
    Edge->>Auth: Validate Token & Check Step-Up
    Note over Auth: Transfer exceeds $250 threshold!<br/>Step-Up MFA Required (PCI-DSS 4.0)
    Auth-->>App: Challenge: Request FIDO2 / Biometric Step-Up
    User->>App: Provides Biometric Touch / Hardware Token
    App->>Auth: Submit WebAuthn Attestation
    Auth-->>Edge: Token Upgraded with MFA Claim
    Edge->>Txn: Dispatch Payment (mTLS over Direct Connect)
    Txn->>Core: Execute Atomic Double-Entry Transfer
    Core->>HSM: Sign Transaction Payload with Master Key
    HSM-->>Core: Cryptographic Signature Verified
    Core-->>Txn: Transaction Committed (RPO=0)
    Txn-->>Edge: Settlement Confirmed
    Edge-->>App: Transfer Successful Receipt
    Core-)Audit: Async Emit Chained Hash Event (7-Yr WORM)
"""

        return {
            "high_level": high_level,
            "component": component_diag,
            "data_flow": data_flow_diag,
            "deployment": deployment_diag,
            "sequence": sequence_diag
        }

architecture_agent = ArchitectureReasoningAgent()

