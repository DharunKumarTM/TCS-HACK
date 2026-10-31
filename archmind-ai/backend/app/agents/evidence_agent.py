import re
import logging
from typing import List, Dict, Any
from app.services.gemini_service import gemini_service
from app.rag.retriever import evidence_retriever

logger = logging.getLogger("archmind.agents.evidence")

SYSTEM_PROMPT = """You are the Evidence Intelligence Agent of ArchMind AI.
Your job is to rigorously examine ingested document chunks, PRDs, transcripts, and policies.
Extract grounded evidence statements preserving original excerpts, file provenance, and speaker attributions.
Distinguish facts, constraints, policies, and architecture preferences.
Output structured evidence objects with confidence score and quality grade."""

class EvidenceIntelligenceAgent:
    """Agent 1: Extracts, grades, deduplicates, and classifies evidence from source documents."""

    def extract_evidence(self, parsed_documents: List[Dict[str, Any]], chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        evidence_list = []
        ev_counter = 1

        # Use Gemini for deep semantic extraction if available
        if gemini_service.is_live():
            for doc in parsed_documents:
                prompt = f"""Analyze the following document '{doc['filename']}' and extract all concrete evidence items, stakeholder quotes, technical constraints, and policies:
---
{doc['raw_text'][:5000]}
---
Return a JSON array of objects with keys:
- statement: string (normalized statement)
- category: string ("Functional", "Non-Functional", "Constraint", "Policy", or "Architecture Preference")
- original_excerpt: string (exact verbatim quote)
- location_reference: string (page or section reference)
- confidence_score: float (0.8 - 1.0)
- quality_grade: string ("High", "Medium", "Low")
"""
                result = gemini_service.generate_structured(prompt, SYSTEM_PROMPT)
                if result and isinstance(result, list):
                    for item in result:
                        evidence_list.append({
                            "evidence_code": f"EV-{ev_counter:03d}",
                            "source_filename": doc["filename"],
                            "statement": item.get("statement", ""),
                            "category": item.get("category", "Functional"),
                            "original_excerpt": item.get("original_excerpt", ""),
                            "location_reference": item.get("location_reference", "General"),
                            "confidence_score": float(item.get("confidence_score", 0.95)),
                            "quality_grade": item.get("quality_grade", "High"),
                            "is_duplicate": False
                        })
                        ev_counter += 1

        # If LLM didn't produce results or offline, perform deterministic semantic extraction
        if not evidence_list:
            evidence_list = self._deterministic_extract(parsed_documents, chunks)

        # Deduplicate statements
        deduplicated = self._deduplicate_evidence(evidence_list)
        return deduplicated

    def _deterministic_extract(self, docs: List[Dict[str, Any]], chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        extracted = []
        ev_idx = 1

        for doc in docs:
            filename = doc["filename"]
            raw_text = doc["raw_text"]

            # 1. Stakeholder quotes extraction
            quotes = doc.get("stakeholder_quotes", [])
            for q in quotes:
                speaker = q["speaker"]
                stmt = q["statement"]
                category = "Architecture Preference"
                if any(k in stmt.lower() for k in ["latency", "second", "tps", "concurrent", "uptime", "availability", "ms"]):
                    category = "Non-Functional"
                elif any(k in stmt.lower() for k in ["pci", "mandate", "prohibit", "must reside", "sovereign", "audit", "policy", "hipaa", "gdpr", "compliance"]):
                    category = "Policy"
                elif any(k in stmt.lower() for k in ["sms", "otp", "biometric", "payment", "fund transfer", "login", "user", "api"]):
                    category = "Functional"

                extracted.append({
                    "evidence_code": f"EV-{ev_idx:03d}",
                    "source_filename": filename,
                    "statement": f"{speaker} states: {stmt}",
                    "category": category,
                    "original_excerpt": f'"{speaker}: {stmt}"',
                    "location_reference": "Stakeholder Statements",
                    "confidence_score": 0.98,
                    "quality_grade": "High",
                    "is_duplicate": False
                })
                ev_idx += 1

            # 2. Section, bullet points and sentences extraction
            sections = doc.get("sections", [])
            candidate_lines = []

            for sec in sections:
                header = sec["header"]
                content = sec["content"]
                # Split by newline or sentence terminators
                raw_lines = re.split(r"(?<=[.!?])\s+|\n+", content)
                for line in raw_lines:
                    line_clean = line.strip()
                    if len(line_clean) >= 20:
                        candidate_lines.append((header, line_clean))

            # Also check if no sections were parsed
            if not candidate_lines and raw_text:
                for line in re.split(r"(?<=[.!?])\s+|\n+", raw_text):
                    line_clean = line.strip()
                    if len(line_clean) >= 20:
                        candidate_lines.append(("General Requirements", line_clean))

            for header, line_clean in candidate_lines:
                lower = line_clean.lower()
                is_bullet = line_clean.startswith(("-", "*", "•", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9."))
                has_code = any(code in line_clean for code in ["FR-", "NFR-", "SEC-", "POL-", "REQ-"])
                has_req_keyword = any(kw in lower for kw in [
                    "must", "shall", "should", "will", "require", "latency", "scale", "concurrent",
                    "performance", "encrypt", "security", "database", "api", "cloud", "on-prem",
                    "support", "provide", "platform", "user", "service", "storage", "privacy", "audit"
                ])

                if is_bullet or has_code or has_req_keyword:
                    cat = "Functional"
                    if any(k in lower for k in ["perf", "latency", "scale", "concurrent", "avail", "99.99%", "rto", "rpo", "tps", "ms", "seconds"]):
                        cat = "Non-Functional"
                    elif any(k in lower for k in ["sec-", "pci", "hipaa", "gdpr", "encrypt", "residency", "audit", "mfa", "policy", "sovereign", "compliance"]):
                        cat = "Policy"
                    elif any(k in lower for k in ["datacenter", "on-prem", "aws", "azure", "gcp", "cloud", "bare metal", "kubernetes", "docker"]):
                        cat = "Constraint"

                    extracted.append({
                        "evidence_code": f"EV-{ev_idx:03d}",
                        "source_filename": filename,
                        "statement": line_clean.lstrip("-*•123456789. "),
                        "category": cat,
                        "original_excerpt": line_clean,
                        "location_reference": f"Section: {header}",
                        "confidence_score": 0.95,
                        "quality_grade": "High",
                        "is_duplicate": False
                    })
                    ev_idx += 1

        return extracted

    def _deduplicate_evidence(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_statements = set()
        clean_items = []
        for item in items:
            normalized = re.sub(r"[^a-zA-Z0-9]", "", item["statement"].lower())
            if normalized in seen_statements:
                item["is_duplicate"] = True
            else:
                seen_statements.add(normalized)
                item["is_duplicate"] = False
            clean_items.append(item)
        return clean_items

evidence_agent = EvidenceIntelligenceAgent()
