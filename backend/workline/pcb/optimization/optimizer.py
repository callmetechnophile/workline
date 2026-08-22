"""Bounded deterministic thermal placement optimizer minimizing hotspot temperatures."""

import math
import random
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from backend.workline.pcb.models.placement import ComponentPlacement, Placement
from backend.workline.pcb.models.project import PCBProject
from backend.workline.pcb.optimization.constraints import HardConstraintChecker
from backend.workline.pcb.optimization.objective import ThermalPlacementObjective


class OptimizationStepRecord(BaseModel):
    """Log record of an individual accepted iteration during placement optimization."""
    iteration: int
    component_moved: str
    previous_position: Tuple[float, float]
    new_position: Tuple[float, float]
    peak_temperature: float
    temperature_reduction: float


class OptimizationResult(BaseModel):
    """Summary of thermal placement optimization run."""
    initial_peak_temperature: float
    optimized_peak_temperature: float
    temperature_reduction_celsius: float
    iterations_evaluated: int
    accepted_moves_count: int
    best_placements: Dict[str, Tuple[float, float]] # {component_id: (x, y)}
    history: List[OptimizationStepRecord] = Field(default_factory=list)


class ThermalPlacementOptimizer:
    """
    Optimizes component physical coordinates (x, y) to dissipate thermal hotspots,
    distribute heat-generating ICs, and strictly respect board boundaries and keepouts.
    """

    def __init__(
        self,
        objective: Optional[ThermalPlacementObjective] = None,
        max_iterations: int = 50,
        random_seed: int = 42,
    ):
        self.objective = objective or ThermalPlacementObjective()
        self.constraint_checker = HardConstraintChecker()
        self.max_iterations = max_iterations
        self.random_seed = random_seed

    def optimize(self, project: PCBProject) -> Tuple[PCBProject, OptimizationResult]:
        """
        Runs bounded deterministic optimization loop:
        Candidate Placement -> Constraint Check -> Physics Evaluation -> Accept/Reject.
        """
        random.seed(self.random_seed)

        # 1. Current State
        curr_coords = {cid: (comp.x, comp.y) for cid, comp in project.components.items()}
        curr_peak = self.objective.evaluate_cost(project, curr_coords)
        initial_peak = curr_peak

        best_coords = dict(curr_coords)
        best_peak = curr_peak

        history: List[OptimizationStepRecord] = []
        movable_comps = [c for c in project.components.values() if not c.locked]

        step_size = 4.0 # mm move step

        # Direction offsets: East, West, North, South, NE, NW, SE, SW
        directions = [
            (step_size, 0.0), (-step_size, 0.0), (0.0, step_size), (0.0, -step_size),
            (step_size * 0.7, step_size * 0.7), (-step_size * 0.7, step_size * 0.7),
            (step_size * 0.7, -step_size * 0.7), (-step_size * 0.7, -step_size * 0.7),
        ]

        iterations_count = 0

        for it in range(1, self.max_iterations + 1):
            if not movable_comps:
                break

            # Pick a component (prefer components with higher thermal dissipation)
            target = random.choice(movable_comps)
            orig_x, orig_y = best_coords[target.id]

            # Try candidate directions
            best_dir_coord = None
            best_dir_peak = best_peak

            for (dx, dy) in directions:
                iterations_count += 1
                cand_x = round(orig_x + dx, 2)
                cand_y = round(orig_y + dy, 2)

                test_coords = dict(best_coords)
                test_coords[target.id] = (cand_x, cand_y)

                # Hard constraint check (board boundaries & no overlaps)
                is_valid, _ = self.constraint_checker.is_valid_candidate(project, test_coords)
                if not is_valid:
                    continue

                # Physics thermal evaluation
                cand_peak = self.objective.evaluate_cost(project, test_coords)
                if cand_peak < best_dir_peak:
                    best_dir_peak = cand_peak
                    best_dir_coord = (cand_x, cand_y)

            # If an improving move was found, accept it
            if best_dir_coord and best_dir_peak < best_peak:
                red = round(best_peak - best_dir_peak, 2)
                history.append(
                    OptimizationStepRecord(
                        iteration=it,
                        component_moved=target.reference_designator,
                        previous_position=(orig_x, orig_y),
                        new_position=best_dir_coord,
                        peak_temperature=round(best_dir_peak, 2),
                        temperature_reduction=red,
                    )
                )
                best_coords[target.id] = best_dir_coord
                best_peak = best_dir_peak

        # 2. Update project with optimized placements
        updated_comps = {}
        updated_placements = {}
        for cid, comp in project.components.items():
            bx, by = best_coords[cid]
            updated_comps[cid] = comp.model_copy(update={"x": bx, "y": by})
            updated_placements[cid] = ComponentPlacement(
                component_id=cid,
                reference_designator=comp.reference_designator,
                x=bx,
                y=by,
                locked=comp.locked,
            )

        updated_project = project.model_copy(
            update={
                "components": updated_comps,
                "placement": Placement(placements=updated_placements, zones=project.placement.zones, version=project.placement.version + 1),
            }
        )

        res = OptimizationResult(
            initial_peak_temperature=round(initial_peak, 2),
            optimized_peak_temperature=round(best_peak, 2),
            temperature_reduction_celsius=round(initial_peak - best_peak, 2),
            iterations_evaluated=iterations_count,
            accepted_moves_count=len(history),
            best_placements=best_coords,
            history=history,
        )

        return updated_project, res
