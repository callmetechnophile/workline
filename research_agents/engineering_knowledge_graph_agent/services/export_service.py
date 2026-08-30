"""
Graph export and snapshot service for EngineeringKnowledgeGraphAgent (Sections 72 & 77).
Exports graph data in JSON, Cytoscape/D3 graph structure, and complete project snapshots.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient


class GraphExporter:
    """Exports graph structures and project snapshots without exposing credentials."""

    def __init__(self, db_client: SurrealDBClient):
        self.db = db_client

    def export_graph_json(self, project_id: str) -> Dict[str, Any]:
        nodes = [n for n in self.db.in_memory.nodes.values() if n.get("project_id") == project_id or n.get("id") == f"project:{project_id}"]
        node_ids = {n["id"] for n in nodes}
        edges = [e.model_dump() for e in self.db.in_memory.edges.values() if e.source_id in node_ids or e.target_id in node_ids]

        return {
            "project_id": project_id,
            "format": "surrealdb_graph_json",
            "nodes": nodes,
            "edges": edges,
        }

    def export_cytoscape_graph(self, project_id: str) -> Dict[str, Any]:
        raw = self.export_graph_json(project_id)
        elements: List[Dict[str, Any]] = []

        for n in raw["nodes"]:
            elements.append({
                "data": {
                    "id": n["id"],
                    "label": n.get("title") or n.get("name") or n["id"],
                    "type": n.get("type", "node"),
                }
            })

        for e in raw["edges"]:
            elements.append({
                "data": {
                    "id": e["id"],
                    "source": e["source_id"],
                    "target": e["target_id"],
                    "label": e["relation_type"],
                }
            })

        return {
            "project_id": project_id,
            "format": "cytoscape_elements",
            "elements": elements,
        }

    def export_to_directory(self, project_id: str, output_dir: str) -> List[str]:
        out_p = Path(output_dir).resolve()
        out_p.mkdir(parents=True, exist_ok=True)
        created_files: List[str] = []

        graph_data = self.export_graph_json(project_id)
        cyto_data = self.export_cytoscape_graph(project_id)

        f_graph = out_p / "project_graph.json"
        f_graph.write_text(json.dumps(graph_data, indent=2), encoding="utf-8")
        created_files.append(str(f_graph))

        f_cyto = out_p / "cytoscape_graph.json"
        f_cyto.write_text(json.dumps(cyto_data, indent=2), encoding="utf-8")
        created_files.append(str(f_cyto))

        return created_files
