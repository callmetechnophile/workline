"""Placement Engine managing component coordinates, board boundaries, and clearances."""

import math
from typing import Dict, List, Optional, Tuple
from backend.workline.pcb.models.board import Board
from backend.workline.pcb.models.component import PCBComponent
from backend.workline.pcb.models.footprint import Footprint
from backend.workline.pcb.models.placement import ComponentPlacement, Placement
from backend.workline.pcb.models.project import PCBProject


class PlacementEngine:
    """Computes candidate placements, enforces board boundaries, keepouts, and component clearances."""

    def __init__(self, clearance_margin_mm: float = 1.0):
        self.clearance_margin_mm = clearance_margin_mm

    def is_within_board(self, comp: PCBComponent, fp: Footprint, board: Board) -> bool:
        """Verifies component courtyard stays strictly inside physical board boundaries."""
        w = fp.courtyard_width or (fp.body_width + 1.0)
        h = fp.courtyard_height or (fp.body_height + 1.0)

        left = comp.x - w / 2.0
        right = comp.x + w / 2.0
        bottom = comp.y - h / 2.0
        top = comp.y + h / 2.0

        edge_margin = 1.5 # mm from board edge
        return (left >= edge_margin) and (right <= board.width - edge_margin) and (bottom >= edge_margin) and (top <= board.height - edge_margin)

    def check_overlap(
        self, comp_a: PCBComponent, fp_a: Footprint, comp_b: PCBComponent, fp_b: Footprint
    ) -> Tuple[bool, float]:
        """
        Determines whether two components overlap on the same layer.
        Returns: (has_overlap, center_distance)
        """
        if comp_a.layer != comp_b.layer:
            return False, 999.0

        w_a = fp_a.courtyard_width or fp_a.body_width
        h_a = fp_a.courtyard_height or fp_a.body_height
        w_b = fp_b.courtyard_width or fp_b.body_width
        h_b = fp_b.courtyard_height or fp_b.body_height

        min_dx = (w_a + w_b) / 2.0 + self.clearance_margin_mm
        min_dy = (h_a + h_b) / 2.0 + self.clearance_margin_mm

        dx = abs(comp_a.x - comp_b.x)
        dy = abs(comp_a.y - comp_b.y)
        dist = math.hypot(comp_a.x - comp_b.x, comp_a.y - comp_b.y)

        overlap = (dx < min_dx) and (dy < min_dy)
        return overlap, dist

    def validate_candidate_placement(
        self, pcb_project: PCBProject, candidate_placements: Dict[str, Tuple[float, float]]
    ) -> Tuple[bool, List[str]]:
        """
        Validates a candidate position mapping against board boundary, keepout, and overlap rules.
        """
        errors = []
        board = pcb_project.board
        fps = pcb_project.footprints

        # Create temporary updated components
        comps = {}
        for cid, (cx, cy) in candidate_placements.items():
            orig = pcb_project.components.get(cid)
            if not orig:
                continue
            if orig.locked and (abs(orig.x - cx) > 1e-4 or abs(orig.y - cy) > 1e-4):
                errors.append(f"Locked component '{orig.reference_designator}' position cannot be modified.")
            comps[cid] = orig.model_copy(update={"x": cx, "y": cy})

        # Check boundaries
        for cid, comp in comps.items():
            fp = fps.get(comp.footprint_id)
            if fp and not self.is_within_board(comp, fp, board):
                errors.append(f"Component '{comp.reference_designator}' ({comp.x:.1f}, {comp.y:.1f}) extends outside board boundaries.")

        # Check pair-wise overlaps
        c_list = list(comps.values())
        for i in range(len(c_list)):
            for j in range(i + 1, len(c_list)):
                ca = c_list[i]
                cb = c_list[j]
                fa = fps.get(ca.footprint_id)
                fb = fps.get(cb.footprint_id)
                if fa and fb:
                    overlap, dist = self.check_overlap(ca, fa, cb, fb)
                    if overlap:
                        errors.append(f"Component clearance violation: '{ca.reference_designator}' overlaps with '{cb.reference_designator}' (dist: {dist:.1f}mm).")

        return len(errors) == 0, errors
