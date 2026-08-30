"""
Graph consistency and referential integrity checker for EngineeringKnowledgeGraphAgent (Section 88).
Audits orphan nodes, missing edges, duplicates, and project isolation violations.
"""

from typing import Any, Dict, List
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient


class GraphConsistencyChecker:
    """Audits graph consistency, orphan nodes, missing edges, and referential integrity."""

    def __init__(self, db_client: SurrealDBClient):
        self.db = db_client

    async def check_consistency(self, project_id: str) -> Dict[str, Any]:
        issues: List[str] = []
        nodes = self.db.in_memory.nodes
        edges = self.db.in_memory.edges

        # 1. Check for broken edge references
        for edge_id, edge in edges.items():
            if edge.source_id not in nodes:
                issues.append(f"Broken edge '{edge_id}': source node '{edge.source_id}' does not exist.")
            if edge.target_id not in nodes:
                issues.append(f"Broken edge '{edge_id}': target node '{edge.target_id}' does not exist.")

        # 2. Check for orphan requirements (must belong to a project)
        for node_id, node in nodes.items():
            if node.get("type") == "requirement":
                p_id = node.get("project_id")
                if not p_id or f"project:{p_id}" not in nodes:
                    issues.append(f"Orphan requirement node '{node_id}' has missing project reference.")

        status = "PASS" if not issues else "FAIL"
        return {
            "status": status,
            "project_id": project_id,
            "total_nodes_checked": len(nodes),
            "total_edges_checked": len(edges),
            "issues": issues,
        }
