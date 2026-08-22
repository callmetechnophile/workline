"""Technical visualization schemas for Paper Banana."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class DiagramNode(BaseModel):
    """Component node in a technical visual diagram."""
    id: str
    label: str
    category: str = "service"
    technology: Optional[str] = None


class DiagramEdge(BaseModel):
    """Connection or data-flow between diagram nodes."""
    source: str
    target: str
    protocol: Optional[str] = None
    label: Optional[str] = None


class TechnicalDiagramSpec(BaseModel):
    """Structured specification of a technical visualization."""
    title: str
    style: str = "blueprint_vector"
    aspect_ratio: str = "16:9"
    theme: str = "dark_engineering"
    nodes: List[DiagramNode] = Field(default_factory=list)
    edges: List[DiagramEdge] = Field(default_factory=list)
    layers: List[str] = Field(default_factory=list)
