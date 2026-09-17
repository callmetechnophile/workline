"""
Cost driver extraction, Pareto analysis, and manufacturing penalty calculation.
Integrates handoffs from Agent #24 (DFM/DFA findings).
"""

from typing import Any, Dict, List, Optional
from research_agents.cost_supply_chain.schemas import CostCategory, CostDriver


class CostDriverEngine:
    """Extracts cost drivers and translates DFM/DFA findings into financial cost penalties."""

    def extract_from_dfm_handoff(
        self,
        dfm_findings: List[Dict[str, Any]],
        base_unit_cost: float,
        currency: str = "USD",
    ) -> List[CostDriver]:
        drivers: List[CostDriver] = []
        for idx, finding in enumerate(dfm_findings):
            rule_id = finding.get("rule_id", "DFM-RULE")
            desc = finding.get("finding", "Process complexity penalty")
            severity = finding.get("severity", "MEDIUM")

            multiplier = 0.08 if severity == "HIGH" else 0.04
            if severity == "CRITICAL":
                multiplier = 0.15

            penalty_cost = round(base_unit_cost * multiplier, 2)
            drivers.append(
                CostDriver(
                    driver_id=f"DFM-DRV-{idx+1:02d}",
                    name=f"DFM Penalty: {rule_id}",
                    category=CostCategory.FABRICATION,
                    impact_percentage=round(multiplier * 100.0, 1),
                    cost_per_unit=penalty_cost,
                    currency=currency,
                    description=desc,
                    mitigation_options=[
                        "Relax GD&T tolerances to standard machining capability",
                        "Consolidate tooling features to avoid secondary setups",
                        "Review material machinability rating",
                    ],
                )
            )
        return drivers

    def extract_from_dfa_handoff(
        self,
        dfa_metrics: Dict[str, Any],
        base_assembly_cost: float,
        currency: str = "USD",
    ) -> List[CostDriver]:
        drivers: List[CostDriver] = []
        fastener_count = dfa_metrics.get("fastener_count", 0)
        assembly_time_s = dfa_metrics.get("total_assembly_time_seconds", 0.0)

        if fastener_count > 10:
            penalty = round(fastener_count * 0.25, 2)
            drivers.append(
                CostDriver(
                    driver_id="DFA-DRV-FASTENERS",
                    name="DFA Penalty: Excessive Fastener Count",
                    category=CostCategory.ASSEMBLY,
                    impact_percentage=12.0,
                    cost_per_unit=penalty,
                    currency=currency,
                    description=f"BOM requires {fastener_count} discrete fasteners, increasing manual assembly labor and cycle time.",
                    mitigation_options=[
                        "Implement snap-fit features into molded parts",
                        "Standardize fastener head and thread sizes",
                        "Consolidate mating brackets into unibody geometries",
                    ],
                )
            )

        if assembly_time_s > 300.0:
            labor_cost = round((assembly_time_s / 3600.0) * 35.0, 2)
            drivers.append(
                CostDriver(
                    driver_id="DFA-DRV-CYCLE-TIME",
                    name="DFA Penalty: Extended Assembly Cycle Time",
                    category=CostCategory.ASSEMBLY,
                    impact_percentage=15.0,
                    cost_per_unit=labor_cost,
                    currency=currency,
                    description=f"Assembly cycle time of {assembly_time_s} seconds exceeds high-throughput target.",
                    mitigation_options=[
                        "Design self-locating alignment pins and chamfers",
                        "Eliminate reorientation during assembly sequence",
                    ],
                )
            )

        return drivers
