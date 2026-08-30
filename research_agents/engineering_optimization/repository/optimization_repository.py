"""
SurrealDB repository for optimization runs, candidates, Pareto frontiers, and decisions.
"""

from typing import Any, Dict, List, Optional
from loguru import logger
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.engineering_optimization.schemas import (
    DesignCandidate,
    OptimizationDecision,
    OptimizationObject,
    ParetoFrontierObject,
)


class OptimizationRepository:
    """SurrealDB graph access repository for optimization data."""

    def __init__(self, db_client: Optional[SurrealDBClient] = None):
        self.db = db_client or SurrealDBClient()
        self._memory_opts: Dict[str, OptimizationObject] = {}
        self._memory_candidates: Dict[str, DesignCandidate] = {}
        self._memory_pareto: Dict[str, ParetoFrontierObject] = {}
        self._memory_decisions: Dict[str, OptimizationDecision] = {}

    async def create_optimization(self, opt: OptimizationObject) -> OptimizationObject:
        try:
            await self.db.create_node("optimization", opt.optimization_id, opt.model_dump())
            await self.db.relate_nodes(
                f"project:{opt.project_id}", "has_optimization", f"optimization:{opt.optimization_id}"
            )
        except Exception as e:
            logger.warning(f"SurrealDB create_optimization fallback: {e}")
        self._memory_opts[opt.optimization_id] = opt
        return opt

    async def create_candidate(self, candidate: DesignCandidate) -> DesignCandidate:
        try:
            await self.db.create_node("candidate", candidate.candidate_id, candidate.model_dump())
            await self.db.relate_nodes(
                f"optimization:{candidate.optimization_id}",
                "evaluates_candidate",
                f"candidate:{candidate.candidate_id}",
            )
        except Exception as e:
            logger.warning(f"SurrealDB create_candidate fallback: {e}")
        self._memory_candidates[candidate.candidate_id] = candidate
        return candidate

    async def create_pareto_frontier(self, frontier: ParetoFrontierObject) -> ParetoFrontierObject:
        try:
            await self.db.create_node("pareto_frontier", frontier.frontier_id, frontier.model_dump())
            await self.db.relate_nodes(
                f"optimization:{frontier.optimization_id}",
                "has_pareto_frontier",
                f"pareto_frontier:{frontier.frontier_id}",
            )
        except Exception as e:
            logger.warning(f"SurrealDB create_pareto_frontier fallback: {e}")
        self._memory_pareto[frontier.frontier_id] = frontier
        return frontier

    async def create_decision(self, decision: OptimizationDecision) -> OptimizationDecision:
        try:
            await self.db.create_node("optimization_decision", decision.decision_id, decision.model_dump())
            await self.db.relate_nodes(
                f"optimization:{decision.optimization_id}",
                "has_decision",
                f"optimization_decision:{decision.decision_id}",
            )
        except Exception as e:
            logger.warning(f"SurrealDB create_decision fallback: {e}")
        self._memory_decisions[decision.decision_id] = decision
        return decision

    async def invalidate_optimization(self, opt_id: str) -> Optional[OptimizationObject]:
        if opt_id in self._memory_opts:
            self._memory_opts[opt_id].status = "INVALIDATED"
            try:
                await self.db.upsert_node("optimization", opt_id, {"status": "INVALIDATED"})
            except Exception as e:
                logger.warning(f"SurrealDB invalidate_optimization fallback: {e}")
            return self._memory_opts[opt_id]
        return None

    async def mark_stale(self, opt_id: str) -> Optional[OptimizationObject]:
        if opt_id in self._memory_opts:
            self._memory_opts[opt_id].status = "STALE"
            try:
                await self.db.upsert_node("optimization", opt_id, {"status": "STALE"})
            except Exception as e:
                logger.warning(f"SurrealDB mark_stale fallback: {e}")
            return self._memory_opts[opt_id]
        return None

    async def get_optimization(self, opt_id: str) -> Optional[OptimizationObject]:
        return self._memory_opts.get(opt_id)

    async def get_candidates(self, opt_id: str) -> List[DesignCandidate]:
        return [c for c in self._memory_candidates.values() if c.optimization_id == opt_id]

    async def get_pareto_frontier(self, frontier_id: str) -> Optional[ParetoFrontierObject]:
        return self._memory_pareto.get(frontier_id)

    async def get_decision(self, decision_id: str) -> Optional[OptimizationDecision]:
        return self._memory_decisions.get(decision_id)
