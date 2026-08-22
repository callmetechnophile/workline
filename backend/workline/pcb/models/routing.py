"""PCB Routing constraints and trace rules."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from backend.workline.pcb.models.net import NetClass


class RoutingConstraint(BaseModel):
    """Geometry and topology rules for trace routing."""
    id: str = "route_rule_default"
    net_class: NetClass = NetClass.DIGITAL
    trace_width: float = 0.254         # mm (10 mil standard)
    clearance: float = 0.200           # mm (8 mil)
    max_length: Optional[float] = None # mm
    preferred_layer: str = "TOP"
    via_allowed: bool = True
    max_via_count: int = 4
    priority: int = 1


class RoutingModel(BaseModel):
    """PCB routing constraint definitions."""
    rules: Dict[str, RoutingConstraint] = Field(default_factory=dict)
    unrouted_nets_count: int = 0
    total_trace_length_mm: float = 0.0
