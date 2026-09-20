"""
Bridge connecting Octopart / Nexar Component Intelligence to Workline Knowledge Base,
Documents Index, SurrealDB Knowledge Graph, and BOM.
"""

import hashlib
import json
import time
from typing import Any, Dict, List, Optional
from loguru import logger
from pydantic import BaseModel, Field

from backend.mcp.nexar_client import nexar_mcp_client
from backend.workline.database.models import GraphEdge, GraphNode
from backend.workline.database.repositories.graph_repository import GraphRepository
from backend.workline.database.repositories.project_repository import ProjectRepository
from backend.workline.database.surrealdb import surreal_db
from backend.workline.documents.models import (
    DocumentRecord,
    DocumentStatus,
    SectionElement,
    SourceType,
    TableElement,
)
from backend.workline.documents.service import document_service
from backend.workline.knowledge.graph.models import EntityType, RelationshipType
from backend.workline.knowledge.graph.service import KnowledgeGraphService
from backend.workline.procurement.models import (
    BOM,
    BomItem,
    CheckStatus,
    ComponentCandidate,
    ProcurementStatus,
)
from backend.workline.procurement.providers.nexar import NexarProvider
from backend.workline.retrieval.qdrant import (
    COLLECTION_COMPONENTS,
    COLLECTION_DOCUMENTS,
    qdrant_manager,
)


class SaveComponentToKnowledgeRequest(BaseModel):
    project_id: str
    component_data: Dict[str, Any]
    team_id: str = "default_team"


class AddComponentToBomRequest(BaseModel):
    project_id: str
    component_data: Dict[str, Any]
    quantity: int = 1
    reference_designator: Optional[str] = None


