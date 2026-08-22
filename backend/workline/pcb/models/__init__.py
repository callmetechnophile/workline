"""PCB Engineering Models package."""

from backend.workline.pcb.models.board import Board, BoardShape, Cutout, Keepout, MountingHole
from backend.workline.pcb.models.component import PCBComponent
from backend.workline.pcb.models.constraints import (
    ConstraintScope,
    ConstraintSource,
    PCBConstraint,
    PCBConstraintItem,
)
from backend.workline.pcb.models.footprint import Footprint, Pad
from backend.workline.pcb.models.layer import Layer, LayerType
from backend.workline.pcb.models.manufacturing import ManufacturingConstraints
from backend.workline.pcb.models.net import Net, NetClass, NetNode
from backend.workline.pcb.models.pin import ElectricalType, Pin
from backend.workline.pcb.models.placement import (
    ComponentPlacement,
    Placement,
    PlacementZone,
    ZoneType,
)
from backend.workline.pcb.models.power import PowerModel, PowerRail, PowerViolationFlag
from backend.workline.pcb.models.project import PCBProject
from backend.workline.pcb.models.routing import RoutingConstraint, RoutingModel
from backend.workline.pcb.models.signal_integrity import (
    PowerIntegrityFeature,
    SignalIntegrityFeature,
    SignalIntegrityModel,
)
from backend.workline.pcb.models.stackup import Stackup
from backend.workline.pcb.models.thermal import (
    BoardThermalProperties,
    ThermalComponent,
    ThermalModel,
)

__all__ = [
    "PCBProject",
    "Board",
    "BoardShape",
    "MountingHole",
    "Cutout",
    "Keepout",
    "Footprint",
    "Pad",
    "Pin",
    "ElectricalType",
    "PCBComponent",
    "Net",
    "NetNode",
    "NetClass",
    "Layer",
    "LayerType",
    "Stackup",
    "Placement",
    "ComponentPlacement",
    "PlacementZone",
    "ZoneType",
    "RoutingConstraint",
    "RoutingModel",
    "PCBConstraint",
    "PCBConstraintItem",
    "ConstraintSource",
    "ConstraintScope",
    "PowerRail",
    "PowerModel",
    "PowerViolationFlag",
    "ThermalComponent",
    "BoardThermalProperties",
    "ThermalModel",
    "SignalIntegrityFeature",
    "PowerIntegrityFeature",
    "SignalIntegrityModel",
    "ManufacturingConstraints",
]
