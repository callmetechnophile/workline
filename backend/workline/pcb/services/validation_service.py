"""PCB Validation Service for design rule and integrity verification."""

from typing import Optional
from backend.workline.pcb.engine.validation import PCBValidationReport, PCBValidator
from backend.workline.pcb.models.project import PCBProject
from backend.workline.pcb.services.pcb_service import PCBService, pcb_service


class PCBValidationService:
    """Coordinates execution of the 12 PCB structural, electrical, and thermal validation rules."""

    def __init__(self, pcb_svc: Optional[PCBService] = None):
        self.pcb_svc = pcb_svc or pcb_service
        self.validator = PCBValidator()

    async def validate_pcb_project(self, project_id: str) -> PCBValidationReport:
        """Runs full validation on a PCB project and returns structured report."""
        proj = await self.pcb_svc.get_pcb_project(project_id)
        if not proj:
            raise ValueError(f"PCB project '{project_id}' not found.")
        return self.validator.validate_project(proj)


# Global singleton validation service
pcb_validation_service = PCBValidationService()
