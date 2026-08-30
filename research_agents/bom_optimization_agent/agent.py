"""
Agent #8: BOMOptimizationAgent implementation using Google ADK conventions.
Optimizes a technically validated engineering BOM across supplier price, availability, shipping, and delivery constraints.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional
import uuid
from loguru import logger

from research_agents.bom_optimization_agent.adapters.base import SupplierAdapter
from research_agents.bom_optimization_agent.adapters.mock_adapter import MockDistributorAdapter
from research_agents.bom_optimization_agent.adapters.shipping.bluedart import BlueDartShippingProvider
from research_agents.bom_optimization_agent.config import opt_config
from research_agents.bom_optimization_agent.providers.base import (
    ProviderError,
    ReasoningProvider,
)
from research_agents.bom_optimization_agent.providers.bedrock import BedrockProvider
from research_agents.bom_optimization_agent.schemas import (
    BOMOptimizationAgentInput,
    BOMOptimizationAgentOutput,
    CostSummary,
    Location,
    OptimizedBOMItem,
    ProcurementStrategy,
    ProcurementTraceabilityItem,
    ProjectConstraints,
    ProjectMeta,
    ShippingOption,
    StructuredError,
    SupplierOffer,
    SupplierOrder,
)
from research_agents.bom_optimization_agent.services.alternative_evaluator import AlternativeEvaluator
from research_agents.bom_optimization_agent.services.compatibility_gate import TechnicalCompatibilityGate
from research_agents.bom_optimization_agent.services.file_exporter import ProcurementFileExporter
from research_agents.bom_optimization_agent.services.order_consolidator import OrderConsolidator
from research_agents.bom_optimization_agent.services.price_calculator import PriceCalculator
from research_agents.bom_optimization_agent.services.report_generator import ProcurementReportGenerator
from research_agents.bom_optimization_agent.services.shipping_service import ShippingService
from research_agents.bom_optimization_agent.services.strategy_generator import StrategyGenerator
from research_agents.bom_optimization_agent.services.traceability_builder import ProcurementTraceabilityBuilder


class BOMOptimizationAgent:
    """
    Google ADK-compliant BOM Cost, Availability & Logistics Optimization Agent.
    Optimizes a technically validated engineering BOM across supplier, price,
    availability, shipping, and delivery constraints.
    """

    NAME = "BOMOptimizationAgent"
    DESCRIPTION = (
        "Optimizes a technically validated engineering BOM across supplier, "
        "price, availability, shipping, and delivery constraints."
    )
    CAPABILITIES = [
        "procurement.optimize",
        "procurement.price",
        "procurement.shipping",
        "procurement.availability",
        "procurement.alternatives",
        "procurement.compare",
    ]

    def __init__(
        self,
        reasoning_provider: Optional[ReasoningProvider] = None,
        supplier_adapters: Optional[List[SupplierAdapter]] = None,
        compatibility_gate: Optional[TechnicalCompatibilityGate] = None,
        price_calculator: Optional[PriceCalculator] = None,
        shipping_service: Optional[ShippingService] = None,
        order_consolidator: Optional[OrderConsolidator] = None,
        strategy_generator: Optional[StrategyGenerator] = None,
        alternative_evaluator: Optional[AlternativeEvaluator] = None,
        traceability_builder: Optional[ProcurementTraceabilityBuilder] = None,
        report_generator: Optional[ProcurementReportGenerator] = None,
        file_exporter: Optional[ProcurementFileExporter] = None,
    ):
        self.provider = reasoning_provider or BedrockProvider()
        # Default mock distributor adapters covering Indian & global suppliers
        self.supplier_adapters = supplier_adapters or [
            MockDistributorAdapter("SUPP-ROBU", "Robu.in", "Pune", "Maharashtra"),
            MockDistributorAdapter("SUPP-MOUSER", "Mouser Electronics", "Bengaluru", "Karnataka"),
            MockDistributorAdapter("SUPP-DIGIKEY", "DigiKey India", "Bengaluru", "Karnataka"),
            MockDistributorAdapter("SUPP-PROBOTS", "Probots", "Bengaluru", "Karnataka"),
        ]
        self.compatibility_gate = compatibility_gate or TechnicalCompatibilityGate()
        self.price_calculator = price_calculator or PriceCalculator()
        self.shipping_service = shipping_service or ShippingService()
        self.order_consolidator = order_consolidator or OrderConsolidator(
            price_calculator=self.price_calculator,
            shipping_service=self.shipping_service,
        )
        self.strategy_generator = strategy_generator or StrategyGenerator(
            order_consolidator=self.order_consolidator,
        )
        self.alternative_evaluator = alternative_evaluator or AlternativeEvaluator()
        self.traceability_builder = traceability_builder or ProcurementTraceabilityBuilder()
        self.report_generator = report_generator or ProcurementReportGenerator()
        self.file_exporter = file_exporter or ProcurementFileExporter()

    async def run(
        self,
        input_data: BOMOptimizationAgentInput,
        execution_id: Optional[str] = None,
    ) -> BOMOptimizationAgentOutput:
        """
        Executes deterministic multi-supplier BOM cost & logistics optimization.
        """
        start_time = time.time()
        exec_id = (
            execution_id
            or (input_data.execution_context.execution_id if input_data.execution_context else None)
            or f"exec_{uuid.uuid4().hex[:8]}"
        )

        destination = input_data.project.destination or Location(
            city=opt_config.default_destination_city,
            state=opt_config.default_destination_state,
            country=opt_config.default_destination_country,
            postal_code=opt_config.default_destination_postal_code,
        )

        bom_items = input_data.bom.get("items", [])
        bom_id = input_data.bom.get("bom_id", "BOM-001")
        proj_id = input_data.project.project_id or input_data.project.title

        logger.info(
            f"[{exec_id}][{self.NAME}] Starting procurement optimization for project='{proj_id}', destination='{destination.city}, {destination.state}'"
        )

        # 1. Collect candidate supplier offers across adapters
        raw_offers: List[SupplierOffer] = []
        if input_data.supplier_data:
            raw_offers = [SupplierOffer.model_validate(o) for o in input_data.supplier_data]
        else:
            for adapter in self.supplier_adapters:
                for item in bom_items:
                    b_id = item.get("bom_item_id", "BOM-001")
                    part_no = item.get("part_number", "")
                    category = item.get("category", "component")
                    qty = int(item.get("quantity", 1))

                    offers = await adapter.get_offers_for_bom_item(b_id, part_no, category, qty)
                    raw_offers.extend(offers)

        # 2. Technical Compatibility Gating (Sections 9 & 10)
        compatible_offers, compat_warnings = self.compatibility_gate.filter_compatible_offers(
            offers=raw_offers,
            bom_items=bom_items,
            approved_alternatives=input_data.component_alternatives,
        )

        # 3. Generate 4 Procurement Strategies (Sections 22, 23, 24)
        selected_strategy, all_strategies, optimized_items = await self.strategy_generator.generate_strategies(
            compatible_offers=compatible_offers,
            bom_items=bom_items,
            destination=destination,
            constraints=input_data.project.constraints,
        )

        # 4. Evaluate Alternative Components (Sections 10 & 18)
        evaluated_alternatives = self.alternative_evaluator.evaluate_alternatives(
            component_alternatives=input_data.component_alternatives,
            bom_items=bom_items,
        )

        # 5. Build Cost Summary (Section 43)
        cost_summary = CostSummary(
            total_product_cost=selected_strategy.total_product_cost,
            total_shipping_cost=selected_strategy.total_shipping_cost,
            total_additional_cost=0.0,
            total_known_landed_cost=selected_strategy.total_known_landed_cost,
            unknown_costs=selected_strategy.unknown_costs,
            supplier_count=selected_strategy.supplier_count,
            order_count=len(selected_strategy.orders),
            estimated_delivery_days=selected_strategy.estimated_delivery_days,
        )

        # 6. Build Procurement Traceability (Section 44)
        traceability = self.traceability_builder.build_traceability(
            bom_items=bom_items,
            compatible_offers=compatible_offers,
            selected_strategy=selected_strategy,
            optimized_items=optimized_items,
        )

        # Supplier summary stats
        supplier_summary = [
            {
                "supplier_id": o.supplier_id,
                "supplier_name": o.supplier_name,
                "city": o.supplier_location.city,
                "items_count": len(o.items),
                "order_subtotal": o.product_subtotal,
                "shipping_cost": o.shipping_cost,
                "order_landed_cost": o.known_landed_cost,
                "lead_time_days": o.delivery_estimate_days,
            }
            for o in selected_strategy.orders
        ]

        delivery_summary = {
            "fastest_delivery_days": min((s.estimated_delivery_days or 99) for s in all_strategies) if all_strategies else None,
            "selected_strategy_days": selected_strategy.estimated_delivery_days,
            "destination_hub": f"{destination.city}, {destination.state}",
            "carrier": "Blue Dart",
        }

        optimization_id = f"OPT-{uuid.uuid4().hex[:6].upper()}"

        # 7. Render 17-Section Markdown Report (Section 45)
        report_markdown = self.report_generator.generate_report(
            project=input_data.project,
            bom_id=bom_id,
            optimization_id=optimization_id,
            destination=destination,
            selected_strategy=selected_strategy,
            all_strategies=all_strategies,
            optimized_items=optimized_items,
            orders=selected_strategy.orders,
            alternatives=evaluated_alternatives,
            compat_warnings=compat_warnings,
            proc_warnings=selected_strategy.warnings,
            cost_summary=cost_summary,
            traceability=traceability,
            assumptions=[],
            unknowns=[],
        )

        output = BOMOptimizationAgentOutput(
            status="success",
            project_id=proj_id,
            bom_id=bom_id,
            optimization_id=optimization_id,
            destination=destination,
            selected_strategy=selected_strategy,
            strategies=all_strategies,
            optimized_items=optimized_items,
            orders=selected_strategy.orders,
            alternatives=evaluated_alternatives,
            compatibility_warnings=compat_warnings,
            procurement_warnings=selected_strategy.warnings,
            cost_summary=cost_summary,
            supplier_summary=supplier_summary,
            delivery_summary=delivery_summary,
            traceability=traceability,
            confidence=0.96,
            structured_report_markdown=report_markdown,
        )

        # 8. File Export if output_dir provided (Section 47)
        if input_data.output_dir:
            self.file_exporter.export_artifacts(output, input_data.output_dir, overwrite=True)

        elapsed = time.time() - start_time
        logger.info(
            f"[{exec_id}][{self.NAME}] Optimization complete in {elapsed:.3f}s: "
            f"Items={len(optimized_items)} Suppliers={cost_summary.supplier_count} "
            f"Orders={cost_summary.order_count} LandedCost=INR {cost_summary.total_known_landed_cost:,.2f}"
        )

        return output

    def run_sync(
        self,
        input_data: BOMOptimizationAgentInput,
        execution_id: Optional[str] = None,
    ) -> BOMOptimizationAgentOutput:
        """Synchronous wrapper for Google ADK / CLI execution."""
        return asyncio.run(self.run(input_data=input_data, execution_id=execution_id))

    # =========================================================================
    # Internal Google ADK Capability Methods
    # =========================================================================

    def optimize_bom(self, input_data: BOMOptimizationAgentInput) -> BOMOptimizationAgentOutput:
        """ADK Capability: Optimizes BOM procurement synchronously."""
        return self.run_sync(input_data)

    def find_supplier_candidates(self, bom_items: List[Dict[str, Any]]) -> List[SupplierOffer]:
        """ADK Capability: Collects candidate supplier quotes across active adapters."""
        all_offers: List[SupplierOffer] = []
        for adapter in self.supplier_adapters:
            for it in bom_items:
                offers = asyncio.run(
                    adapter.get_offers_for_bom_item(
                        it.get("bom_item_id", "BOM-001"),
                        it.get("part_number", ""),
                        it.get("category", "component"),
                        int(it.get("quantity", 1)),
                    )
                )
                all_offers.extend(offers)
        return all_offers

    def calculate_product_cost(self, offer: SupplierOffer, qty: int) -> float:
        """ADK Capability: Calculates product subtotal respecting MOQ & price breaks."""
        item, _ = self.price_calculator.calculate_item_cost(offer, "Component", qty)
        return item.product_cost

    def calculate_shipping(self, order: SupplierOrder, destination: Location) -> ShippingOption:
        """ADK Capability: Computes Blue Dart freight for a supplier order bundle."""
        return asyncio.run(self.shipping_service.calculate_order_shipping(order, destination))

    def calculate_landed_cost(self, product_cost: float, shipping_cost: float) -> float:
        """ADK Capability: Computes known total landed cost."""
        return round(product_cost + shipping_cost, 2)

    def validate_availability(self, offer: SupplierOffer, qty: int) -> bool:
        """ADK Capability: Validates stock availability against required quantity."""
        return (offer.available_quantity is None) or (offer.available_quantity >= qty)

    def evaluate_alternatives(self, alternatives: List[Dict[str, Any]], bom_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """ADK Capability: Evaluates cost and approval status of alternative parts."""
        return self.alternative_evaluator.evaluate_alternatives(alternatives, bom_items)

    def optimize_orders(self, offers: List[SupplierOffer], bom_items: List[Dict[str, Any]], dest: Location) -> List[SupplierOrder]:
        """ADK Capability: Consolidates items into single supplier order packages."""
        return asyncio.run(self.order_consolidator.consolidate_orders(offers, bom_items, dest))

    def generate_procurement_strategies(
        self, offers: List[SupplierOffer], bom_items: List[Dict[str, Any]], dest: Location
    ) -> List[ProcurementStrategy]:
        """ADK Capability: Generates 4 distinct procurement configurations."""
        _, strategies, _ = asyncio.run(
            self.strategy_generator.generate_strategies(offers, bom_items, dest, ProjectConstraints())
        )
        return strategies

    def compare_strategies(self, strategies: List[ProcurementStrategy]) -> Dict[str, Any]:
        """ADK Capability: Compares financial and delivery trade-offs across strategies."""
        return {
            s.name: {
                "total_landed_cost": s.total_known_landed_cost,
                "delivery_days": s.estimated_delivery_days,
                "supplier_count": s.supplier_count,
            }
            for s in strategies
        }

    def generate_cost_report(self, output: BOMOptimizationAgentOutput) -> str:
        """ADK Capability: Exports Markdown procurement report."""
        return output.structured_report_markdown
