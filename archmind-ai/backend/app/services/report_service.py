import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.database.models import (
    Project, Evidence, Requirement, Conflict, ArchitectureComponent,
    APIEndpoint, DataFlow, ArchitectureDecision, TraceabilityMapping,
    ArchitectureRisk, ValidationResult
)

logger = logging.getLogger("archmind.services.report")

class ReportService:
    """Generates comprehensive Architecture Dossier reports in Markdown and JSON."""

    def generate_markdown_report(self, db: Session, project_id: str) -> str:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return "# ArchMind AI Architecture Dossier\nProject not found."

        evidence = db.query(Evidence).filter(Evidence.project_id == project_id).all()
        requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()
        conflicts = db.query(Conflict).filter(Conflict.project_id == project_id).all()
        components = db.query(ArchitectureComponent).filter(ArchitectureComponent.project_id == project_id).all()
        apis = db.query(APIEndpoint).filter(APIEndpoint.project_id == project_id).all()
        adrs = db.query(ArchitectureDecision).filter(ArchitectureDecision.project_id == project_id).all()
        risks = db.query(ArchitectureRisk).filter(ArchitectureRisk.project_id == project_id).all()
        validations = db.query(ValidationResult).filter(ValidationResult.project_id == project_id).all()
        traceability = db.query(TraceabilityMapping).filter(TraceabilityMapping.project_id == project_id).all()

        md = f"""# ArchMind AI - Enterprise Architecture Dossier
**Project:** {project.name}  
**Generated At:** {project.updated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Status:** {project.status.upper()}  

---

## 1. Executive Summary
ArchMind AI successfully ingested source documents, extracted grounded evidence, analyzed semantic contradictions, and synthesized an enterprise-grade architecture tailored for institutional reliability and regulatory compliance.

- **Total Ingested Evidence:** {len(evidence)} items
- **Normalized Requirements:** {len(requirements)} specifications
- **Detected & Resolved Conflicts:** {len(conflicts)} architectural tensions
- **Decomposed Components:** {len(components)} services
- **Documented ADRs:** {len(adrs)} decisions
- **Traceability Coverage:** {round(len([t for t in traceability if t.coverage_status == 'Fully Covered']) / max(1, len(traceability)) * 100, 1)}%

---

## 2. Evidence Provenance & Stakeholder Statements
| Evidence Code | Category | Source File | Original Excerpt |
|---|---|---|---|
"""
        for ev in evidence[:10]:
            excerpt = ev.original_excerpt.replace("\n", " ")[:90]
            md += f"| **{ev.evidence_code}** | {ev.category} | `{ev.source_filename}` | \"{excerpt}...\" |\n"

        md += """
---

## 3. Normalized Requirements Specification
| REQ Code | Title | Type | Category | Priority | Approval Status |
|---|---|---|---|---|---|
"""
        for req in requirements:
            md += f"| **{req.req_code}** | {req.title} | {req.req_type} | {req.category} | {req.priority} | {req.approval_status} |\n"

        md += """
---

## 4. Conflict Detective & Resolution Register
| Conflict Code | Colliding Requirements | Type | Severity | Resolution Status |
|---|---|---|---|---|
"""
        for conf in conflicts:
            req_str = ", ".join(conf.conflicting_req_codes or [])
            md += f"| **{conf.conflict_code}** | {req_str} | {conf.conflict_type} | {conf.severity} | {conf.status} |\n"

        md += """
---

## 5. Architectural Component Decomposition
| Component Code | Name | Layer | Tech Stack | Deployment Target |
|---|---|---|---|---|
"""
        for comp in components:
            md += f"| **{comp.component_code}** | {comp.name} | {comp.layer} | `{comp.technology_stack}` | {comp.deployment_target} |\n"

        md += """
---

## 6. Architecture Decision Records (ADRs)
"""
        for adr in adrs:
            md += f"""### [{adr.adr_code}] {adr.title}
- **Status:** `{adr.status}`
- **Context:** {adr.context}
- **Decision:** {adr.decision}
- **Trade-Offs:** {adr.trade_offs}
- **Supporting Requirements:** {', '.join(adr.supporting_req_codes or [])}

"""

        md += """---

## 7. Risk Register & Automated Health Validations
| Risk Code | Title | Category | Severity | Score | Mitigation Strategy |
|---|---|---|---|---|---|
"""
        for risk in risks:
            md += f"| **{risk.risk_code}** | {risk.title} | {risk.category} | {risk.severity} | {risk.risk_score} | {risk.mitigation_strategy[:80]}... |\n"

        md += """
---

## 8. Traceability Matrix
| Requirement Code | Description | Mapped Components | Related ADRs | Coverage Status |
|---|---|---|---|---|
"""
        for t in traceability:
            comps = ", ".join(t.mapped_component_codes or []) or "None"
            adrs_str = ", ".join(t.related_adr_codes or []) or "None"
            md += f"| **{t.req_code}** | {t.req_description[:60]}... | {comps} | {adrs_str} | {t.coverage_status} |\n"

        md += "\n\n*Generated autonomously by ArchMind AI – Evidence-Driven Agentic Software Architect.*"
        return md

report_service = ReportService()

