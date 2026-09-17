"""
SurrealDB graph access repository for Agent #25 (CostSupplyChainAgent).
Persists BOM rollups, cost baselines, supplier evaluations, risks, and make/buy decisions.
"""

from typing import Any, Dict, List, Optional
from loguru import logger
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.cost_supply_chain.schemas import (
    BOMCostRollup,
    ChangeCostImpact,
    CostDashboardData,
    MakeVsBuyAnalysis,
    SupplierComparison,
    SupplyRisk,
)


class CostRepository:
    """SurrealDB graph access repository with memory fallback."""

    def __init__(self, db_client: Optional[SurrealDBClient] = None):
        self.db = db_client or SurrealDBClient()
        self._memory_rollups: Dict[str, BOMCostRollup] = {}
        self._memory_suppliers: Dict[str, SupplierComparison] = {}
        self._memory_risks: Dict[str, List[SupplyRisk]] = {}  # project_id -> risks
        self._memory_make_buy: Dict[str, MakeVsBuyAnalysis] = {}
        self._memory_changes: Dict[str, ChangeCostImpact] = {}

    async def save_bom_rollup(
        self, rollup: BOMCostRollup, team_id: Optional[str] = None, user_id: Optional[str] = None
    ) -> BOMCostRollup:
        self._memory_rollups[rollup.bom_id] = rollup
        try:
            payload = rollup.model_dump()
            if team_id:
                payload["team_id"] = team_id
            if user_id:
                payload["user_id"] = user_id
            await self.db.create_node("bom_cost_rollup", rollup.bom_id, payload)
            await self.db.relate_nodes(
                f"project:{rollup.project_id}", "has_cost_rollup", f"bom_cost_rollup:{rollup.bom_id}"
            )
        except Exception as e:
            logger.warning(f"SurrealDB save_bom_rollup fallback to memory: {e}")
        return rollup

    async def get_bom_rollup(self, bom_id: str) -> Optional[BOMCostRollup]:
        return self._memory_rollups.get(bom_id)

    async def save_supplier_comparison(self, comparison: SupplierComparison) -> SupplierComparison:
        self._memory_suppliers[comparison.part_id] = comparison
        try:
            await self.db.create_node("supplier_comparison", comparison.part_id, comparison.model_dump())
        except Exception as e:
            logger.warning(f"SurrealDB save_supplier_comparison fallback: {e}")
        return comparison

    async def get_supplier_comparison(self, part_id: str) -> Optional[SupplierComparison]:
        return self._memory_suppliers.get(part_id)

    async def save_supply_risks(self, project_id: str, risks: List[SupplyRisk]) -> List[SupplyRisk]:
        self._memory_risks[project_id] = risks
        try:
            for r in risks:
                await self.db.create_node("supply_risk", r.risk_id, r.model_dump())
                await self.db.relate_nodes(
                    f"project:{project_id}", "has_supply_risk", f"supply_risk:{r.risk_id}"
                )
        except Exception as e:
            logger.warning(f"SurrealDB save_supply_risks fallback: {e}")
        return risks

    async def get_supply_risks(self, project_id: str) -> List[SupplyRisk]:
        return self._memory_risks.get(project_id, [])

    async def save_make_buy(self, analysis: MakeVsBuyAnalysis) -> MakeVsBuyAnalysis:
        self._memory_make_buy[analysis.analysis_id] = analysis
        try:
            await self.db.create_node("make_vs_buy", analysis.analysis_id, analysis.model_dump())
        except Exception as e:
            logger.warning(f"SurrealDB save_make_buy fallback: {e}")
        return analysis

    async def get_make_buy(self, analysis_id: str) -> Optional[MakeVsBuyAnalysis]:
        return self._memory_make_buy.get(analysis_id)

    async def save_change_impact(self, impact: ChangeCostImpact) -> ChangeCostImpact:
        self._memory_changes[impact.change_id] = impact
        try:
            await self.db.create_node("change_cost_impact", impact.change_id, impact.model_dump())
            await self.db.relate_nodes(
                f"project:{impact.project_id}", "has_cost_impact", f"change_cost_impact:{impact.change_id}"
            )
        except Exception as e:
            logger.warning(f"SurrealDB save_change_impact fallback: {e}")
        return impact

    async def get_change_impact(self, change_id: str) -> Optional[ChangeCostImpact]:
        return self._memory_changes.get(change_id)
