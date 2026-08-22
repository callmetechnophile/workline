"""Central PCB Service managing PCB lifecycle, disk caching, and SurrealDB graph persistence."""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from cli.wline.core.paths import get_config_dir
from backend.workline.database.models import GraphEdge, GraphNode
from backend.workline.database.repositories.graph_repository import GraphRepository
from backend.workline.database.repositories.project_repository import ProjectRepository
from backend.workline.pcb.engine.builder import PCBBuilder
from backend.workline.pcb.io.serializer import WLPCBSerializer
from backend.workline.pcb.models.project import PCBProject
from backend.workline.procurement.engine import ProcurementEngine, procurement_engine
from backend.workline.procurement.models import BOM


class PCBService:
    """Orchestrates PCB project creation, updates, and SurrealDB graph persistence."""

    def __init__(
        self,
        procurement: Optional[ProcurementEngine] = None,
        graph_repo: Optional[GraphRepository] = None,
        project_repo: Optional[ProjectRepository] = None,
    ):
        self.procurement = procurement or procurement_engine
        self.graph_repo = graph_repo or GraphRepository()
        self.project_repo = project_repo or ProjectRepository()
        self._pcb_projects: Dict[str, PCBProject] = {}

        self._pcb_dir = get_config_dir() / "pcb"
        self._pcb_dir.mkdir(parents=True, exist_ok=True)

    def _save_disk(self, project: PCBProject) -> None:
        """Saves .wlpcb format to disk cache."""
        try:
            clean_name = project.project_id.replace(":", "_")
            fpath = self._pcb_dir / f"{clean_name}.wlpcb"
            with open(fpath, "w", encoding="utf-8") as fp:
                fp.write(WLPCBSerializer.to_wlpcb_json(project))
            fpath_id = self._pcb_dir / f"{project.id.replace(':', '_')}.wlpcb"
            with open(fpath_id, "w", encoding="utf-8") as fp:
                fp.write(WLPCBSerializer.to_wlpcb_json(project))
        except Exception:
            pass

    def _load_disk(self, project_id: str) -> Optional[PCBProject]:
        """Loads .wlpcb from disk cache."""
        clean_name = project_id.replace(":", "_")
        for candidate in [f"{project_id}.wlpcb", f"{clean_name}.wlpcb"]:
            fpath = self._pcb_dir / candidate
            if fpath.exists():
                try:
                    with open(fpath, "r", encoding="utf-8") as fp:
                        return WLPCBSerializer.from_wlpcb_json(fp.read())
                except Exception:
                    pass
        return None

    async def create_pcb_project(
        self,
        project_id: str,
        bom_id_or_name: Optional[str] = None,
        board_width: float = 80.0,
        board_height: float = 60.0,
    ) -> PCBProject:
        """Constructs and persists a new PCBProject from project BOM."""
        bom = None
        if bom_id_or_name:
            bom = await self.procurement.get_bom(bom_id_or_name)
        if not bom:
            bom = await self.procurement.get_bom(project_id)

        if not bom:
            from backend.workline.procurement.models import BOM, BOMItem, BOMStatus
            bom = BOM(
                bom_id=f"bom_{project_id}",
                project_id=project_id,
                status=BOMStatus.APPROVED,
                items=[
                    BOMItem(
                        bom_item_id=f"bi_mcu_{project_id}",
                        component_id="comp_mcu",
                        manufacturer="Espressif",
                        mpn="ESP32-S3-WROOM-1",
                        category="Microcontroller / Compute Unit",
                        quantity=1,
                        selected_vendor="DigiKey",
                        unit_price=385.0,
                        extended_price=385.0,
                    ),
                    BOMItem(
                        bom_item_id=f"bi_pwr_{project_id}",
                        component_id="comp_pwr",
                        manufacturer="Texas Instruments",
                        mpn="LM2596S-3.3",
                        category="Power Management / Regulator",
                        quantity=1,
                        selected_vendor="DigiKey",
                        unit_price=89.0,
                        extended_price=89.0,
                    ),
                ],
                total_cost=474.0,
            )

        pcb_proj = PCBBuilder.build_from_bom(
            project_id=project_id,
            bom=bom,
            board_width=board_width,
            board_height=board_height,
        )

        self._pcb_projects[pcb_proj.id] = pcb_proj
        self._pcb_projects[project_id] = pcb_proj
        self._save_disk(pcb_proj)

        # Persist to SurrealDB graph
        await self.persist_pcb_graph(pcb_proj)

        return pcb_proj

    async def get_pcb_project(self, project_id_or_pcb_id: str) -> Optional[PCBProject]:
        """Fetch PCB project from memory, disk cache, or graph."""
        if project_id_or_pcb_id in self._pcb_projects:
            return self._pcb_projects[project_id_or_pcb_id]

        disk_proj = self._load_disk(project_id_or_pcb_id)
        if disk_proj:
            self._pcb_projects[disk_proj.id] = disk_proj
            self._pcb_projects[disk_proj.project_id] = disk_proj
            return disk_proj

        return None

    async def update_pcb_project(self, project: PCBProject) -> PCBProject:
        """Updates in-memory state, disk cache, and graph."""
        project.updated_at = datetime.now(timezone.utc).isoformat()
        self._pcb_projects[project.id] = project
        self._pcb_projects[project.project_id] = project
        self._save_disk(project)
        await self.persist_pcb_graph(project)
        return project

    async def persist_pcb_graph(self, pcb_proj: PCBProject) -> None:
        """Persists PCBProject nodes and engineering relationships in SurrealDB."""
        try:
            node_id = f"pcb:{pcb_proj.id}"

            # 1. PCBProject Node
            await self.graph_repo.save_node(
                GraphNode(
                    id=node_id,
                    type="PCBProject",
                    label=f"PCB: {pcb_proj.name} ({pcb_proj.board.width}x{pcb_proj.board.height}mm)",
                    data={
                        "project_id": pcb_proj.project_id,
                        "layer_count": pcb_proj.board.layer_count,
                        "component_count": len(pcb_proj.components),
                        "net_count": len(pcb_proj.nets),
                    },
                )
            )

            # 2. Project -[HAS_PCB]-> PCBProject
            await self.graph_repo.save_edge(
                GraphEdge(
                    id=f"has_pcb:{pcb_proj.project_id}_{pcb_proj.id.replace(':', '_')}",
                    source_id=f"project:{pcb_proj.project_id}",
                    target_id=node_id,
                    relationship="HAS_PCB",
                    data={"project_id": pcb_proj.project_id},
                )
            )

            # 3. PCBComponent Nodes and Relationships
            for comp in pcb_proj.components.values():
                comp_node_id = f"pcb_comp:{comp.id}"
                await self.graph_repo.save_node(
                    GraphNode(
                        id=comp_node_id,
                        type="PCBComponent",
                        label=f"{comp.reference_designator} ({comp.value})",
                        data={
                            "project_id": pcb_proj.project_id,
                            "x": comp.x,
                            "y": comp.y,
                            "footprint_id": comp.footprint_id,
                            "layer": comp.layer,
                        },
                    )
                )

                # PCBProject -[CONTAINS]-> PCBComponent
                await self.graph_repo.save_edge(
                    GraphEdge(
                        id=f"contains:{pcb_proj.id.replace(':', '_')}_{comp.id}",
                        source_id=node_id,
                        target_id=comp_node_id,
                        relationship="CONTAINS",
                        data={"project_id": pcb_proj.project_id},
                    )
                )

                # PCBComponent -[REFERENCES_COMPONENT]-> Canonical Component
                await self.graph_repo.save_edge(
                    GraphEdge(
                        id=f"ref_comp:{comp.id}_{comp.component_id.replace(':', '_')}",
                        source_id=comp_node_id,
                        target_id=comp.component_id,
                        relationship="REFERENCES_COMPONENT",
                        data={"project_id": pcb_proj.project_id},
                    )
                )

                # PCBComponent -[USES_FOOTPRINT]-> Footprint
                await self.graph_repo.save_edge(
                    GraphEdge(
                        id=f"uses_fp:{comp.id}_{comp.footprint_id}",
                        source_id=comp_node_id,
                        target_id=f"footprint:{comp.footprint_id}",
                        relationship="USES_FOOTPRINT",
                        data={"project_id": pcb_proj.project_id},
                    )
                )

            # 4. Net Nodes and PIN_CONNECTS Edges
            for net in pcb_proj.nets.values():
                net_node_id = f"net:{net.id}"
                await self.graph_repo.save_node(
                    GraphNode(
                        id=net_node_id,
                        type="Net",
                        label=f"Net: {net.name} ({net.net_class.value})",
                        data={"project_id": pcb_proj.project_id, "voltage": net.voltage, "priority": net.priority},
                    )
                )
                for node in net.nodes:
                    comp_node_id = f"pcb_comp:{node.component_id}"
                    await self.graph_repo.save_edge(
                        GraphEdge(
                            id=f"conn:{node.component_id}_{net.id}_{node.pin_number}",
                            source_id=comp_node_id,
                            target_id=net_node_id,
                            relationship="PIN_CONNECTS",
                            data={"pin_number": node.pin_number, "pin_name": node.pin_name},
                        )
                    )
        except Exception:
            pass


# Global singleton PCB service
pcb_service = PCBService()
