"""Hard geometric constraints for placement optimization."""

from typing import Dict, List, Tuple
from backend.workline.pcb.engine.placement import PlacementEngine
from backend.workline.pcb.models.project import PCBProject


class HardConstraintChecker:
    """Strictly guarantees that no candidate optimization placement violates physical design rules."""

    def __init__(self):
        self.placement_engine = PlacementEngine()

    def is_valid_candidate(
        self, project: PCBProject, candidate_coords: Dict[str, Tuple[float, float]]
    ) -> Tuple[bool, List[str]]:
        """Returns True only if all components stay inside board boundaries and have no overlaps."""
        return self.placement_engine.validate_candidate_placement(project, candidate_coords)
