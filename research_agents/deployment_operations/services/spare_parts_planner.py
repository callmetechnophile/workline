"""
Spare parts planning integrating with Agent #25 (Cost & Supply Chain).
"""

from typing import Any, Dict, List, Optional
from research_agents.deployment_operations.schemas import SparePartRequirement


class SparePartsPlanner:
    """Converts sourcing lead times and criticality into operational spare inventory recommendations."""

    def plan_spares(
        self,
        supply_chain_handoff: Optional[Dict[str, Any]] = None,
    ) -> List[SparePartRequirement]:
        spares: List[SparePartRequirement] = []

        if supply_chain_handoff and "parts" in supply_chain_handoff:
            for p in supply_chain_handoff["parts"]:
                is_ss = p.get("is_single_source", False)
                lt = p.get("lead_time_weeks", 4.0)
                risk_level = "HIGH" if (is_ss or lt > 16.0) else "LOW"
                qty = 2 if risk_level == "HIGH" else 1

                spares.append(
                    SparePartRequirement(
                        part_id=p.get("part_id", "PART-UNKNOWN"),
                        part_name=p.get("part_name", "Component"),
                        recommended_stock_qty=qty,
                        lead_time_weeks=lt,
                        is_single_source=is_ss,
                        is_critical=is_ss or lt > 12.0,
                        sourcing_risk_level=risk_level,
                    )
                )
        else:
            # Baseline critical spares
            spares.append(
                SparePartRequirement(
                    part_id="SPARE-MCU-01",
                    part_name="Primary Microcontroller Module",
                    recommended_stock_qty=2,
                    lead_time_weeks=18.0,
                    is_single_source=True,
                    is_critical=True,
                    sourcing_risk_level="HIGH",
                )
            )
            spares.append(
                SparePartRequirement(
                    part_id="SPARE-PWR-02",
                    part_name="12V Redundant Power Supply Unit",
                    recommended_stock_qty=1,
                    lead_time_weeks=6.0,
                    is_single_source=False,
                    is_critical=True,
                    sourcing_risk_level="MEDIUM",
                )
            )

        return spares
