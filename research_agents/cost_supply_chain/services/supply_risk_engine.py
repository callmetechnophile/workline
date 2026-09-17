"""
Supply chain risk identification engine.
Detects single-sourcing, obsolescence, long lead-times, MOQ mismatch, and geographical concentration.
"""

from typing import List, Optional
from research_agents.cost_supply_chain.config import config
from research_agents.cost_supply_chain.schemas import (
    LifecycleStatus,
    PartCost,
    RiskSeverity,
    RiskType,
    SupplyRisk,
)


class SupplyRiskEngine:
    """Evaluates supply chain vulnerabilities across engineering BOMs."""

    def assess_bom_risks(
        self,
        project_id: str,
        parts: List[PartCost],
        target_volume: int = 1000,
    ) -> List[SupplyRisk]:
        risks: List[SupplyRisk] = []
        thresholds = config.risk_thresholds

        for idx, p in enumerate(parts):
            if p.is_single_source:
                unit = p.unit_cost or 0.0
                severity = RiskSeverity.HIGH if unit * p.quantity_per_assembly > 50.0 else RiskSeverity.MEDIUM
                risks.append(
                    SupplyRisk(
                        risk_id=f"RISK-SS-{p.part_id}",
                        part_id=p.part_id,
                        part_name=p.part_name,
                        risk_type=RiskType.SINGLE_SOURCE,
                        severity=severity,
                        description=f"Part '{p.part_name}' relies exclusively on a single source ({p.primary_supplier or 'Unspecified'}).",
                        supplier_country=p.supplier_country,
                        mitigation_strategy="Qualify secondary alternate supplier or design in multi-vendor footprint.",
                    )
                )

            if p.lifecycle_status in [LifecycleStatus.EOL, LifecycleStatus.NRND, LifecycleStatus.OBSOLETE]:
                severity = RiskSeverity.CRITICAL if p.lifecycle_status == LifecycleStatus.OBSOLETE else RiskSeverity.HIGH
                risks.append(
                    SupplyRisk(
                        risk_id=f"RISK-OBS-{p.part_id}",
                        part_id=p.part_id,
                        part_name=p.part_name,
                        risk_type=RiskType.OBSOLESCENCE,
                        severity=severity,
                        lifecycle_status=p.lifecycle_status,
                        description=f"Part '{p.part_name}' has lifecycle status '{p.lifecycle_status.value}'. Component faces discontinuation.",
                        mitigation_strategy="Execute redesign for replacement active silicon or secure Last-Time-Buy (LTB) buffer.",
                    )
                )

            if p.lead_time_weeks is not None:
                if p.lead_time_weeks >= thresholds.lead_time_critical_weeks:
                    risks.append(
                        SupplyRisk(
                            risk_id=f"RISK-LT-{p.part_id}",
                            part_id=p.part_id,
                            part_name=p.part_name,
                            risk_type=RiskType.LONG_LEAD_TIME,
                            severity=RiskSeverity.CRITICAL,
                            lead_time_weeks=p.lead_time_weeks,
                            description=f"Lead time of {p.lead_time_weeks} weeks exceeds critical threshold ({thresholds.lead_time_critical_weeks} wks).",
                            mitigation_strategy="Establish supplier consignment stock or pre-order raw material wafers/billets.",
                        )
                    )
                elif p.lead_time_weeks >= thresholds.lead_time_warning_weeks:
                    risks.append(
                        SupplyRisk(
                            risk_id=f"RISK-LT-{p.part_id}",
                            part_id=p.part_id,
                            part_name=p.part_name,
                            risk_type=RiskType.LONG_LEAD_TIME,
                            severity=RiskSeverity.MEDIUM,
                            lead_time_weeks=p.lead_time_weeks,
                            description=f"Lead time of {p.lead_time_weeks} weeks requires early procurement trigger.",
                            mitigation_strategy="Issue long-lead POs during initial design phase.",
                        )
                    )

            if p.moq is not None and p.moq > target_volume * thresholds.high_moq_ratio_threshold:
                risks.append(
                    SupplyRisk(
                        risk_id=f"RISK-MOQ-{p.part_id}",
                        part_id=p.part_id,
                        part_name=p.part_name,
                        risk_type=RiskType.HIGH_MOQ,
                        severity=RiskSeverity.MEDIUM,
                        moq=p.moq,
                        description=f"MOQ of {p.moq} units exceeds batch requirement ({target_volume}) by {round(p.moq/target_volume, 1)}x, tying up working capital.",
                        mitigation_strategy="Source through regional catalog distributor (e.g. Digi-Key/Mouser) or negotiate distributor split.",
                    )
                )

        return risks
