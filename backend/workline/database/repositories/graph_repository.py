"""SurrealDB Engineering Knowledge Graph repository for nodes, relations, and traversals."""

from typing import Any, Dict, List, Optional
from backend.workline.database.models import GraphEdge, GraphNode, GraphPayload
from backend.workline.database.surrealdb import SurrealDBManager, surreal_db


class GraphRepository:
    """Repository managing engineering knowledge graph entities and directed relation edges."""

    def __init__(self, db: SurrealDBManager = surreal_db):
        self.db = db
        # In-memory graph index
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: Dict[str, GraphEdge] = {}

    async def create_node(self, node: GraphNode) -> GraphNode:
        """Insert or update a graph node."""
        self._nodes[node.id] = node
        if await self.db.is_connected():
            try:
                table_type = node.type.lower() if node.type else "nodes"
                node_id = f"{table_type}:{node.id}" if not node.id.startswith(f"{table_type}:") else node.id
                sql = f"UPSERT {node_id} CONTENT $data;"
                await self.db.query(sql, {"data": node.model_dump()})
            except Exception:
                pass
        return node

    async def create_edge(self, edge: GraphEdge) -> GraphEdge:
        """Insert a relation edge between nodes."""
        self._edges[edge.id] = edge
        if await self.db.is_connected():
            try:
                rel = edge.relationship.upper()
                sql = f"RELATE {edge.source}->{rel}->{edge.target} SET data = $data;"
                await self.db.query(sql, {"data": edge.data})
            except Exception:
                pass
        return edge

    save_node = create_node
    save_edge = create_edge

    async def get_project_graph(self, project_id: str) -> GraphPayload:
        """
        Query the complete knowledge graph for a project.
        Extracts Subsystems, Components, Connections, Datasheets, and Requirements.
        """
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        # Find nodes belonging to project
        for n in self._nodes.values():
            if n.data.get("project_id") == project_id or n.id == project_id or n.id == f"project:{project_id}":
                nodes.append(n)

        # Find edges connecting project nodes
        node_ids = {n.id for n in nodes}
        for e in self._edges.values():
            if e.source in node_ids or e.target in node_ids or e.data.get("project_id") == project_id:
                edges.append(e)

        # If graph is empty, dynamically construct initial root node
        if not nodes:
            root_id = f"project:{project_id}"
            root_node = GraphNode(
                id=root_id,
                type="Project",
                label=project_id.replace("-", " ").title(),
                data={"project_id": project_id},
            )
            nodes.append(root_node)

        return GraphPayload(nodes=nodes, edges=edges)

    async def get_component_graph(self, component_id: str) -> GraphPayload:
        """Retrieve 1-hop subgraph centered on a component."""
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        target_node = self._nodes.get(component_id)
        if target_node:
            nodes.append(target_node)

        for e in self._edges.values():
            if e.source == component_id or e.target == component_id:
                edges.append(e)
                other_id = e.target if e.source == component_id else e.source
                if other_id in self._nodes and self._nodes[other_id] not in nodes:
                    nodes.append(self._nodes[other_id])

        return GraphPayload(nodes=nodes, edges=edges)

    async def get_subsystem_graph(self, subsystem_id: str) -> GraphPayload:
        """Retrieve subsystem components and interfaces."""
        return await self.get_component_graph(subsystem_id)

    async def get_path_graph(self, source_id: str, target_id: str) -> GraphPayload:
        """Find relationship path between two nodes."""
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        if source_id in self._nodes:
            nodes.append(self._nodes[source_id])
        if target_id in self._nodes and target_id != source_id:
            nodes.append(self._nodes[target_id])

        for e in self._edges.values():
            if (e.source == source_id and e.target == target_id) or (e.source == target_id and e.target == source_id):
                edges.append(e)

        return GraphPayload(nodes=nodes, edges=edges)
