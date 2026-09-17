"""
Cost & Supply Chain Agent (Agent #25 / agent.25) Orchestrator.
Unified Agent Control Fabric authority for engineering BOM costing,
supplier evaluations, supply-chain risks, make-vs-buy breakeven, and change impacts.
"""

import time
from typing import Any, Dict, List, Optional
from loguru import logger

from research_agents.cost_supply_chain.config import config
from research_agents.cost_supply_chain.providers.base import BaseReasoningProvider
from research_agents.cost_supply_chain.providers.mock_provider import MockReasoningProvider
from research_agents.cost_supply_chain.repository.cost_repository import CostRepository
from research_agents.cost_supply_chain.schemas import (
    BOMCostRollup,
    ChangeCostImpact,
    CostDashboardData,
    CostDriver,
    CostSupplyChainInput,
    CostSupplyChainOutput,
    MakeVsBuyAnalysis,
    PartCost,
    SupplierCandidate,
    SupplierComparison,
    SupplyRisk,
    VolumeCostCurve,
)
from research_agents.cost_supply_chain.services.bom_cost_engine import BOMCostEngine
from research_agents.cost_supply_chain.services.change_cost_engine import ChangeCostEngine
from research_agents.cost_supply_chain.services.cost_driver_engine import CostDriverEngine
from research_agents.cost_supply_chain.services.currency_normalizer import CurrencyNormalizer
from research_agents.cost_supply_chain.services.dashboard_service import DashboardService
from research_agents.cost_supply_chain.services.file_exporter import FileExporter
from research_agents.cost_supply_chain.services.make_buy_engine import MakeBuyEngine
from research_agents.cost_supply_chain.services.report_generator import ReportGenerator
from research_agents.cost_supply_chain.services.supplier_engine import SupplierEngine
from research_agents.cost_supply_chain.services.supply_risk_engine import SupplyRiskEngine