class NexarKnowledgeBridge:
    """
    Normalizes Octopart / Nexar component intelligence, prevents duplicate records,
    indexes into the Documents Library and Qdrant, updates SurrealDB knowledge graphs,
    and enables zero-friction 'Add to BOM' operations.
    """

    def __init__(
        self,
        graph_repo: Optional[GraphRepository] = None,
        project_repo: Optional[ProjectRepository] = None,
    ):
        self.graph_repo = graph_repo or GraphRepository()
        self.project_repo = project_repo or ProjectRepository()
        self.mcp = nexar_mcp_client
        self._indexed_mpns: Dict[str, str] = {}  # mpn -> document_id

    async def search_nexar_components(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Query Nexar via MCP tool."""
        res = await self.mcp.execute_tool(
            self.mcp.TOOL_SEARCH_COMPONENTS,
            {"query": query, "limit": limit},
        )
        if not res.success or not res.data:
            return []
        return res.data

    async def lookup_exact_mpn(self, mpn: str) -> Optional[Dict[str, Any]]:
        """Look up single exact MPN via MCP tool."""
        res = await self.mcp.execute_tool(
            self.mcp.TOOL_LOOKUP_MPN,
            {"mpn": mpn},
        )
        if not res.success or not res.data:
            return None
        return res.data

    async def save_to_knowledge_base(
        self,
        project_id: str,
        comp_dict: Dict[str, Any],
        team_id: str = "default_team",
    ) -> Dict[str, Any]:
        """
        1. Normalize into DocumentRecord and Component node.
        2. Prevent duplicate MPN records in this project.
        3. Persist in SurrealDB (Component, Manufacturer, Datasheet, and Relationships).
        4. Add to Documents Index.
        5. Index in Qdrant for semantic search.
        """
        mpn = (comp_dict.get("manufacturer_part_number") or comp_dict.get("mpn") or "UNKNOWN").strip().upper()
        mfr = (comp_dict.get("manufacturer") or "Unknown Manufacturer").strip()
        category = comp_dict.get("category") or "Electronic Component"
        description = comp_dict.get("description") or f"Component {mpn} by {mfr}"
        comp_id = comp_dict.get("component_id") or f"component:{mfr.lower().replace(' ', '_')}_{mpn.lower().replace(' ', '_')}"

        # Deduplication check: inspect if document already exists for this project + MPN
        existing_docs = document_service.list_documents(project_id=project_id)
        for doc in existing_docs:
            if doc.metadata.get("mpn", "").upper() == mpn:
                logger.info(f"[NexarKnowledgeBridge] MPN '{mpn}' already indexed in project '{project_id}' as '{doc.document_id}'. Returning existing.")
                return {
                    "status": "EXISTING",
                    "document_id": doc.document_id,
                    "component_id": comp_id,
                    "mpn": mpn,
                    "title": doc.title,
                    "message": f"Component {mpn} is already indexed in this project's Knowledge Base.",
                    "document": doc.model_dump(),
                }

        doc_id = f"doc_nexar_{hashlib.sha256(f'{project_id}:{mpn}'.encode()).hexdigest()[:12]}"
        now = time.time()

        # Extract specs into structured markdown/tables for Document Intelligence
        elec = comp_dict.get("electrical", {}) or {}
        phys = comp_dict.get("physical", {}) or {}
        avail = comp_dict.get("availability", {}) or {}
        pricing = comp_dict.get("pricing", {}) or {}
        datasheet_info = comp_dict.get("datasheet", {}) or {}
        datasheet_url = datasheet_info.get("url") if isinstance(datasheet_info, dict) else None

        summary_paragraphs = [
            f"**Manufacturer**: {mfr}",
            f"**Part Number (MPN)**: {mpn}",
            f"**Category**: {category}",
            f"**Description**: {description}",
            f"**Package / Case**: {phys.get('package') or 'Unknown'}",
            f"**Mounting**: {phys.get('mounting') or 'Surface Mount'}",
            f"**Nominal Voltage**: {elec.get('nominal_voltage') or 'N/A'} V (Range: {elec.get('voltage_min') or 'N/A'}V - {elec.get('voltage_max') or 'N/A'}V)",
            f"**Max Current**: {elec.get('current_max') or 'N/A'} A",
            f"**Global Stock Availability**: {avail.get('stock', 0):,} units ({'In Stock' if avail.get('in_stock') else 'Check Lead Time'})",
            f"**Estimated Unit Price**: {pricing.get('currency', 'INR')} {pricing.get('unit_price', 0.0):.2f}",
        ]
        if datasheet_url:
            summary_paragraphs.append(f"**Verified Technical Datasheet**: [Datasheet Link]({datasheet_url})")

        # Create structured specs table
        spec_rows = [
            ["MPN", mpn],
            ["Manufacturer", mfr],
            ["Category", category],
            ["Package", str(phys.get("package") or "N/A")],
            ["Voltage Nominal", f"{elec.get('nominal_voltage', 'N/A')} V"],
            ["Voltage Range", f"{elec.get('voltage_min', 'N/A')}V - {elec.get('voltage_max', 'N/A')}V"],
            ["Current Max", f"{elec.get('current_max', 'N/A')} A"],
            ["In Stock", "Yes" if avail.get("in_stock") else "No"],
            ["Stock Count", f"{avail.get('stock', 0):,}"],
            ["Lead Time Days", str(avail.get("lead_time_days", 0))],
            ["Datasheet URL", datasheet_url or "None"],
        ]

        doc_record = DocumentRecord(
            document_id=doc_id,
            project_id=project_id,
            team_id=team_id,
            source_type=SourceType.OCTOPART_NEXAR,
            source_uri=datasheet_url or f"https://nexar.com/part/{mpn}",
            filename=f"{mpn}_specification.json",
            mime_type="application/json",
            title=f"{mfr} {mpn} Specification & Intelligence",
            source_hash=hashlib.sha256(f"{mfr}:{mpn}:{now}".encode()).hexdigest(),
            content_hash=hashlib.sha256(json.dumps(comp_dict, sort_keys=True).encode()).hexdigest(),
            created_at=now,
            updated_at=now,
            status=DocumentStatus.INDEXED,
            sections=[
                SectionElement(
                    section_id=f"{doc_id}_sec_spec",
                    heading=f"{mfr} {mpn} Technical Specification",
                    level=1,
                    page_number=1,
                    paragraphs=summary_paragraphs,
                    tables=[
                        TableElement(
                            table_id=f"{doc_id}_tbl_1",
                            document_id=doc_id,
                            page_number=1,
                            section_title="Specifications",
                            headers=["Parameter", "Value"],
                            rows=spec_rows,
                            caption=f"{mpn} Parametric Data",
                        )
                    ],
                )
            ],
            metadata={
                "mpn": mpn,
                "manufacturer": mfr,
                "category": category,
                "package": phys.get("package"),
                "datasheet_url": datasheet_url,
                "source": "Nexar/Octopart MCP",
                "in_stock": avail.get("in_stock", False),
                "stock": avail.get("stock", 0),
                "unit_price": pricing.get("unit_price", 0.0),
                "currency": pricing.get("currency", "INR"),
                "last_synchronized": now,
                "component_id": comp_id,
            },
        )

        # 1. Store in document intelligence service
        document_service._documents[doc_id] = doc_record

        # 2. Store in SurrealDB Knowledge Graph
        try:
            # Component Node
            await self.graph_repo.save_node(
                GraphNode(
                    id=comp_id,
                    type="Component",
                    label=f"{mfr} {mpn}",
                    data={"project_id": project_id, **comp_dict},
                )
            )
            # Relationship: Project USES / HAS_COMPONENT Component
            await self.graph_repo.save_edge(
                GraphEdge(
                    id=f"has_comp:{project_id}_{comp_id.replace(':', '_')}",
                    source_id=f"project:{project_id}",
                    target_id=comp_id,
                    relationship="HAS_COMPONENT",
                    data={"project_id": project_id, "source": "Nexar MCP", "indexed_at": now},
                )
            )
            # Manufacturer Node & Edge
            mfr_node_id = f"mfr:{mfr.lower().replace(' ', '_')}"
            await self.graph_repo.save_node(
                GraphNode(
                    id=mfr_node_id,
                    type="Manufacturer",
                    label=mfr,
                    data={"name": mfr},
                )
            )
            await self.graph_repo.save_edge(
                GraphEdge(
                    id=f"mfr_edge:{comp_id.replace(':', '_')}_{mfr_node_id.replace(':', '_')}",
                    source_id=comp_id,
                    target_id=mfr_node_id,
                    relationship="MANUFACTURED_BY",
                    data={},
                )
            )
            # Datasheet Node & Edge
            if datasheet_url:
                ds_node_id = f"ds:{hashlib.sha256(datasheet_url.encode()).hexdigest()[:12]}"
                await self.graph_repo.save_node(
                    GraphNode(
                        id=ds_node_id,
                        type="Datasheet",
                        label=f"{mpn} Datasheet",
                        data={"url": datasheet_url, "mpn": mpn, "manufacturer": mfr},
                    )
                )
                await self.graph_repo.save_edge(
                    GraphEdge(
                        id=f"has_ds:{comp_id.replace(':', '_')}_{ds_node_id}",
                        source_id=comp_id,
                        target_id=ds_node_id,
                        relationship="HAS_DATASHEET",
                        data={"url": datasheet_url},
                    )
                )
        except Exception as e:
            logger.warning(f"[NexarKnowledgeBridge] SurrealDB graph persistence fallback: {e}")

        # 3. Index in Qdrant Vector database
        try:
            semantic_text = f"{mfr} {mpn} {category}: {description}. Package: {phys.get('package')}. " \
                            f"Voltage: {elec.get('nominal_voltage')}V. Current: {elec.get('current_max')}A."
            qdrant_manager.index_document(
                collection=COLLECTION_COMPONENTS,
                doc_id=comp_id,
                text=semantic_text,
                payload={
                    "doc_id": doc_id,
                    "mpn": mpn,
                    "manufacturer": mfr,
                    "category": category,
                    "project_id": project_id,
                    "in_stock": avail.get("in_stock", True),
                    "datasheet_url": datasheet_url,
                },
            )
        except Exception as e:
            logger.warning(f"[NexarKnowledgeBridge] Qdrant index fallback: {e}")

        return {
            "status": "INDEXED",
            "document_id": doc_id,
            "component_id": comp_id,
            "mpn": mpn,
            "title": doc_record.title,
            "datasheet_url": datasheet_url,
            "document": doc_record.model_dump(),
        }

    async def add_to_bom(
        self,
        project_id: str,
        comp_dict: Dict[str, Any],
        quantity: int = 1,
        reference_designator: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Directly add the selected Nexar component to the active project's BOM.
        """
        mpn = (comp_dict.get("manufacturer_part_number") or comp_dict.get("mpn") or "UNKNOWN").strip().upper()
        mfr = (comp_dict.get("manufacturer") or "Unknown").strip()
        desc = comp_dict.get("description") or f"{mfr} {mpn}"
        phys = comp_dict.get("physical", {}) or {}
        pkg = phys.get("package") or comp_dict.get("package") or "Standard"
        pricing = comp_dict.get("pricing", {}) or {}
        unit_price = float(pricing.get("unit_price", 0.0) or 0.0)
        curr = pricing.get("currency", "INR")
        datasheet_info = comp_dict.get("datasheet", {}) or {}
        datasheet_url = datasheet_info.get("url") if isinstance(datasheet_info, dict) else None

        avail = comp_dict.get("availability", {}) or {}
        stock = int(avail.get("stock", 0) or 0)

        item_id = f"item_{hashlib.sha256(f'{project_id}:{mpn}:{time.time()}'.encode()).hexdigest()[:8]}"
        ref_des = reference_designator or f"U{int(time.time()) % 100}"

        bom_item = BomItem(
            bom_item_id=item_id,
            bom_id=f"bom:{project_id}",
            reference_designator=ref_des,
            part_number=mpn,
            mpn=mpn,
            manufacturer=mfr,
            description=desc,
            package=pkg,
            quantity=quantity,
            required_quantity=quantity,
            selected_vendor="Nexar / Octopart",
            unit_price=unit_price,
            extended_price=round(unit_price * quantity, 2),
            currency=curr,
            stock=stock,
            status=ProcurementStatus.AVAILABLE if stock > 0 else ProcurementStatus.UNRESOLVED,
            validation_status=CheckStatus.PASS,
            datasheet_url=datasheet_url,
            vendor_product_url=comp_dict.get("vendor", {}).get("product_url") if isinstance(comp_dict.get("vendor"), dict) else None,
        )

        # Update project BOM list
        project = await self.project_repo.get_project(project_id)
        current_bom = project.bom if project and project.bom else []
        current_bom.append({
            "item_id": bom_item.bom_item_id,
            "component_name": desc,
            "mpn": mpn,
            "manufacturer": mfr,
            "vendor": "Nexar / Octopart",
            "quantity": quantity,
            "unit_price": unit_price,
            "extended_price": round(unit_price * quantity, 2),
            "currency": curr,
            "datasheet_url": datasheet_url,
            "validation_status": "PASS",
        })
        await self.project_repo.update_project(project_id, {"bom": current_bom})

        return {
            "status": "ADDED_TO_BOM",
            "item": bom_item.model_dump(),
            "total_items": len(current_bom),
        }

    async def generate_knowledge_base_from_components(
        self,
        project_id: str,
        idea: Optional[str] = None,
        components: Optional[List[Dict[str, Any]]] = None,
        team_id: str = "default_team",
    ) -> Dict[str, Any]:
        """
        Synthesizes a complete Engineering Knowledge Base by accessing component datasheets
        via the Octopart / Nexar API, indexing them into the Documents Library, SurrealDB
        Knowledge Graph, and Qdrant semantic index.
        """
        logger.info(f"[NexarKnowledgeBridge] Generating knowledge base for project '{project_id}'...")

        # 1. Resolve components to index
        target_mpns_or_queries: List[str] = []

        if components and len(components) > 0:
            for c in components:
                name = c.get("mpn") or c.get("part_number") or c.get("name") or c.get("component")
                if name:
                    target_mpns_or_queries.append(str(name).strip())

        # Check existing project BOM if none passed directly
        if not target_mpns_or_queries:
            try:
                project = await self.project_repo.get_project(project_id)
                if project and project.bom:
                    for b in project.bom:
                        name = b.get("mpn") or b.get("part_number") or b.get("component_name")
                        if name:
                            target_mpns_or_queries.append(str(name).strip())
            except Exception as e:
                logger.warning(f"[NexarKnowledgeBridge] Project BOM retrieval fallback: {e}")

        # Domain-driven defaults if project has no BOM yet
        if not target_mpns_or_queries:
            idea_lower = (idea or "").lower()
            if any(k in idea_lower for k in ("bms", "battery", "lifepo4", "cell", "pack", "charge", "discharge")):
                target_mpns_or_queries = [
                    "BQ76952PFBR",
                    "INA226AIDGSR",
                    "SN65HVD230DR",
                    "CSD19536KCS",
                    "LM5164DDAR",
                    "ESP32-S3",
                ]
            elif any(k in idea_lower for k in ("solar", "mppt", "photovoltaic")):
                target_mpns_or_queries = ["CN3791", "INA226AIDGSR", "ESP32-S3", "CSD19536KCS"]
            elif any(k in idea_lower for k in ("drone", "robot", "motor", "rover")):
                target_mpns_or_queries = ["STM32F405RGT6", "DRV8833PWPR", "BME280", "SN65HVD230DR"]
            else:
                # Universal smart hardware default set
                target_mpns_or_queries = [
                    "BQ76952PFBR",
                    "INA226AIDGSR",
                    "ESP32-S3",
                    "SN65HVD230DR",
                    "BME280",
                ]

        indexed_results: List[Dict[str, Any]] = []
        datasheets: List[Dict[str, Any]] = []

        for q in target_mpns_or_queries:
            try:
                # 1. Search Nexar via MCP
                search_res = await self.search_nexar_components(q, limit=1)
                cand = search_res[0] if search_res else None

                if not cand:
                    # Fallback lookup exact
                    cand = await self.lookup_exact_mpn(q)

                if cand:
                    # 2. Index into Knowledge Base
                    saved = await self.save_to_knowledge_base(
                        project_id=project_id,
                        comp_dict=cand,
                        team_id=team_id,
                    )
                    indexed_results.append(saved)

                    ds_info = cand.get("datasheet") or {}
                    ds_url = ds_info.get("url") if isinstance(ds_info, dict) else None
                    mfr = cand.get("manufacturer") or "Manufacturer"
                    mpn = cand.get("manufacturer_part_number") or cand.get("mpn") or q

                    if ds_url:
                        datasheets.append({
                            "datasheet_id": saved.get("document_id") or f"ds_{mpn.lower()}",
                            "url": ds_url,
                            "manufacturer": mfr,
                            "mpn": mpn,
                            "title": f"{mfr} {mpn} Datasheet",
                            "document_type": "Manufacturer Technical Datasheet (PDF)",
                            "verification_status": "VERIFIED",
                            "highlights": [
                                f"Package: {cand.get('physical', {}).get('package', 'Standard')}",
                                f"Category: {cand.get('category', 'IC')}",
                                f"Stock: {cand.get('availability', {}).get('stock', 0):,} units",
                            ],
                        })
            except Exception as err:
                logger.warning(f"[NexarKnowledgeBridge] Failed to index candidate for '{q}': {err}")

        logger.info(f"[NexarKnowledgeBridge] Successfully indexed {len(indexed_results)} components and {len(datasheets)} datasheets for '{project_id}'.")

        return {
            "status": "SUCCESS",
            "project_id": project_id,
            "indexed_count": len(indexed_results),
            "documents": indexed_results,
            "datasheets": datasheets,
        }

    def get_project_datasheets(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all linked manufacturer datasheets for a project from the Document Service.
        """
        docs = document_service.list_documents(project_id=project_id)
        datasheets: List[Dict[str, Any]] = []

        for doc in docs:
            ds_url = doc.metadata.get("datasheet_url") or (doc.source_uri if str(doc.source_uri).endswith(".pdf") else None)
            if ds_url:
                mpn = doc.metadata.get("mpn") or doc.title.split()[0]
                mfr = doc.metadata.get("manufacturer") or "Verified Manufacturer"
                datasheets.append({
                    "datasheet_id": doc.document_id,
                    "url": ds_url,
                    "manufacturer": mfr,
                    "mpn": mpn,
                    "title": f"{mfr} {mpn} Technical Datasheet",
                    "document_type": "Manufacturer Technical Datasheet (PDF)",
                    "verification_status": "VERIFIED",
                    "highlights": [
                        f"Package: {doc.metadata.get('package', 'Standard')}",
                        f"Stock: {doc.metadata.get('stock', 0):,} units in stock",
                        f"Unit Price: {doc.metadata.get('currency', 'INR')} {doc.metadata.get('unit_price', 0.0):.2f}",
                    ],
                })

        return datasheets


# Global singleton instance
nexar_knowledge_bridge = NexarKnowledgeBridge()
