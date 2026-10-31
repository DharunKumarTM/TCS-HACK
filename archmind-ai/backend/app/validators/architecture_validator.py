"""
Deterministic Architecture Graph Validators for ArchMind AI.
"""

from typing import List, Dict, Any, Tuple
import networkx as nx

class ArchitectureGraphValidator:
    """Provides standalone structural verification of architecture components and dependency graphs."""

    @staticmethod
    def verify_acyclic_graph(components: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """Validates that component inter-dependencies form a strictly acyclic directed graph."""
        G = nx.DiGraph()
        for comp in components:
            G.add_node(comp["component_code"])

        for comp in components:
            src = comp["component_code"]
            for target in comp.get("dependencies", []):
                G.add_edge(src, target)

        cycles = list(nx.simple_cycles(G))
        cycle_paths = [" -> ".join(c + [c[0]]) for c in cycles]
        return len(cycles) == 0, cycle_paths

    @staticmethod
    def calculate_coverage_metrics(components: List[Dict[str, Any]], requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates exact requirement-to-component coverage percentages."""
        if not requirements:
            return {"coverage_pct": 100.0, "uncovered_codes": []}

        mapped_codes = set()
        for comp in components:
            for code in comp.get("related_req_codes", []):
                mapped_codes.add(code)

        all_req_codes = set([r["req_code"] for r in requirements])
        uncovered = list(all_req_codes - mapped_codes)
        pct = (len(mapped_codes.intersection(all_req_codes)) / max(1, len(all_req_codes))) * 100.0

        return {
            "total_requirements": len(requirements),
            "covered_count": len(mapped_codes.intersection(all_req_codes)),
            "uncovered_count": len(uncovered),
            "coverage_pct": round(pct, 1),
            "uncovered_codes": uncovered
        }

architecture_validator = ArchitectureGraphValidator()

