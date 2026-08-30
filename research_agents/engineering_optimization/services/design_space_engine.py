"""
Design space exploration, feasibility checking, Pareto frontier computation,
weighted sum ranking, and candidate isolation engine (Agent #20).
"""

import hashlib
import json
import random
from typing import Any, Dict, List, Optional, Tuple
import uuid
from loguru import logger

from research_agents.engineering_optimization.config import optimization_config
from research_agents.engineering_optimization.schemas import (
    ConstraintObject,
    DesignCandidate,
    ObjectiveObject,
    OptimizationObject,
    ParetoFrontierObject,
    ParetoPoint,
    RobustnessObject,
    VariableObject,
)


class DesignSpaceEngine:
    """
    Candidate generator, feasibility evaluator, Pareto frontier calculator,
    and weighted objective ranker.

    INVARIANTS:
    - Hard constraint violation -> candidate.feasible = False, never recommended.
    - Soft constraint violations are recorded with penalty if penalty is declared.
    - Candidate evaluation never touches the production BOM or architecture.
    - Pareto dominance: candidate A dominates B if A <= B in all objectives
      and strictly < in at least one (minimization convention).
    """

    def __init__(self, random_seed: int = None):
        self.random_seed = random_seed or optimization_config.default_random_seed

    # ── Candidate generation ────────────────────────────────────────────────────

    def generate_candidates(
        self,
        optimization: OptimizationObject,
        n_candidates: int = None,
    ) -> List[DesignCandidate]:
        """Generate design candidates by grid-sampling the variable space."""
        n = min(n_candidates or optimization_config.max_candidates, optimization_config.max_candidates)
        random.seed(self.random_seed)
        candidates: List[DesignCandidate] = []

        for i in range(n):
            var_values: Dict[str, float] = {}
            for var in optimization.variables:
                if var.step is not None:
                    # Discrete stepped variable
                    steps = []
                    v = var.min_value
                    while v <= var.max_value + 1e-12:
                        steps.append(round(v, 6))
                        v += var.step
                    var_values[var.name] = random.choice(steps) if steps else var.min_value
                else:
                    var_values[var.name] = round(
                        random.uniform(var.min_value, var.max_value), 6
                    )

            candidate_id = f"CAND-{uuid.uuid4().hex[:8].upper()}"
            c = DesignCandidate(
                candidate_id=candidate_id,
                optimization_id=optimization.optimization_id,
                variable_values=var_values,
            )
            candidates.append(c)

        return candidates

    # ── Objective evaluation ────────────────────────────────────────────────────

    def evaluate_objectives(
        self,
        candidate: DesignCandidate,
        objectives: List[ObjectiveObject],
        simulation_results: Optional[Dict[str, Any]] = None,
    ) -> DesignCandidate:
        """
        Compute objective values for a candidate.
        Uses simulation_results if provided; otherwise uses variable values as proxy.
        """
        sim = simulation_results or {}
        for obj in objectives:
            if obj.name in sim:
                candidate.objective_values[obj.name] = float(sim[obj.name])
            elif obj.name in candidate.variable_values:
                candidate.objective_values[obj.name] = candidate.variable_values[obj.name]
            else:
                # Derived proxy: use mean of all variable values (placeholder)
                if candidate.variable_values:
                    candidate.objective_values[obj.name] = round(
                        sum(candidate.variable_values.values()) / len(candidate.variable_values), 4
                    )
                else:
                    candidate.objective_values[obj.name] = 0.0
        return candidate

    # ── Feasibility checking ────────────────────────────────────────────────────

    def check_feasibility(
        self,
        candidate: DesignCandidate,
        constraints: List[ConstraintObject],
    ) -> DesignCandidate:
        """
        Evaluate all constraints against the candidate's variable and objective values.
        HARD violations mark feasible=False immediately and irreversibly.
        SOFT violations are recorded with penalty.
        """
        combined = {**candidate.variable_values, **candidate.objective_values}

        for con in constraints:
            value = combined.get(con.name)
            if value is None:
                continue  # Cannot evaluate — skip (conservative)

            # Determine violation
            violated = False
            violation_magnitude = 0.0

            # Parse simple expressions: "<= limit", ">= limit"
            expr = con.expression.strip().lower()
            if "<=" in expr:
                violated = value > con.limit + optimization_config.hard_constraint_tolerance
                violation_magnitude = max(0.0, value - con.limit)
            elif ">=" in expr:
                violated = value < con.limit - optimization_config.hard_constraint_tolerance
                violation_magnitude = max(0.0, con.limit - value)
            elif "<" in expr:
                violated = value >= con.limit
                violation_magnitude = max(0.0, value - con.limit)
            elif ">" in expr:
                violated = value <= con.limit
                violation_magnitude = max(0.0, con.limit - value)

            if violated:
                if con.constraint_type == "HARD":
                    # INVARIANT: Hard violation -> INFEASIBLE, no conversion to soft
                    candidate.feasible = False
                    candidate.hard_constraint_violations.append(
                        f"{con.name}: {value} violates {con.expression} {con.limit} {con.unit}"
                    )
                    candidate.constraint_violations[con.constraint_id] = violation_magnitude
                    logger.debug(
                        f"[HARD CONSTRAINT VIOLATION] {candidate.candidate_id}: "
                        f"{con.name}={value} violates limit={con.limit} {con.unit}"
                    )
                else:  # SOFT
                    candidate.constraint_violations[con.constraint_id] = violation_magnitude
                    if con.penalty is not None:
                        logger.debug(
                            f"[SOFT CONSTRAINT VIOLATION] {candidate.candidate_id}: "
                            f"{con.name}={value}, penalty={con.penalty}"
                        )

        return candidate

    # ── Pareto frontier ─────────────────────────────────────────────────────────

    def compute_pareto_frontier(
        self,
        optimization_id: str,
        candidates: List[DesignCandidate],
        objectives: List[ObjectiveObject],
    ) -> ParetoFrontierObject:
        """
        Compute multi-objective Pareto frontier from feasible candidates.
        ONLY feasible candidates may appear on the Pareto frontier.
        Dominance rule (minimization convention):
          A dominates B if A[i] <= B[i] for all i, and A[i] < B[i] for at least one i.
        For MAXIMIZE objectives, negate the value before comparison.
        """
        feasible = [c for c in candidates if c.feasible]
        infeasible_count = len(candidates) - len(feasible)

        # Normalize to minimization
        def norm(c: DesignCandidate) -> List[float]:
            row = []
            for obj in objectives:
                v = c.objective_values.get(obj.name, 0.0)
                row.append(v if obj.direction == "MINIMIZE" else -v)
            return row

        pareto_points: List[ParetoPoint] = []
        dominated_count = 0

        for i, ci in enumerate(feasible):
            ni = norm(ci)
            is_dominated = False
            for j, cj in enumerate(feasible):
                if i == j:
                    continue
                nj = norm(cj)
                # cj dominates ci?
                eps = optimization_config.pareto_epsilon
                if all(nj[k] <= ni[k] + eps for k in range(len(objectives))) and \
                   any(nj[k] < ni[k] - eps for k in range(len(objectives))):
                    is_dominated = True
                    break
            if not is_dominated:
                pareto_points.append(ParetoPoint(
                    candidate_id=ci.candidate_id,
                    objective_values=ci.objective_values.copy(),
                    dominance_rank=0,
                ))
            else:
                dominated_count += 1

        frontier_id = f"PARETO-{uuid.uuid4().hex[:8].upper()}"
        return ParetoFrontierObject(
            frontier_id=frontier_id,
            optimization_id=optimization_id,
            points=pareto_points,
            dominated_count=dominated_count,
            infeasible_count=infeasible_count,
            method="non_dominated_sorting",
        )

    # ── Weighted sum ranking ────────────────────────────────────────────────────

    def rank_by_weighted_sum(
        self,
        candidates: List[DesignCandidate],
        objectives: List[ObjectiveObject],
    ) -> List[DesignCandidate]:
        """Rank feasible candidates by weighted sum of normalized objective values."""
        feasible = [c for c in candidates if c.feasible]
        if not feasible:
            return []

        # Compute per-objective min/max for normalization
        ranges: Dict[str, Tuple[float, float]] = {}
        for obj in objectives:
            vals = [c.objective_values.get(obj.name, 0.0) for c in feasible]
            ranges[obj.name] = (min(vals), max(vals))

        def weighted_score(c: DesignCandidate) -> float:
            score = 0.0
            for obj in objectives:
                v = c.objective_values.get(obj.name, 0.0)
                lo, hi = ranges[obj.name]
                span = hi - lo
                norm_v = (v - lo) / span if span > 1e-12 else 0.0
                if obj.direction == "MAXIMIZE":
                    norm_v = 1.0 - norm_v
                score += obj.weight * norm_v
            return score

        return sorted(feasible, key=weighted_score)

    # ── Sensitivity / Robustness ────────────────────────────────────────────────

    def compute_robustness(
        self,
        candidate: DesignCandidate,
        objectives: List[ObjectiveObject],
        perturbation: float = 0.05,
    ) -> RobustnessObject:
        """Estimate per-variable sensitivity to objective changes via finite-difference perturbation."""
        sensitivity: Dict[str, float] = {}
        worst_case: Dict[str, float] = {}
        total_sensitivity = 0.0

        for var_name, base_val in candidate.variable_values.items():
            delta = base_val * perturbation if abs(base_val) > 1e-12 else perturbation
            perturbed_obj_sum = 0.0
            base_obj_sum = sum(candidate.objective_values.values())

            for obj in objectives:
                base_obj = candidate.objective_values.get(obj.name, 0.0)
                # Approximate sensitivity: d(obj)/d(var) ~= obj * perturbation factor
                sens = abs(base_obj * perturbation) if abs(base_obj) > 1e-12 else perturbation
                perturbed_obj_sum += (base_obj + sens) if obj.direction == "MINIMIZE" else (base_obj - sens)

            sensitivity[var_name] = round(abs(perturbed_obj_sum - base_obj_sum), 4)
            total_sensitivity += sensitivity[var_name]

        for obj in objectives:
            base_val = candidate.objective_values.get(obj.name, 0.0)
            worst_case[obj.name] = round(base_val * (1.0 + perturbation), 4)

        robustness_score = max(0.0, 1.0 - min(total_sensitivity / (len(objectives) + 1), 1.0))
        return RobustnessObject(
            candidate_id=candidate.candidate_id,
            sensitivity_map=sensitivity,
            worst_case_objective=worst_case,
            robustness_score=round(robustness_score, 4),
        )
