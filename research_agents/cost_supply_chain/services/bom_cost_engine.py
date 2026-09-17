"""
Hierarchical BOM cost rollup and volume cost curve calculation engine.
Zero-fabrication rule: unpriced parts remain PRICE_UNKNOWN and are never guessed.
"""

from typing import Dict, List, Optional
from loguru import logger
from research_agents.cost_supply_chain.config import PRICE_UNKNOWN, config
from research_agents.cost_supply_chain.schemas import (
    BOMCostRollup,
    CostCategory,
    CostDriver,
    PartCost,
    VolumeCostCurve,
    VolumeCostPoint,
)
from research_agents.cost_supply_chain.services.currency_normalizer import CurrencyNormalizer


class BOMCostEngine:
    """Hierarchical BOM cost calculation and volume scaling."""

    def __init__(self, normalizer: Optional[CurrencyNormalizer] = None):
        self.normalizer = normalizer or CurrencyNormalizer()

    def rollup_bom_cost(
        self,
        bom_id: str,
        project_id: str,
        parts: List[PartCost],
        target_volume: int = 1000,
        target_currency: str = "USD",
    ) -> BOMCostRollup:
        """
        Compute total unit cost, category breakdown, and unpriced count.
        Enforces zero fabrication: unpriced parts are tracked explicitly.
        """
        total_unit_cost = 0.0
        total_tooling = 0.0
        unpriced_parts: List[str] = []
        category_sums: Dict[str, float] = {cat.value: 0.0 for cat in CostCategory}
        normalized_parts: List[PartCost] = []

        is_complete = True

        for p in parts:
            p_copy = p.model_copy()
            effective_cost = p.unit_cost
            if p.volume_tiers:
                sorted_tiers = sorted(p.volume_tiers, key=lambda t: t.min_quantity)
                for tier in sorted_tiers:
                    if target_volume >= tier.min_quantity:
                        effective_cost = tier.unit_cost

            if effective_cost is None or p.price_status == PRICE_UNKNOWN:
                unpriced_parts.append(p.part_id)
                is_complete = False
                p_copy.price_status = PRICE_UNKNOWN
                normalized_parts.append(p_copy)
                continue

            norm_unit, status = self.normalizer.convert(
                effective_cost, p.currency, target_currency
            )
            p_copy.unit_cost = norm_unit
            p_copy.currency = target_currency
            normalized_parts.append(p_copy)

            extended_part_cost = norm_unit * p.quantity_per_assembly
            total_unit_cost += extended_part_cost

            if p.breakdown:
                if p.breakdown.raw_material:
                    c, _ = self.normalizer.convert(p.breakdown.raw_material, p.currency, target_currency)
                    category_sums[CostCategory.RAW_MATERIAL.value] += c * p.quantity_per_assembly
                if p.breakdown.fabrication:
                    c, _ = self.normalizer.convert(p.breakdown.fabrication, p.currency, target_currency)
                    category_sums[CostCategory.FABRICATION.value] += c * p.quantity_per_assembly
                if p.breakdown.assembly:
                    c, _ = self.normalizer.convert(p.breakdown.assembly, p.currency, target_currency)
                    category_sums[CostCategory.ASSEMBLY.value] += c * p.quantity_per_assembly
                if p.breakdown.testing_inspection:
                    c, _ = self.normalizer.convert(p.breakdown.testing_inspection, p.currency, target_currency)
                    category_sums[CostCategory.TEST_INSPECTION.value] += c * p.quantity_per_assembly
                if p.breakdown.overhead_logistics:
                    c, _ = self.normalizer.convert(p.breakdown.overhead_logistics, p.currency, target_currency)
                    category_sums[CostCategory.OVERHEAD_LOGISTICS.value] += c * p.quantity_per_assembly
                if p.breakdown.tooling_nre:
                    c, _ = self.normalizer.convert(p.breakdown.tooling_nre, p.currency, target_currency)
                    total_tooling += c
            else:
                category_sums[CostCategory.RAW_MATERIAL.value] += extended_part_cost

        conf_factor = 0.05 if is_complete else 0.15
        conf_interval = {
            "lower_bound": round(total_unit_cost * (1.0 - conf_factor), 2),
            "upper_bound": round(total_unit_cost * (1.0 + conf_factor), 2),
        }

        top_drivers: List[CostDriver] = []
        priced_parts = [p for p in normalized_parts if p.unit_cost is not None]
        sorted_by_impact = sorted(
            priced_parts, key=lambda x: (x.unit_cost or 0) * x.quantity_per_assembly, reverse=True
        )
        for idx, p in enumerate(sorted_by_impact[:5]):
            ext = (p.unit_cost or 0.0) * p.quantity_per_assembly
            impact_pct = round((ext / total_unit_cost * 100.0), 2) if total_unit_cost > 0 else 0.0
            top_drivers.append(
                CostDriver(
                    driver_id=f"DRIVER-{idx+1:02d}",
                    name=f"Part: {p.part_name}",
                    category=CostCategory.RAW_MATERIAL,
                    impact_percentage=impact_pct,
                    cost_per_unit=ext,
                    currency=target_currency,
                    description=f"Direct unit cost of {p.part_name} contributes {impact_pct}% to total BOM unit cost.",
                    mitigation_options=[
                        "Negotiate volume discounts",
                        "Identify secondary qualified supplier",
                        "Evaluate alternative lower-spec variant",
                    ],
                )
            )

        return BOMCostRollup(
            bom_id=bom_id,
            project_id=project_id,
            target_volume=target_volume,
            currency=target_currency,
            total_unit_cost=round(total_unit_cost, 2),
            total_extended_cost=round(total_unit_cost * target_volume, 2),
            total_tooling_nre=round(total_tooling, 2),
            is_cost_complete=is_complete,
            unpriced_parts_count=len(unpriced_parts),
            unpriced_part_ids=unpriced_parts,
            parts_cost_breakdown=normalized_parts,
            category_breakdown={k: round(v, 2) for k, v in category_sums.items() if v > 0},
            confidence_interval=conf_interval,
            top_cost_drivers=top_drivers,
        )

    def generate_volume_cost_curve(
        self,
        rollup: BOMCostRollup,
        quantities: Optional[List[int]] = None,
    ) -> VolumeCostCurve:
        """Compute unit cost curve across production volumes including tooling amortization."""
        qty_points = quantities or [100, 500, 1000, 2500, 5000, 10000, 25000, 50000]
        points: List[VolumeCostPoint] = []
        base_unit = rollup.total_unit_cost or 0.0
        tooling = rollup.total_tooling_nre

        for q in qty_points:
            discount_factor = 1.0 - (0.05 * (q / 1000.0) ** 0.2 - 0.05)
            discount_factor = max(0.70, min(1.05, discount_factor))
            variable_cost = base_unit * discount_factor
            amortized_tooling = tooling / q if q > 0 else 0.0
            effective_unit = round(variable_cost + amortized_tooling, 2)
            points.append(
                VolumeCostPoint(
                    quantity=q,
                    unit_cost=effective_unit,
                    extended_cost=round(effective_unit * q, 2),
                )
            )

        return VolumeCostCurve(
            part_or_bom_id=rollup.bom_id,
            currency=rollup.currency,
            curve_points=points,
        )
