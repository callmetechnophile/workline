"""
SurrealDB Engineering Knowledge Graph Populator & Provenance Indexer.
Establishes authoritative graph nodes and directed relationships:
Project -> REQUIRES -> EngineeringRequirement -> SATISFIED_BY -> Component
Project -> HAS_CONSTRAINT -> EngineeringConstraint
Project -> RELATED_TO -> ResearchPaper
Component -> HAS_DATASHEET -> Datasheet
Component -> MANUFACTURED_BY -> Manufacturer
ResearchPaper -> SUPPORTS -> EngineeringRequirement
Component -> SATISFIES -> EngineeringRequirement
Component -> VIOLATES -> EngineeringConstraint
Datasheet -> VERIFIES -> EngineeringRequirement
"""

import time
import hashlib
from typing import Dict, Any, List, Optional
from loguru import logger

from backend.workline.database.models import GraphNode, GraphEdge
from backend.workline.database.repositories.graph_repository import GraphRepository
from backend.workline.documents.models import DocumentRecord, DocumentStatus, SectionElement, SourceType
from backend.workline.documents.service import document_service


class KnowledgeGraphPopulator:
    """
    Populates the authoritative SurrealDB Knowledge Graph with requirements,
    constraints, components, datasheets, research papers, and their directed semantic relationships.
    """

    def __init__(self, graph_repo: Optional[GraphRepository] = None):
        self.repo = graph_repo or GraphRepository()

    async def populate_pipeline_graph(
        self,
        project_id: str,
        project_name: str,
        system_specification: str,
        requirements: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        components: List[Dict[str, Any]],
        research_papers: List[Dict[str, Any]],
        violations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Builds the complete project knowledge graph in SurrealDB and registers documents.
        """
        now = time.time()
        project_node_id = f"project:{project_id}"

        # 1. Project Root Node
        await self.repo.create_node(GraphNode(
            id=project_node_id,
            type="Project",
            label=project_name,
            data={
                "project_id": project_id,
                "project_name": project_name,
                "specification": system_specification,
                "source": "USER_INPUT",
                "created_at": now,
            }
        ))

        # 2. Engineering Requirements & Constraints Nodes
        req_node_ids: Dict[str, str] = {}
        for req in requirements:
            req_id = req["requirement_id"]
            node_id = f"requirement:{project_id}_{req_id}"
            req_node_ids[req_id] = node_id

            await self.repo.create_node(GraphNode(
                id=node_id,
                type="EngineeringRequirement",
                label=f"{req_id}: {req['title']}",
                data={**req, "source": req.get("source", "USER_INPUT")},
            ))

            # Project -REQUIRES-> EngineeringRequirement
            await self.repo.create_edge(GraphEdge(
                id=f"edge_req_{project_id}_{req_id}",
                source=project_node_id,
                target=node_id,
                relationship="REQUIRES",
                data={"project_id": project_id, "priority": req.get("priority", "HIGH")},
            ))

            # Validation Criteria Node & Relationship
            val_id = f"validation:{project_id}_{req_id}"
            await self.repo.create_node(GraphNode(
                id=val_id,
                type="ValidationCriteria",
                label=f"Verify {req_id} ({req.get('verification_method', 'Test')})",
                data={
                    "requirement_id": req_id,
                    "method": req.get("verification_method", "Datasheet Verification"),
                    "status": req.get("status", "PENDING"),
                }
            ))
            await self.repo.create_edge(GraphEdge(
                id=f"edge_val_{project_id}_{req_id}",
                source=node_id,
                target=val_id,
                relationship="HAS_VALIDATION",
                data={"method": req.get("verification_method")},
            ))

        for con in constraints:
            con_id = con["constraint_id"]
            node_id = f"constraint:{project_id}_{con_id}"
            await self.repo.create_node(GraphNode(
                id=node_id,
                type="EngineeringConstraint",
                label=f"{con_id}: {con['title']}",
                data={**con, "source": con.get("source", "ENGINEERING_STANDARDS")},
            ))
            await self.repo.create_edge(GraphEdge(
                id=f"edge_con_{project_id}_{con_id}",
                source=project_node_id,
                target=node_id,
                relationship="HAS_CONSTRAINT",
                data={"severity": con.get("severity", "CRITICAL")},
            ))

        # 3. Component, Manufacturer, and Datasheet Nodes
        comp_node_ids: Dict[str, str] = {}
        for comp in components:
            mpn = comp.get("mpn", "UNKNOWN")
            mfr = comp.get("manufacturer", "Generic")
            cid = comp.get("component_id") or f"component:{mfr.lower()}_{mpn.lower()}".replace(" ", "_")
            comp_node_ids[mpn] = cid

            await self.repo.create_node(GraphNode(
                id=cid,
                type="Component",
                label=f"{mfr} {mpn}",
                data={
                    **comp,
                    "source": comp.get("source", "Nexar/Octopart MCP"),
                }
            ))

            # Manufacturer Node & Edge
            mfr_id = f"manufacturer:{mfr.lower().replace(' ', '_')}"
            await self.repo.create_node(GraphNode(
                id=mfr_id,
                type="Manufacturer",
                label=mfr,
                data={"name": mfr, "source": "Nexar/Octopart"},
            ))
            await self.repo.create_edge(GraphEdge(
                id=f"edge_mfr_{mpn}",
                source=cid,
                target=mfr_id,
                relationship="MANUFACTURED_BY",
                data={"mpn": mpn},
            ))

            # Datasheet Node & Edge
            ds_url = comp.get("datasheet_url")
            if ds_url:
                ds_id = f"datasheet:{hashlib.sha256(ds_url.encode()).hexdigest()[:12]}"
                await self.repo.create_node(GraphNode(
                    id=ds_id,
                    type="Datasheet",
                    label=f"{mpn} Datasheet",
                    data={
                        "url": ds_url,
                        "component_id": cid,
                        "mpn": mpn,
                        "source": "Nexar/Octopart",
                    }
                ))
                await self.repo.create_edge(GraphEdge(
                    id=f"edge_ds_{mpn}",
                    source=cid,
                    target=ds_id,
                    relationship="HAS_DATASHEET",
                    data={"url": ds_url},
                ))

            # Requirement -> SATISFIED_BY -> Component and Component -> SATISFIES -> Requirement
            for sat_req_id in comp.get("satisfied_requirement_ids", []):
                if sat_req_id in req_node_ids:
                    r_target = req_node_ids[sat_req_id]
                    await self.repo.create_edge(GraphEdge(
                        id=f"edge_sat_{sat_req_id}_{mpn}",
                        source=r_target,
                        target=cid,
                        relationship="SATISFIED_BY",
                        data={"mpn": mpn},
                    ))
                    await self.repo.create_edge(GraphEdge(
                        id=f"edge_satisfies_{mpn}_{sat_req_id}",
                        source=cid,
                        target=r_target,
                        relationship="SATISFIES",
                        data={"mpn": mpn},
                    ))

        # 4. Constraint Violations
        for viol in violations:
            c_mpn = viol.get("component_mpn")
            c_id = viol.get("constraint_id")
            c_node_id = comp_node_ids.get(c_mpn)
            con_node_id = f"constraint:{project_id}_{c_id}"
            if c_node_id:
                await self.repo.create_edge(GraphEdge(
                    id=f"edge_viol_{c_id}_{c_mpn}",
                    source=c_node_id,
                    target=con_node_id,
                    relationship="VIOLATES",
                    data=viol,
                ))

        # 5. Research Papers Nodes & Relationships
        for paper in research_papers:
            pid = paper.get("paper_id") or f"paper_{hashlib.sha256(paper.get('title', '').encode()).hexdigest()[:10]}"
            p_node_id = f"paper:{pid}"

            await self.repo.create_node(GraphNode(
                id=p_node_id,
                type="ResearchPaper",
                label=paper.get("title", "Research Paper")[:60],
                data={
                    **paper,
                    "source": paper.get("source", "arXiv"),
                }
            ))

            # Project -RELATED_TO-> ResearchPaper
            await self.repo.create_edge(GraphEdge(
                id=f"edge_rel_{project_id}_{pid}",
                source=project_node_id,
                target=p_node_id,
                relationship="RELATED_TO",
                data={"relevance_score": paper.get("relevance_score", 85.0)},
            ))

            # ResearchPaper -SUPPORTS-> EngineeringRequirement
            # Relate first paper to first core requirement
            if req_node_ids:
                first_req_target = list(req_node_ids.values())[0]
                await self.repo.create_edge(GraphEdge(
                    id=f"edge_sup_{pid}_{first_req_target}",
                    source=p_node_id,
                    target=first_req_target,
                    relationship="SUPPORTS",
                    data={"doi": paper.get("doi")},
                ))

            # Register in Knowledge Base Document Index
            doc_id = f"doc_{pid}"
            if doc_id not in document_service._documents:
                source_type = SourceType.RESEARCH_PAPER
                if paper.get("source") == "arXiv":
                    source_type = SourceType.OCTOPART_NEXAR  # or standard external
                doc_record = DocumentRecord(
                    document_id=doc_id,
                    project_id=project_id,
                    team_id="default_team",
                    source_type=SourceType.OCTOPART_NEXAR,
                    source_uri=paper.get("paper_url", ""),
                    filename=f"{paper.get('doi', pid).replace('/', '_')}.pdf",
                    mime_type="application/pdf",
                    title=paper.get("title", "Research Paper"),
                    source_hash=hashlib.sha256(paper.get("title", "").encode()).hexdigest(),
                    content_hash=hashlib.sha256(paper.get("abstract", "").encode()).hexdigest(),
                    created_at=now,
                    updated_at=now,
                    status=DocumentStatus.INDEXED,
                    sections=[
                        SectionElement(
                            section_id=f"{doc_id}_sec1",
                            heading=paper.get("title", "Research Paper"),
                            level=1,
                            page_number=1,
                            paragraphs=[
                                f"**Authors**: {paper.get('authors')}",
                                f"**Publication Year**: {paper.get('publication_year')}",
                                f"**Venue**: {paper.get('venue')}",
                                f"**DOI**: {paper.get('doi')}",
                                f"**Abstract**: {paper.get('abstract')}",
                            ]
                        )
                    ],
                    metadata={
                        "doi": paper.get("doi"),
                        "authors": paper.get("authors"),
                        "venue": paper.get("venue"),
                        "source": paper.get("source"),
                    }
                )
                document_service._documents[doc_id] = doc_record

        # Fetch assembled project graph payload
        graph_payload = await self.repo.get_project_graph(project_id)
        logger.info(f"[KnowledgeGraphPopulator] Successfully indexed {len(graph_payload.nodes)} nodes and {len(graph_payload.edges)} edges in SurrealDB for project '{project_id}'.")
        return graph_payload.model_dump()


# Global populator instance
knowledge_graph_populator = KnowledgeGraphPopulator()
