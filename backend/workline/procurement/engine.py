"""Workline Procurement Engine: Orchestrates Nexar primary and Scrapling acquisition, deterministic validation, multi-vendor optimization, and BOM lifecycle."""

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import uuid

from backend.workline.database.models import GraphEdge, GraphNode, ProjectModel
from backend.workline.database.repositories.graph_repository import GraphRepository
from backend.workline.database.repositories.project_repository import ProjectRepository
from backend.workline.procurement.datasheets.service import DatasheetService, datasheet_service
from backend.workline.procurement.models import (
    BOM,
    BOMItem,
    BOMStatus,
    ComponentCandidate,
    ComponentRequirement,
    DatasheetMetadata,
    DeterministicValidationReport,
    ProcurementPlan,
)
from backend.workline.procurement.optimize import ProcurementOptimizer
from backend.workline.procurement.providers.manual import ManualProvider
from backend.workline.procurement.providers.nexar import NexarProvider
from backend.workline.procurement.providers.scrapling import ScraplingProvider
from backend.workline.procurement.search import ComponentSearchEngine
from backend.workline.procurement.validate import TechnicalValidator
from backend.workline.retrieval.qdrant import (
    COLLECTION_COMPONENTS,
    COLLECTION_DOCUMENTS,
    COLLECTION_RESEARCH,
    QdrantManager,
    qdrant_manager,
)


