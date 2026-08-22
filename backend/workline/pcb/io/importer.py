"""Abstract PCB Importer interface for future EDA interoperability."""

from abc import ABC, abstractmethod
from typing import Any, Dict
from backend.workline.pcb.models.project import PCBProject


class PCBImporter(ABC):
    """Abstract interface for importing external EDA projects (KiCad, Altium, IPC-2581, ODB++)."""

    @property
    @abstractmethod
    def format_name(self) -> str:
        pass

    @abstractmethod
    def import_project(self, file_path_or_content: Any) -> PCBProject:
        """Parse external file and produce canonical PCBProject."""
        pass
