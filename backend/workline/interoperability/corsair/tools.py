"""Corsair tool declarations and execution interfaces."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CorsairTool(BaseModel):
    """Manifest of an external tool or service available in Corsair integration suite."""
    tool_name: str
    description: str
    category: str  # "RESEARCH", "DOCS", "SIMULATION"
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)


class CorsairToolRegistry:
    """Registry of Corsair-enabled external tools and APIs."""

    def __init__(self):
        self._tools: Dict[str, CorsairTool] = {}
        self._seed_tools()

    def _seed_tools(self) -> None:
        self._tools["datasheet_synthesis"] = CorsairTool(
            tool_name="datasheet_synthesis",
            description="Extracts electrical characteristics and maximum ratings from vendor datasheets.",
            category="DOCS",
            input_schema={"type": "object", "required": ["query"]},
            output_schema={"type": "object", "required": ["summary", "references"]},
        )
        self._tools["signal_integrity_check"] = CorsairTool(
            tool_name="signal_integrity_check",
            description="Analyzes impedance matching and transmission line reflection.",
            category="SIMULATION",
            input_schema={"type": "object", "required": ["trace_geometry"]},
            output_schema={"type": "object", "required": ["characteristic_impedance", "reflections"]},
        )

    def list_tools(self) -> List[CorsairTool]:
        return list(self._tools.values())

    def get_tool(self, tool_name: str) -> Optional[CorsairTool]:
        return self._tools.get(tool_name)
