"""Internal .wlpcb format serializer and deserializer."""

import json
from typing import Optional
from backend.workline.pcb.models.project import PCBProject


class WLPCBSerializer:
    """Serializes and deserializes authoritative PCB project state to/from .wlpcb internal format."""

    @staticmethod
    def to_wlpcb_json(project: PCBProject) -> str:
        """Serialize PCBProject to .wlpcb JSON format."""
        return project.model_dump_json(indent=2)

    @staticmethod
    def from_wlpcb_json(json_str: str) -> PCBProject:
        """Parse PCBProject from .wlpcb JSON format."""
        return PCBProject.model_validate_json(json_str)