class ProcurementEngine:
    """Central service for component sourcing, technical validation, multi-vendor optimization, and BOM lifecycle."""

    def __init__(
        self,
        project_repo: Optional[ProjectRepository] = None,
        graph_repo: Optional[GraphRepository] = None,
        qdrant: Optional[QdrantManager] = None,
        nexar: Optional[NexarProvider] = None,
        scrapling: Optional[ScraplingProvider] = None,
        datasheet_svc: Optional[DatasheetService] = None,
    ):
        self.project_repo = project_repo or ProjectRepository()
        self.graph_repo = graph_repo or GraphRepository()
        self.qdrant = qdrant or qdrant_manager

        self.nexar = nexar or NexarProvider()
        self.scrapling = scrapling or ScraplingProvider()
        self.manual = ManualProvider()
        self.datasheet_service = datasheet_svc or datasheet_service

        self.search_engine = ComponentSearchEngine(
            nexar=self.nexar,
            scrapling=self.scrapling,
            manual=self.manual,
            qdrant=self.qdrant,
            project_repo=self.project_repo,
            graph_repo=self.graph_repo,
        )
        self.validator = TechnicalValidator()
        self.optimizer = ProcurementOptimizer()

        self._components: Dict[str, ComponentCandidate] = {}
        self._boms: Dict[str, BOM] = {}

    async def search_and_validate_candidates(
        self, requirement: ComponentRequirement
    ) -> List[Tuple[ComponentCandidate, DeterministicValidationReport]]:
        """Search across providers and deterministically validate against a requirement."""
        query = f"{requirement.category} {requirement.description or ''}".strip()
        candidates = await self.search_engine.search_vendors(query, limit_per_source=5, requirement=requirement)

        validated_pairs: List[Tuple[ComponentCandidate, DeterministicValidationReport]] = []
        for cand in candidates:
            self._components[cand.component_id] = cand
            report = self.validator.validate(cand, requirement)
            validated_pairs.append((cand, report))

        return validated_pairs

    async def generate_project_bom(
        self, project_id: str, requirements: List[ComponentRequirement]
    ) -> Tuple[BOM, ProcurementPlan]:
        """
        Executes end-to-end procurement sourcing:
        1. Query Nexar (Primary) + Scrapling (Fallback) per requirement.
        2. Programmatically evaluate deterministic constraints.
        3. Optimize single-vendor vs multi-vendor landed costs.
        4. Persist Graph nodes/edges (REQUIRES, SATISFIES, HAS_LISTING, HAS_DATASHEET, CONTAINS, REFERENCES).
        5. Return BOM in READY_FOR_REVIEW state requiring human approval.
        """
        # Ensure project node exists in SurrealDB
        await self.project_repo.get_project(project_id)

        candidate_map: Dict[str, List[ComponentCandidate]] = {}

        # 1. Search and Validate for all requirements
        for req in requirements:
            req_node_id = f"req:{req.requirement_id}"
            await self.graph_repo.save_node(
                GraphNode(
                    id=req_node_id,
                    type="ComponentRequirement",
                    label=f"Req: {req.category} (Qty: {req.quantity})",
                    data={"project_id": project_id, **req.model_dump()},
                )
            )
            await self.graph_repo.save_edge(
                GraphEdge(
                    id=f"requires:{project_id}_{req.requirement_id}",
                    source_id=f"project:{project_id}",
                    target_id=req_node_id,
                    relationship="REQUIRES",
                    data={"project_id": project_id},
                )
            )

            pairs = await self.search_and_validate_candidates(req)
            cands = [p[0] for p in pairs]
            candidate_map[req.requirement_id] = cands

            # Persist candidate nodes & relations
            for cand, report in pairs:
                await self._persist_component_graph(cand, req_node_id, project_id)

        # 2. Multi-Vendor Optimization & Tradeoff Analysis
        plan = self.optimizer.optimize_procurement(project_id, requirements, candidate_map)
        rec_option = plan.recommended_option

        # 3. Create BOM (Status: READY_FOR_REVIEW)
        bom_id = f"bom:{project_id}_{uuid.uuid4().hex[:8]}"
        bom = BOM(
            bom_id=bom_id,
            project_id=project_id,
            version=1,
            status=BOMStatus.READY_FOR_REVIEW,
            total_component_cost=rec_option.total_component_cost,
            estimated_shipping=rec_option.estimated_shipping,
            estimated_total=rec_option.estimated_landed_total,
            currency="INR",
            items=rec_option.items,
            vendor_breakdown={v: 0.0 for v in rec_option.selected_vendors},
        )

        self._boms[bom_id] = bom
        self._boms[project_id] = bom
        self._save_bom_disk(bom)

        # 4. Persist BOM node & CONTAINS edges in SurrealDB
        bom_node_id = f"bom:{project_id}"
        await self.graph_repo.save_node(
            GraphNode(
                id=bom_node_id,
                type="BOM",
                label="Bill of Materials",
                data={"project_id": project_id, **bom.model_dump()},
            )
        )
        await self.graph_repo.save_edge(
            GraphEdge(
                id=f"contains:{project_id}_bom",
                source_id=f"project:{project_id}",
                target_id=bom_node_id,
                relationship="CONTAINS",
                data={"project_id": project_id},
            )
        )

        for item in bom.items:
            await self.graph_repo.save_edge(
                GraphEdge(
                    id=f"ref:{item.bom_item_id}",
                    source_id=bom_node_id,
                    target_id=item.component_id,
                    relationship="REFERENCES",
                    data={"project_id": project_id, "quantity": item.quantity, "vendor": item.selected_vendor},
                )
            )

        # Update Project record with BOM items
        bom_dicts = [
            {
                "item_id": item.bom_item_id,
                "component_name": item.description or item.mpn,
                "mpn": item.mpn,
                "manufacturer": item.manufacturer,
                "vendor": item.selected_vendor,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "extended_price": item.extended_price,
                "currency": item.currency,
                "datasheet_url": item.datasheet_url,
                "validation_status": item.validation_status.value if hasattr(item.validation_status, "value") else str(item.validation_status),
            }
            for item in bom.items
        ]
        await self.project_repo.update_project(project_id, {"bom": bom_dicts})

        return bom, plan

    async def _persist_component_graph(
        self, cand: ComponentCandidate, req_node_id: str, project_id: str
    ) -> None:
        """Saves canonical Component, VendorListing, and Datasheet nodes with relational edges."""
        # 1. Component node
        await self.graph_repo.save_node(
            GraphNode(
                id=cand.component_id,
                type="Component",
                label=f"{cand.manufacturer} {cand.manufacturer_part_number}",
                data={"project_id": project_id, **cand.model_dump()},
            )
        )

        # 2. SATISFIES edge (Component -> Requirement)
        await self.graph_repo.save_edge(
            GraphEdge(
                id=f"sat:{cand.component_id}_{req_node_id.replace(':', '_')}",
                source_id=cand.component_id,
                target_id=req_node_id,
                relationship="SATISFIES",
                data={"project_id": project_id},
            )
        )

        # 3. Vendor Listing nodes and HAS_LISTING / SOLD_BY edges
        for listing in cand.listings:
            listing_node_id = f"listing:{listing.listing_id.replace(':', '_')}"
            await self.graph_repo.save_node(
                GraphNode(
                    id=listing_node_id,
                    type="VendorListing",
                    label=f"{listing.vendor_name} ({listing.currency} {listing.unit_price})",
                    data={"project_id": project_id, **listing.model_dump()},
                )
            )
            await self.graph_repo.save_edge(
                GraphEdge(
                    id=f"has_list:{cand.component_id.replace(':', '_')}_{listing_node_id.replace(':', '_')}",
                    source_id=cand.component_id,
                    target_id=listing_node_id,
                    relationship="HAS_LISTING",
                    data={"project_id": project_id},
                )
            )

        # 4. Datasheet node, HAS_DATASHEET edge, and Qdrant indexing via DatasheetService
        if cand.datasheet:
            meta = DatasheetMetadata(
                datasheet_id=cand.datasheet.datasheet_id,
                component_id=cand.component_id,
                url=cand.datasheet.url,
                manufacturer=cand.manufacturer,
                mpn=cand.manufacturer_part_number,
                title=cand.datasheet.title,
                document_type=cand.datasheet.document_type,
            )
            await self.datasheet_service.verify_and_index(meta, project_id=project_id, component_id=cand.component_id)

    def _save_bom_disk(self, bom: BOM) -> None:
        """Persist BOM JSON to ~/.workline/boms for cross-process CLI availability."""
        try:
            from cli.wline.core.paths import get_config_dir
            bom_dir = get_config_dir() / "boms"
            bom_dir.mkdir(parents=True, exist_ok=True)
            with open(bom_dir / f"{bom.project_id}.json", "w", encoding="utf-8") as fp:
                fp.write(bom.model_dump_json(indent=2))
            clean_id = bom.bom_id.replace(":", "_")
            with open(bom_dir / f"{clean_id}.json", "w", encoding="utf-8") as fp:
                fp.write(bom.model_dump_json(indent=2))
        except Exception:
            pass

    def _load_bom_disk(self, target_id: str) -> Optional[BOM]:
        """Load BOM from ~/.workline/boms."""
        try:
            from cli.wline.core.paths import get_config_dir
            bom_dir = get_config_dir() / "boms"
            clean_id = target_id.replace(":", "_")
            for fname in [f"{target_id}.json", f"{clean_id}.json"]:
                fpath = bom_dir / fname
                if fpath.exists():
                    with open(fpath, "r", encoding="utf-8") as fp:
                        return BOM.model_validate_json(fp.read())
        except Exception:
            pass
        return None

    async def get_bom(self, bom_id_or_project_id: str) -> Optional[BOM]:
        """Fetch BOM by BOM ID or Project ID."""
        if bom_id_or_project_id in self._boms:
            return self._boms[bom_id_or_project_id]

        for b in self._boms.values():
            if b.bom_id == bom_id_or_project_id or b.project_id == bom_id_or_project_id:
                return b

        # Check disk cache
        disk_bom = self._load_bom_disk(bom_id_or_project_id)
        if disk_bom:
            self._boms[disk_bom.bom_id] = disk_bom
            self._boms[disk_bom.project_id] = disk_bom
            return disk_bom

        return None

    async def approve_bom(self, bom_id: str, approved_by: str = "Lead Engineer") -> Optional[BOM]:
        """Human approval action transitioning BOM status from READY_FOR_REVIEW to APPROVED."""
        bom = await self.get_bom(bom_id)
        if not bom:
            # Search by prefix or project id
            for b in self._boms.values():
                if b.bom_id == bom_id or b.project_id == bom_id:
                    bom = b
                    break

        if not bom:
            return None

        bom.status = BOMStatus.APPROVED
        bom.approved_by = approved_by
        bom.updated_at = datetime.now(timezone.utc).isoformat()
        self._boms[bom.bom_id] = bom
        self._boms[bom.project_id] = bom
        self._save_bom_disk(bom)

        # Update SurrealDB node
        bom_node_id = f"bom:{bom.project_id}"
        await self.graph_repo.save_node(
            GraphNode(
                id=bom_node_id,
                type="BOM",
                label="Bill of Materials (APPROVED)",
                data={"project_id": bom.project_id, **bom.model_dump()},
            )
        )
        return bom

    def get_component(self, component_id: str) -> Optional[ComponentCandidate]:
        """Fetch cached component candidate details."""
        return self._components.get(component_id)


# Global procurement engine singleton
procurement_engine = ProcurementEngine()
