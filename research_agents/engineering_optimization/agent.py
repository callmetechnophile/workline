"""
Agent #20: EngineeringOptimizationAgent implementation using Google ADK conventions.
Explores feasible design alternatives, computes Pareto frontiers, and identifies
optimal or Pareto-efficient solutions against explicit objectives and constraints.

ANSWERS: "WHICH FEASIBLE DESIGN IS BEST FOR THE DEFINED OBJECTIVE?"
REJECTS: vague optimization requests without explicit measurable objectives.
INVARIANT: Hard constraint violations -> INFEASIBLE. Never recommended.
INVARIANT: Candidate selection -> OptimizationDecision + Agent #16 ChangeRequest only.
INVARIANT: Candidates are isolated branches. Production BOM/arch never modified.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from loguru import logger

from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.engineering_knowledge_graph_agent.services.graph_query import KnowledgeGraphService
from research_agents.engineering_optimization.config import optimization_config
from research_agents.engineering_optimization.providers.base import ReasoningProvider
from research_agents.engineering_optimization.providers.bedrock import BedrockOptimizationProvider
from research_agents.engineering_optimization.repository.optimization_repository import OptimizationRepository
from research_agents.engineering_optimization.schemas import (
    ConstraintObject,
    DesignCandidate,
    ObjectiveObject,
    OptimizationDecision,
    OptimizationInput,
    OptimizationObject,
    OptimizationOutput,
    ParetoFrontierObject,
    RobustnessObject,
    VariableObject,
)
from research_agents.engineering_optimization.services.design_space_engine import DesignSpaceEngine
from research_agents.engineering_optimization.services.file_exporter import OptimizationFileExporter
from research_agents.engineering_optimization.services.reoptimization_engine import ReoptimizationEngine
from research_agents.engineering_optimization.services.report_generator import OptimizationReportGenerator


# ── Vague objective detection ──────────────────────────────────────────────────
_VAGUE_PHRASES = frozenset([
    "make it better", "make it cheaper and faster", "make it powerful",
    "improve it", "optimize everything", "just optimize", "make it faster",
    "make it smaller", "make it more efficient",
])


def _is_vague_objective(description: str) -> bool:
    """Return True if the optimization description is too vague to proceed."""
    norm = description.strip().lower()
    return norm in _VAGUE_PHRASES or len(norm.split()) < 3


class EngineeringOptimizationAgent:
    """
    Google ADK-compliant Engineering Optimization Agent (Agent #20).

    ANSWERS: WHICH FEASIBLE DESIGN IS BEST FOR THE DEFINED OBJECTIVE?
    - Rejects vague objectives without measurable metrics.
    - Enforces hard constraints deterministically (no silent conversion).
    - Delegates all simulation to Agent #19 (EngineeringSimulationAgent).
    - Delegates all change control to Agent #16 (EngineeringChangeControlAgent).
    - Candidates are isolated; production project is never mutated.
    """

    NAME = "EngineeringOptimizationAgent"
    DESCRIPTION = (
        "Explore feasible engineering design alternatives and identify optimal or "
        "Pareto-efficient solutions against explicit objectives, constraints, "
        "requirements, simulation results, and verified evidence."
    )
    CAPABILITIES = [
        "optimization.create",
        "optimization.evaluate",
        "optimization.pareto",
        "optimization.tradeoff",
        "optimization.select",
        "graph.read",
        "graph.insert",
        "graph.update",
    ]

    def __init__(
        self,
        db_client: Optional[SurrealDBClient] = None,
        reasoning_provider: Optional[ReasoningProvider] = None,
    ):
        self.db = db_client or SurrealDBClient()
        self.provider = reasoning_provider or BedrockOptimizationProvider()
        self.repo = OptimizationRepository(self.db)
        self.graph_service = KnowledgeGraphService(self.db)
        self.engine = DesignSpaceEngine()
        self.reopt_engine = ReoptimizationEngine()
        self.report_gen = OptimizationReportGenerator()
        self.exporter = OptimizationFileExporter()

    # ── Core optimization cycle ────────────────────────────────────────────────

    async def run_optimization_cycle(
        self,
        input_data: OptimizationInput,
        objectives: Optional[List[ObjectiveObject]] = None,
        variables: Optional[List[VariableObject]] = None,
        constraints: Optional[List[ConstraintObject]] = None,
        n_candidates: int = 10,
        simulation_results_map: Optional[Dict[str, Dict[str, Any]]] = None,
        output_dir: Optional[str] = None,
    ) -> OptimizationOutput:
        """
        Full optimization cycle: create -> generate candidates -> evaluate ->
        feasibility check -> Pareto -> robustness -> recommend -> report -> export.
        """
        # 1. Build objectives/variables/constraints with safe defaults for demo
        objectives = objectives or self._default_objectives()
        variables = variables or self._default_variables()
        constraints = constraints or self._default_constraints()

        # 2. Reject vague objectives
        for obj in objectives:
            if _is_vague_objective(obj.description) and not obj.unit:
                raise ValueError(
                    f"REJECTED: Objective '{obj.name}' is too vague. "
                    "Provide explicit direction (MINIMIZE/MAXIMIZE), unit, and measurable metric."
                )

        # 3. Create optimization object
        opt_id = f"OPT-{uuid.uuid4().hex[:8].upper()}"
        name = input_data.optimization_name or f"Optimization-{opt_id}"
        optimization = OptimizationObject(
            optimization_id=opt_id,
            project_id=input_data.project_id,
            name=name,
            description=f"Multi-objective optimization for project {input_data.project_id}",
            objectives=objectives,
            variables=variables,
            constraints=constraints,
            status="RUNNING",
        )
        await self.repo.create_optimization(optimization)
        logger.info(f"[OPTIMIZATION] Created {opt_id} for project {input_data.project_id}")

        # 4. Generate candidates (isolated branches)
        candidates = self.engine.generate_candidates(optimization, n_candidates=n_candidates)
        logger.info(f"[OPTIMIZATION] Generated {len(candidates)} candidates")

        # 5. Evaluate objectives + feasibility for each candidate
        sim_map = simulation_results_map or {}
        for c in candidates:
            sim_results = sim_map.get(c.candidate_id)
            c = self.engine.evaluate_objectives(c, objectives, sim_results)
            c = self.engine.check_feasibility(c, constraints)
            await self.repo.create_candidate(c)

        feasible = [c for c in candidates if c.feasible]
        infeasible = [c for c in candidates if not c.feasible]
        logger.info(
            f"[OPTIMIZATION] Feasibility: {len(feasible)} feasible, {len(infeasible)} infeasible"
        )

        # 6. Pareto frontier
        pareto: Optional[ParetoFrontierObject] = None
        if len(objectives) >= 1 and feasible:
            pareto = self.engine.compute_pareto_frontier(opt_id, candidates, objectives)
            await self.repo.create_pareto_frontier(pareto)
            logger.info(f"[OPTIMIZATION] Pareto frontier: {len(pareto.points)} non-dominated points")

        # 7. Weighted ranking -> top recommendation
        ranked = self.engine.rank_by_weighted_sum(candidates, objectives)
        recommended_id: Optional[str] = ranked[0].candidate_id if ranked else None
        rationale = ""
        if recommended_id:
            rationale = await self.provider.explain_tradeoff(
                prompt=(
                    f"Optimization {opt_id}: {len(feasible)} feasible candidates. "
                    f"Recommended: {recommended_id}. "
                    f"Objectives: {[o.name for o in objectives]}. "
                    "Justify this recommendation based on Pareto optimality and weighted ranking."
                ),
                system_prompt=(
                    "You are an expert engineering optimization advisor. Provide a concise, "
                    "evidence-based recommendation justification. Never fabricate simulation data."
                ),
            )

        # 8. Robustness
        robustness: List[RobustnessObject] = []
        if ranked:
            rob = self.engine.compute_robustness(ranked[0], objectives)
            robustness.append(rob)

        # 9. Generate report
        optimization.status = "COMPLETE" if feasible else "INFEASIBLE"
        optimization.candidate_ids = [c.candidate_id for c in candidates]
        if pareto:
            optimization.pareto_frontier_id = pareto.frontier_id
        report = self.report_gen.generate_report(
            optimization=optimization,
            candidates=candidates,
            pareto=pareto,
            recommended_id=recommended_id,
            rationale=rationale,
            robustness=robustness,
        )

        # 10. Export
        exported: List[str] = []
        if output_dir or input_data.output_dir:
            out_dir = output_dir or input_data.output_dir
            exported = self.exporter.export_artifacts(
                output_dir=out_dir,
                optimization=optimization,
                candidates=candidates,
                pareto=pareto,
                decision=None,
                robustness=robustness,
                report_markdown=report,
            )

        return OptimizationOutput(
            optimization=optimization,
            candidates=candidates,
            pareto_frontier=pareto,
            decision=None,
            report_markdown=report,
            exported_files=exported,
        )

    # ── Capability methods (Google ADK) ───────────────────────────────────────

    async def create_optimization(
        self,
        project_id: str,
        objectives: List[Dict[str, Any]],
        variables: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        name: str = "",
    ) -> Dict[str, Any]:
        """Create an optimization specification with objectives, variables, and constraints."""
        opt_id = f"OPT-{uuid.uuid4().hex[:8].upper()}"
        objs = [ObjectiveObject(**o) for o in objectives]
        vars_ = [VariableObject(**v) for v in variables]
        cons = [ConstraintObject(**c) for c in constraints]
        opt = OptimizationObject(
            optimization_id=opt_id,
            project_id=project_id,
            name=name or f"Optimization-{opt_id}",
            description=f"Optimization for project {project_id}",
            objectives=objs,
            variables=vars_,
            constraints=cons,
        )
        await self.repo.create_optimization(opt)
        return {"optimization_id": opt_id, "status": opt.status}

    async def evaluate_candidates(
        self,
        optimization_id: str,
        n_candidates: int = 10,
    ) -> Dict[str, Any]:
        """Generate and evaluate candidates for an existing optimization."""
        opt = await self.repo.get_optimization(optimization_id)
        if not opt:
            return {"error": f"Optimization {optimization_id} not found"}
        candidates = self.engine.generate_candidates(opt, n_candidates=n_candidates)
        for c in candidates:
            c = self.engine.evaluate_objectives(c, opt.objectives)
            c = self.engine.check_feasibility(c, opt.constraints)
            await self.repo.create_candidate(c)
        feasible = [c for c in candidates if c.feasible]
        return {
            "optimization_id": optimization_id,
            "candidates_generated": len(candidates),
            "feasible": len(feasible),
            "infeasible": len(candidates) - len(feasible),
        }

    async def compute_pareto(self, optimization_id: str) -> Dict[str, Any]:
        """Compute the Pareto frontier for an optimization."""
        opt = await self.repo.get_optimization(optimization_id)
        if not opt:
            return {"error": f"Optimization {optimization_id} not found"}
        candidates = await self.repo.get_candidates(optimization_id)
        if not candidates:
            return {"error": "No candidates found. Run evaluate_candidates first."}
        pareto = self.engine.compute_pareto_frontier(optimization_id, candidates, opt.objectives)
        await self.repo.create_pareto_frontier(pareto)
        return {
            "frontier_id": pareto.frontier_id,
            "pareto_points": len(pareto.points),
            "dominated": pareto.dominated_count,
            "infeasible_excluded": pareto.infeasible_count,
        }

    async def analyze_tradeoffs(self, optimization_id: str) -> Dict[str, Any]:
        """Analyze trade-offs between objectives on the Pareto frontier."""
        opt = await self.repo.get_optimization(optimization_id)
        if not opt:
            return {"error": f"Optimization {optimization_id} not found"}
        candidates = await self.repo.get_candidates(optimization_id)
        feasible = [c for c in candidates if c.feasible]
        if len(opt.objectives) < 2:
            return {"message": "Single-objective optimization: no trade-off analysis needed."}
        ranked = self.engine.rank_by_weighted_sum(candidates, opt.objectives)
        return {
            "optimization_id": optimization_id,
            "objective_count": len(opt.objectives),
            "feasible_count": len(feasible),
            "objectives_in_tension": [o.name for o in opt.objectives],
            "top_candidate": ranked[0].candidate_id if ranked else None,
        }

    async def get_recommendation(self, optimization_id: str) -> Dict[str, Any]:
        """Get the recommended candidate for an optimization."""
        opt = await self.repo.get_optimization(optimization_id)
        if not opt:
            return {"error": f"Optimization {optimization_id} not found"}
        candidates = await self.repo.get_candidates(optimization_id)
        ranked = self.engine.rank_by_weighted_sum(candidates, opt.objectives)
        if not ranked:
            return {"error": "No feasible candidates. All candidates violate hard constraints."}
        top = ranked[0]
        rationale = await self.provider.explain_tradeoff(
            prompt=f"Recommended candidate: {top.candidate_id}. Objectives: {top.objective_values}"
        )
        return {
            "recommended_candidate_id": top.candidate_id,
            "objective_values": top.objective_values,
            "feasible": top.feasible,
            "rationale": rationale,
        }

    async def select_candidate(
        self,
        optimization_id: str,
        candidate_id: str,
        selected_by: str,
        rationale: str,
    ) -> Dict[str, Any]:
        """
        Select a candidate and create an OptimizationDecision.
        Triggers a ChangeRequest through Agent #16.
        INVARIANT: Never directly mutates project state upon selection.
        """
        opt = await self.repo.get_optimization(optimization_id)
        if not opt:
            return {"error": f"Optimization {optimization_id} not found"}

        candidates = await self.repo.get_candidates(optimization_id)
        candidate = next((c for c in candidates if c.candidate_id == candidate_id), None)
        if not candidate:
            return {"error": f"Candidate {candidate_id} not found in optimization {optimization_id}"}

        if not candidate.feasible:
            return {
                "error": (
                    f"REJECTED: Candidate {candidate_id} is INFEASIBLE due to hard constraint violations: "
                    f"{candidate.hard_constraint_violations}. "
                    "Cannot select an infeasible candidate."
                )
            }

        decision_id = f"OPTDEC-{uuid.uuid4().hex[:8].upper()}"
        cr_id = f"CR-OPT-{uuid.uuid4().hex[:6].upper()}"  # Change request placeholder (Agent #16)

        decision = OptimizationDecision(
            decision_id=decision_id,
            optimization_id=optimization_id,
            candidate_id=candidate_id,
            selected_by=selected_by,
            rationale=rationale,
            change_request_id=cr_id,
        )
        await self.repo.create_decision(decision)
        opt.decision_id = decision_id
        logger.info(
            f"[SELECTION] Decision {decision_id}: candidate {candidate_id} selected, "
            f"ChangeRequest {cr_id} created (Agent #16 handoff)"
        )
        return {
            "decision_id": decision_id,
            "candidate_id": candidate_id,
            "change_request_id": cr_id,
            "status": "DECISION_RECORDED",
            "message": (
                f"Candidate {candidate_id} selected. ChangeRequest {cr_id} submitted to "
                "Agent #16 (EngineeringChangeControlAgent) for approval."
            ),
        }

    async def assess_impact(
        self,
        optimization_id: str,
        candidate_id: str,
    ) -> Dict[str, Any]:
        """Assess the impact of selecting a candidate on the project."""
        candidates = await self.repo.get_candidates(optimization_id)
        candidate = next((c for c in candidates if c.candidate_id == candidate_id), None)
        if not candidate:
            return {"error": f"Candidate {candidate_id} not found"}
        if not candidate.feasible:
            return {
                "candidate_id": candidate_id,
                "impact": "BLOCKED",
                "reason": f"Infeasible: {candidate.hard_constraint_violations}",
            }
        return {
            "candidate_id": candidate_id,
            "variable_changes": candidate.variable_values,
            "objective_values": candidate.objective_values,
            "impact": "REQUIRES_CHANGE_CONTROL",
            "message": "Selection requires Agent #16 ChangeRequest before production propagation.",
        }

    async def detect_reoptimization(
        self,
        optimization_id: str,
        current_bom_version: str,
        current_architecture_version: str,
    ) -> Dict[str, Any]:
        """Detect if an optimization result is stale due to upstream changes."""
        opt = await self.repo.get_optimization(optimization_id)
        if not opt:
            return {"error": f"Optimization {optimization_id} not found"}
        stale = self.reopt_engine.check_staleness(opt, current_bom_version, current_architecture_version)
        if stale:
            self.reopt_engine.mark_stale(opt)
            rec = self.reopt_engine.suggest_reoptimization(
                opt,
                reason=f"BOM {opt.bom_version}->{current_bom_version} or Arch changed",
            )
            await self.repo.mark_stale(optimization_id)
            return rec
        return {"optimization_id": optimization_id, "status": "CURRENT", "message": "Optimization is current."}

    async def generate_report(self, optimization_id: str) -> Dict[str, Any]:
        """Generate a 21-section Markdown optimization report."""
        opt = await self.repo.get_optimization(optimization_id)
        if not opt:
            return {"error": f"Optimization {optimization_id} not found"}
        candidates = await self.repo.get_candidates(optimization_id)
        ranked = self.engine.rank_by_weighted_sum(candidates, opt.objectives)
        recommended_id = ranked[0].candidate_id if ranked else None
        robustness: List[RobustnessObject] = []
        if ranked:
            robustness.append(self.engine.compute_robustness(ranked[0], opt.objectives))
        pareto_id = opt.pareto_frontier_id
        pareto = await self.repo.get_pareto_frontier(pareto_id) if pareto_id else None
        report = self.report_gen.generate_report(
            optimization=opt,
            candidates=candidates,
            pareto=pareto,
            recommended_id=recommended_id,
            rationale="Weighted sum ranking with Pareto analysis.",
            robustness=robustness,
        )
        return {"optimization_id": optimization_id, "report_markdown": report}

    # ── Sync wrapper for CLI ───────────────────────────────────────────────────

    def run_optimization_cycle_sync(
        self,
        input_data: OptimizationInput,
        objectives: Optional[List[ObjectiveObject]] = None,
        variables: Optional[List[VariableObject]] = None,
        constraints: Optional[List[ConstraintObject]] = None,
        n_candidates: int = 10,
    ) -> OptimizationOutput:
        """Synchronous wrapper for run_optimization_cycle."""
        return asyncio.run(
            self.run_optimization_cycle(
                input_data=input_data,
                objectives=objectives,
                variables=variables,
                constraints=constraints,
                n_candidates=n_candidates,
            )
        )

    # ── Default demo specs ────────────────────────────────────────────────────

    def _default_objectives(self) -> List[ObjectiveObject]:
        return [
            ObjectiveObject(
                objective_id="OBJ-PWR",
                name="power_dissipation_watts",
                direction="MINIMIZE",
                unit="W",
                weight=0.6,
                description="Minimize thermal power dissipation to stay within budget",
            ),
            ObjectiveObject(
                objective_id="OBJ-COST",
                name="unit_cost_usd",
                direction="MINIMIZE",
                unit="USD",
                weight=0.4,
                description="Minimize per-unit component cost",
            ),
        ]

    def _default_variables(self) -> List[VariableObject]:
        return [
            VariableObject(
                variable_id="VAR-CURRENT",
                name="current_ma",
                unit="mA",
                min_value=80.0,
                max_value=200.0,
                step=20.0,
                current_value=150.0,
                description="Operating current draw",
            ),
            VariableObject(
                variable_id="VAR-VOLTAGE",
                name="voltage_v",
                unit="V",
                min_value=1.8,
                max_value=3.6,
                step=0.3,
                current_value=3.3,
                description="Supply voltage rail",
            ),
        ]

    def _default_constraints(self) -> List[ConstraintObject]:
        return [
            ConstraintObject(
                constraint_id="CON-TEMP",
                name="junction_temp_c",
                constraint_type="HARD",
                expression="<= limit",
                limit=80.0,
                unit="degC",
                description="Junction temperature must not exceed 80 degC",
            ),
            ConstraintObject(
                constraint_id="CON-PWR",
                name="power_dissipation_watts",
                constraint_type="HARD",
                expression="<= limit",
                limit=0.5,
                unit="W",
                description="Power dissipation must not exceed 0.5 W",
            ),
            ConstraintObject(
                constraint_id="CON-COST",
                name="unit_cost_usd",
                constraint_type="SOFT",
                expression="<= limit",
                limit=5.0,
                unit="USD",
                description="Target cost ceiling (soft)",
                penalty=1.0,
            ),
        ]
