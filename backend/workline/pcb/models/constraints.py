"""PCB Engineering Design Constraints with provenance tracking."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ConstraintSource(str, Enum):
    """Authoritative provenance origin of an engineering constraint."""
    USER = "USER"
    DATASHEET = "DATASHEET"
    ENGINEERING_RULE = "ENGINEERING_RULE"
    MANUFACTURING_RULE = "MANUFACTURING_RULE"


class ConstraintScope(str, Enum):
    """Scope of application for the constraint."""
    GLOBAL = "GLOBAL"
    NET_CLASS = "NET_CLASS"
    COMPONENT = "COMPONENT"
    REGION = "REGION"


class PCBConstraintItem(BaseModel):
    """Individual numerical rule with explicit provenance."""
    name: str
    value: float
    unit: str                          # "mm", "A/mm2", "°C", "mil", "count"
    source: ConstraintSource = ConstraintSource.ENGINEERING_RULE
    source_reference: Optional[str] = "Standard IPC-2221 Design Rules"
    confidence: float = 1.0
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PCBConstraint(BaseModel):
    """Complete collection of design rule limits governing layout, clearance, power, and thermal."""
    id: str = "pcb_constraint_default"
    project_id: str
    scope: ConstraintScope = ConstraintScope.GLOBAL
    target_id: Optional[str] = None    # NetClass, ComponentID, or RegionID

    # Geometric & Clearance Limits
    minimum_trace_width: PCBConstraintItem = Field(default_factory=lambda: PCBConstraintItem(name="minimum_trace_width", value=0.15, unit="mm", source=ConstraintSource.MANUFACTURING_RULE))
    minimum_clearance: PCBConstraintItem = Field(default_factory=lambda: PCBConstraintItem(name="minimum_clearance", value=0.15, unit="mm", source=ConstraintSource.MANUFACTURING_RULE))
    minimum_via_diameter: PCBConstraintItem = Field(default_factory=lambda: PCBConstraintItem(name="minimum_via_diameter", value=0.60, unit="mm", source=ConstraintSource.MANUFACTURING_RULE))
    minimum_via_drill: PCBConstraintItem = Field(default_factory=lambda: PCBConstraintItem(name="minimum_via_drill", value=0.30, unit="mm", source=ConstraintSource.MANUFACTURING_RULE))
    minimum_annular_ring: PCBConstraintItem = Field(default_factory=lambda: PCBConstraintItem(name="minimum_annular_ring", value=0.15, unit="mm", source=ConstraintSource.MANUFACTURING_RULE))
    minimum_copper_to_edge: PCBConstraintItem = Field(default_factory=lambda: PCBConstraintItem(name="minimum_copper_to_edge", value=0.30, unit="mm", source=ConstraintSource.MANUFACTURING_RULE))

    # High-Speed & Physical Limits
    maximum_trace_length: Optional[PCBConstraintItem] = None
    maximum_via_count: PCBConstraintItem = Field(default_factory=lambda: PCBConstraintItem(name="maximum_via_count", value=6.0, unit="count", source=ConstraintSource.ENGINEERING_RULE))
    maximum_current_density: PCBConstraintItem = Field(default_factory=lambda: PCBConstraintItem(name="maximum_current_density", value=35.0, unit="A/mm2", source=ConstraintSource.ENGINEERING_RULE))
    maximum_temperature: PCBConstraintItem = Field(default_factory=lambda: PCBConstraintItem(name="maximum_temperature", value=85.0, unit="°C", source=ConstraintSource.DATASHEET))