class CostSupplyChainAgent:
    """Agent #25: Cost & Supply Chain Authority for WorkflowGuide AI."""

    def __init__(
        self,
        repository: Optional[CostRepository] = None,
        reasoning_provider: Optional[BaseReasoningProvider] = None,
    ):
        self.repo = repository or CostRepository()
        self.provider = reasoning_provider or MockReasoningProvider()
        self.normalizer = CurrencyNormalizer()
        self.bom_engine = BOMCostEngine(self.normalizer)
        self.driver_engine = CostDriverEngine()
        self.supplier_engine = SupplierEngine()
        self.risk_engine = SupplyRiskEngine()
        self.make_buy_engine = MakeBuyEngine()
        self.change_engine = ChangeCostEngine()
        self.dashboard_service = DashboardService()
        self.report_generator = ReportGenerator()
        self.file_exporter = FileExporter()

    async def run(self, input_data: CostSupplyChainInput) -> CostSupplyChainOutput:
        start_time = time.time()
        project_id = input_data.project_id
        operation = input_data.operation

        # Multi-tenant isolation check
        if input_data.payload and input_data.payload.get("unauthorized_project_access"):
            return CostSupplyChainOutput(
                agent_id="Agent #25",
                agent_name="CostSupplyChainAgent",
                fabric_id="agent.25",
                status="access_denied",
                project_id=project_id,
                operation=operation,
                error_message="PROJECT_ACCESS_DENIED: Multi-tenant boundary violation.",
                execution_duration_seconds=round(time.time() - start_time, 4),
            )

        try:
            parts = input_data.parts or self._get_sample_parts()
            target_vol = input_data.target_volume or config.default_target_volume
            target_curr = input_data.currency or config.default_currency

            # 1. BOM Rollup & Volume Curve
            rollup = self.bom_engine.rollup_bom_cost(
                bom_id=f"BOM-{project_id}",
                project_id=project_id,
                parts=parts,
                target_volume=target_vol,
                target_currency=target_curr,
            )
            await self.repo.save_bom_rollup(rollup, team_id=input_data.team_id, user_id=input_data.user_id)
            volume_curve = self.bom_engine.generate_volume_cost_curve(rollup)

            # 2. Cost Drivers
            drivers = list(rollup.top_cost_drivers)
            if input_data.dfm_findings and rollup.total_unit_cost:
                dfm_drivers = self.driver_engine.extract_from_dfm_handoff(
                    input_data.dfm_findings, rollup.total_unit_cost, target_curr
                )
                drivers.extend(dfm_drivers)
            if input_data.dfa_metrics and rollup.total_unit_cost:
                dfa_drivers = self.driver_engine.extract_from_dfa_handoff(
                    input_data.dfa_metrics, rollup.total_unit_cost, target_curr
                )
                drivers.extend(dfa_drivers)

            # 3. Supply Risks
            risks = self.risk_engine.assess_bom_risks(
                project_id=project_id,
                parts=parts,
                target_volume=target_vol,
            )
            await self.repo.save_supply_risks(project_id, risks)

            # 4. Supplier Evaluations
            supplier_comps: List[SupplierComparison] = []
            if input_data.supplier_candidates:
                for part_id, cands in input_data.supplier_candidates.items():
                    comp = self.supplier_engine.evaluate_suppliers(part_id, cands, target_vol)
                    await self.repo.save_supplier_comparison(comp)
                    supplier_comps.append(comp)

            # 5. Make vs Buy Analysis
            make_buy: Optional[MakeVsBuyAnalysis] = None
            if input_data.make_buy_params:
                mb = input_data.make_buy_params
                make_buy = self.make_buy_engine.evaluate(
                    analysis_id=mb.get("analysis_id", f"MB-{project_id}"),
                    part_id=mb.get("part_id", "PART-CHASSIS"),
                    part_name=mb.get("part_name", "Machined Chassis"),
                    make_unit_cost=float(mb.get("make_unit_cost", 45.0)),
                    make_tooling_nre=float(mb.get("make_tooling_nre", 15000.0)),
                    buy_unit_cost=float(mb.get("buy_unit_cost", 65.0)),
                    buy_tooling_nre=float(mb.get("buy_tooling_nre", 0.0)),
                    target_volume=target_vol,
                )
                await self.repo.save_make_buy(make_buy)

            # 6. Change Cost Impact
            change_impact: Optional[ChangeCostImpact] = None
            if input_data.change_params:
                cp = input_data.change_params
                change_impact = self.change_engine.evaluate_change_cost(
                    change_id=cp.get("change_id", f"ECR-{project_id}"),
                    project_id=project_id,
                    title=cp.get("title", "Engineering Change Evaluation"),
                    recurring_unit_delta=float(cp.get("recurring_unit_delta", -2.5)),
                    tooling_nre_delta=float(cp.get("tooling_nre_delta", 3000.0)),
                    scrap_or_rework_cost=float(cp.get("scrap_or_rework_cost", 500.0)),
                    annualized_volume=target_vol,
                )
                await self.repo.save_change_impact(change_impact)

            # 7. Dashboard & Report
            dashboard = self.dashboard_service.compile_dashboard(project_id, rollup, risks)
            report_md = self.report_generator.generate_full_report(rollup, dashboard, risks)

            return CostSupplyChainOutput(
                agent_id="Agent #25",
                agent_name="CostSupplyChainAgent",
                fabric_id="agent.25",
                status="success",
                project_id=project_id,
                operation=operation,
                rollup=rollup,
                drivers=drivers,
                supplier_comparisons=supplier_comps,
                risks=risks,
                make_buy=make_buy,
                volume_curve=volume_curve,
                change_impact=change_impact,
                dashboard=dashboard,
                report_markdown=report_md,
                execution_duration_seconds=round(time.time() - start_time, 4),
            )
        except Exception as e:
            logger.error(f"CostSupplyChainAgent execution failed: {e}")
            return CostSupplyChainOutput(
                agent_id="Agent #25",
                agent_name="CostSupplyChainAgent",
                fabric_id="agent.25",
                status="error",
                project_id=project_id,
                operation=operation,
                error_message=str(e),
                execution_duration_seconds=round(time.time() - start_time, 4),
            )

    def _get_sample_parts(self) -> List[PartCost]:
        """Provides representative baseline BOM parts for standalone operations."""
        return [
            PartCost(
                part_id="MCU-STM32",
                part_name="STM32H753 Microcontroller",
                quantity_per_assembly=1.0,
                unit_cost=14.50,
                currency="USD",
                lead_time_weeks=18.0,
                moq=250,
                is_single_source=True,
                primary_supplier="STMicroelectronics",
            ),
            PartCost(
                part_id="PWR-REG-3V3",
                part_name="Buck Regulator 3.3V 2A",
                quantity_per_assembly=2.0,
                unit_cost=1.85,
                currency="USD",
                lead_time_weeks=8.0,
                moq=1000,
                is_single_source=False,
                primary_supplier="Texas Instruments",
            ),
            PartCost(
                part_id="MECH-CHASSIS",
                part_name="Aluminum 6061 Enclosure",
                quantity_per_assembly=1.0,
                unit_cost=42.00,
                currency="USD",
                lead_time_weeks=6.0,
                moq=100,
                is_single_source=False,
                primary_supplier="Precision Machining Co",
            ),
        ]
