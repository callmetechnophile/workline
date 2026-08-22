"""Authoritative Pydantic PCBProject entity referencing Workline project."""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from backend.workline.pcb.models.board import Board
BoardGeometry = Board
from backend.workline.pcb.models.component import PCBComponent
from backend.workline.pcb.models.constraints import PCBConstraint
from backend.workline.pcb.models.footprint import Footprint
from backend.workline.pcb.models.manufacturing import ManufacturingConstraints
from backend.workline.pcb.models.net import Net
from backend.workline.pcb.models.placement import Placement
from backend.workline.pcb.models.power import PowerModel
from backend.workline.pcb.models.routing import RoutingModel
from backend.workline.pcb.models.signal_integrity import SignalIntegrityModel
from backend.workline.pcb.models.stackup import Stackup
from backend.workline.pcb.models.thermal import ThermalModel


class PCBProject(BaseModel):
    """
    Authoritative PCB Engineering Unit Project Model.
    Directly references the existing Workline project without creating a second project database.
    """
    id: str = Field(default_factory=lambda: f"pcb_proj_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
    project_id: str                    # Parent Workline project identifier
    name: str = "Hardware System PCB"

    board: Board = Field(default_factory=Board)
    stackup: Stackup = Field(default_factory=Stackup)

    components: Dict[str, PCBComponent] = Field(default_factory=dict)
    footprints: Dict[str, Footprint] = Field(default_factory=dict)
    nets: Dict[str, Net] = Field(default_factory=dict)

    constraints: PCBConstraint = Field(default_factory=lambda: PCBConstraint(project_id=""))
    placement: Placement = Field(default_factory=Placement)
    routing: RoutingModel = Field(default_factory=RoutingModel)

    power: PowerModel = Field(default_factory=PowerModel)
    thermal: ThermalModel = Field(default_factory=ThermalModel)
    signal_integrity: SignalIntegrityModel = Field(default_factory=SignalIntegrityModel)
    manufacturing: ManufacturingConstraints = Field(default_factory=ManufacturingConstraints)

    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
