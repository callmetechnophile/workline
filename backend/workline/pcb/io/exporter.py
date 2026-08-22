"""Abstract PCB Exporter interface for future EDA interoperability."""

from abc import ABC, abstractmethod
from typing import Any
from backend.workline.pcb.models.project import PCBProject


class PCBExporter(ABC):
    """Abstract interface for exporting to external CAD / manufacturing formats (KiCad, Altium, IPC-2581, Gerber)."""

    @property
    @abstractmethod
    def format_name(self) -> str:
        pass

    @abstractmethod
    def export_project(self, project: PCBProject) -> Any:
        """Export canonical PCBProject to target format."""
        pass
