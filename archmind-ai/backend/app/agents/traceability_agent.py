import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("archmind.agents.traceability")

class TraceabilityAgent:
    """Agent 8: Computes bidirectional traceability matrix and simulates change impacts."""

    def build_traceability_matrix(
        self,
        requirements: List[Dict[str, Any]],
        components: List[Dict[str, Any]],
        apis: List[Dict[str, Any]],
        adrs: List[Dict[str, Any]],
        conflicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Builds rigorous evidence-to-architecture traceability without fabricating 100% coverage.
        """
        traceability_items = []
        fully_covered = 0
        partially_covered = 0
        not_covered = 0
        blocked = 0

        # Check unresolved conflicts that block requirements
        unresolved_conflicts = [c for c in conflicts if c.get("status") != "Resolved"]
        blocked_req_codes = set()
        for conf in unresolved_conflicts:
            for code in conf.get("conflicting_req_codes", []):
                blocked_req_codes.add(code)

        for req in requirements:
            req_code = req["req_code"]
            evidence_codes = req.get("source_evidence_codes", [])

            # Find mapped components
            mapped_components = [
                c["component_code"] for c in components
                if req_code in c.get("related_req_codes", [])
            ]

            # Find related APIs
            related_apis = [
                f"{a['method']} {a['path']}" for a in apis
                if req_code in a.get("related_req_codes", [])
            ]

            # Find related ADRs
            related_adrs = [
                a["adr_code"] for a in adrs
                if req_code in a.get("supporting_req_codes", [])
            ]

            # Determine Coverage Status
            if req_code in blocked_req_codes:
                coverage_status = "Blocked"
                coverage_score = 0.3
                validation_status = "Warn"
                blocked += 1
            elif len(mapped_components) > 0 and len(related_adrs) > 0:
                coverage_status = "Fully Covered"
                coverage_score = 1.0
                validation_status = "Pass"
                fully_covered += 1
            elif len(mapped_components) > 0 or len(related_adrs) > 0:
                coverage_status = "Partially Covered"
                coverage_score = 0.65
                validation_status = "Warn"
                partially_covered += 1
            else:
                coverage_status = "Not Covered"
                coverage_score = 0.0
                validation_status = "Fail"
                not_covered += 1

            traceability_items.append({
                "req_code": req_code,
                "req_description": req["description"],
                "req_category": req["category"],
                "evidence_codes": evidence_codes,
                "mapped_component_codes": mapped_components,
                "related_api_ids": related_apis,
                "related_adr_codes": related_adrs,
                "validation_status": validation_status,
                "coverage_status": coverage_status,
                "coverage_score": coverage_score
            })

        total = len(requirements) if requirements else 1
        overall_coverage_pct = round((fully_covered / total) * 100.0, 1)

        return {
            "total_requirements": len(requirements),
            "fully_covered": fully_covered,
            "partially_covered": partially_covered,
            "not_covered": not_covered,
            "blocked": blocked,
            "overall_coverage_pct": overall_coverage_pct,
            "items": traceability_items
        }

    def simulate_change_impact(
        self,
        target_req_code: str,
        modified_description: str,
        requirements: List[Dict[str, Any]],
        components: List[Dict[str, Any]],
        apis: List[Dict[str, Any]],
        adrs: List[Dict[str, Any]],
        risks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Simulates the downstream architectural impact of changing a requirement.
        Identifies affected components, APIs, ADRs, database implications, and scaling risks.
        """
        target_req = next((r for r in requirements if r["req_code"] == target_req_code), None)
        original_desc = target_req["description"] if target_req else "Unknown requirement"

        affected_components = []
        affected_apis = []
        affected_adrs = []
        infrastructure_changes = []
        performance_risks = []
        new_clarifications = []
        database_implications = ""
        scaling_requirements = ""

        # Identify directly affected components
        for c in components:
            if target_req_code in c.get("related_req_codes", []):
                affected_components.append(c["component_code"])

        # Identify directly affected APIs
        for a in apis:
            if target_req_code in a.get("related_req_codes", []):
                affected_apis.append(f"{a['method']} {a['path']}")

        # Identify affected ADRs
        for adr in adrs:
            if target_req_code in adr.get("supporting_req_codes", []):
                affected_adrs.append(adr["adr_code"])

        # Heuristic / Semantic Change Analysis
        mod_lower = modified_description.lower()
        orig_lower = original_desc.lower()

        # Case A: Massive concurrency / TPS increase (e.g. 100k -> 500k or 10k -> 100k)
        if any(term in mod_lower for term in ["500,000", "1,000,000", "200,000", "50,000 tps", "100,000"]):
            infrastructure_changes.extend([
                "Upgrade Edge API Gateway autoscaling policy: max replica count increased from 40 to 180 pods.",
                "Redis Cluster capacity expansion: Shard count must scale from 6 nodes to 18 nodes with read-replicas.",
                "AWS Direct Connect fiber bandwidth upgrade from 10Gbps to redundant 40Gbps dedicated pipes."
            ])
            performance_risks.extend([
                "Core Ledger database connection pool saturation under spike loads.",
                "HSM hardware crypto processing bottleneck at elevated TPS rates.",
                "Increased potential for distributed deadlocks in transactional double-entry ledger."
            ])
            database_implications = "Requires migrating single-writer PostgreSQL to distributed partitioned database (e.g., CockroachDB or YugabyteDB) with localized regional sharding."
            scaling_requirements = "Horizontal autoscaling must switch from CPU-based thresholds to reactive queue-depth and p99 latency metric triggers."
            new_clarifications.append("Does enterprise budget allow multi-million dollar hardware HSM expansion to sustain 50,000+ cryptographically signed TPS?")

        # Case B: Stricter Latency Target (e.g., sub-500ms or 1.0s login)
        elif any(term in mod_lower for term in ["500ms", "1.0s", "sub-second", "1 second"]):
            infrastructure_changes.extend([
                "Deploy CloudFront / Global Edge CDN points of presence for TLS session resumption.",
                "Implement Kernel-bypass DPDK networking on API Gateway hosts."
            ])
            performance_risks.extend([
                "Hybrid network transit latency between edge and on-prem ledger may breach sub-second SLA.",
                "Third-party SMS gateway latency cannot guarantee sub-second delivery."
            ])
            database_implications = "Read queries must be served 100% from in-memory cache; zero database lookups permitted on hot login path."
            scaling_requirements = "Enforce strict circuit-breakers with 250ms fallback timeout."
            new_clarifications.append("Should mobile clients use local biometric key stores to eliminate server-side roundtrips?")

        # Case C: Sovereign Cloud / On-Premise Change
        elif any(term in mod_lower for term in ["cloud-only", "all in aws", "public cloud"]):
            infrastructure_changes.extend([
                "Decommission on-premises Tier-IV datacenter hosting for core banking ledger.",
                "Provision AWS Sovereign Cloud or AWS Nitro Enclaves for cryptographic keys."
            ])
            performance_risks.extend([
                "Severe regulatory compliance violation under National Sovereign Data directives."
            ])
            database_implications = "Migration to AWS Aurora Serverless PostgreSQL with KMS customer-managed keys."
            new_clarifications.append("Has legal compliance approved explicit waiver from Central Bank for cloud hosting of ledger?")

        else:
            infrastructure_changes.append("Component configuration adjustment and scaling threshold recalibration.")
            performance_risks.append("Regression in downstream transaction settlement throughput.")
            database_implications = "Minor schema indexing optimizations recommended."
            scaling_requirements = "Monitor resource utilization during load testing."

        summary = (
            f"Modifying {target_req_code} impacts {len(affected_components)} components ({', '.join(affected_components) or 'None'}), "
            f"{len(affected_apis)} APIs, and {len(affected_adrs)} formal ADRs. "
            f"Identified {len(infrastructure_changes)} required infrastructure modifications and {len(performance_risks)} elevated performance risks."
        )

        return {
            "target_req_code": target_req_code,
            "original_description": original_desc,
            "modified_description": modified_description,
            "affected_components": affected_components,
            "affected_apis": affected_apis,
            "affected_adrs": affected_adrs,
            "infrastructure_changes": infrastructure_changes,
            "performance_risks": performance_risks,
            "database_implications": database_implications,
            "scaling_requirements": scaling_requirements,
            "new_clarification_questions": new_clarifications,
            "comparison_summary": summary,
            "status": "Proposed"
        }

traceability_agent = TraceabilityAgent()

