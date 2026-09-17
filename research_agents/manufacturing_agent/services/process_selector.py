"""
Manufacturing Process Selection and Trade-Off Comparison Engine (Section 3).
"""

from typing import Any, Dict, List, Optional
from research_agents.manufacturing_agent.schemas import (
    ManufacturingProcess,
    ProcessCapabilityComparison,
    VolumeTierLiteral,
)


class ProcessSelector:
    """Evaluates candidate manufacturing processes against geometry, material, tolerances, and volume."""

    def evaluate_process(
        self,
        process_name: str,
        material: str,
        volume_tier: VolumeTierLiteral = "PROTOTYPE",
        requires_tight_tolerance: bool = False,
    ) -> ManufacturingProcess:
        name_upper = process_name.upper()

        if "CNC" in name_upper or "MILLING" in name_upper or "TURNING" in name_upper:
            vol_suit = "STRONG" if volume_tier in ("PROTOTYPE", "LOW_VOLUME") else "ACCEPTABLE" if volume_tier == "MEDIUM_VOLUME" else "POOR"
            return ManufacturingProcess(
                process_id=f"PROC-CNC-{volume_tier}",
                name="3/5-Axis CNC Milling",
                family="CNC_MACHINING",
                geometric_compatibility="YES",
                material_compatibility="YES",
                tolerance_capability="STRONG",
                surface_finish_capability="STRONG",
                volume_suitability=vol_suit,
                tooling_complexity="LOW",
                risk_level="LOW",
                evidence_level="E3",
                notes="Ideal for low-volume precision; high per-unit cost at mass production volume.",
            )

        elif "INJECTION" in name_upper or "MOLD" in name_upper:
            vol_suit = "POOR" if volume_tier == "PROTOTYPE" else "ACCEPTABLE" if volume_tier == "LOW_VOLUME" else "STRONG"
            tooling = "HIGH"
            return ManufacturingProcess(
                process_id=f"PROC-MOLD-{volume_tier}",
                name="Thermoplastic Injection Molding",
                family="INJECTION_MOLDING",
                geometric_compatibility="YES",
                material_compatibility="YES" if "PLASTIC" in material.upper() or "POLY" in material.upper() else "NO",
                tolerance_capability="ACCEPTABLE",
                surface_finish_capability="STRONG",
                volume_suitability=vol_suit,
                tooling_complexity=tooling,
                risk_level="MEDIUM",
                evidence_level="E3",
                notes="High upfront steel mold tooling expenditure; lowest unit cost at scale.",
            )

        elif "ADDITIVE" in name_upper or "3D_PRINT" in name_upper:
            vol_suit = "STRONG" if volume_tier == "PROTOTYPE" else "POOR"
            tol_cap = "ACCEPTABLE" if not requires_tight_tolerance else "POOR"
            return ManufacturingProcess(
                process_id=f"PROC-AM-{volume_tier}",
                name="Additive Manufacturing (SLS / DMLS)",
                family="ADDITIVE_MANUFACTURING",
                geometric_compatibility="STRONG",
                material_compatibility="YES",
                tolerance_capability=tol_cap,
                surface_finish_capability="POOR",
                volume_suitability=vol_suit,
                tooling_complexity="LOW",
                risk_level="LOW",
                evidence_level="E3",
                notes="Zero tooling required; rough surface finish (Ra 6.3-12.5um) requiring secondary machining.",
            )

        else:
            return ManufacturingProcess(
                process_id=f"PROC-GENERIC-{volume_tier}",
                name=process_name,
                family="CNC_MACHINING",
                geometric_compatibility="CONDITIONAL",
                material_compatibility="CONDITIONAL",
                tolerance_capability="UNKNOWN",
                surface_finish_capability="UNKNOWN",
                volume_suitability="UNKNOWN",
                tooling_complexity="UNKNOWN",
                risk_level="UNKNOWN",
                evidence_level="E1",
                notes="Process capabilities require supplier technical data verification.",
            )

    def compare_processes(
        self,
        process_a: ManufacturingProcess,
        process_b: ManufacturingProcess,
        volume_tier: VolumeTierLiteral,
    ) -> ProcessCapabilityComparison:
        summary = (
            f"Comparison between {process_a.name} ({process_a.volume_suitability} for {volume_tier}) "
            f"and {process_b.name} ({process_b.volume_suitability} for {volume_tier})."
        )
        rec = process_a.name if process_a.volume_suitability == "STRONG" else process_b.name
        tradeoffs = [
            f"{process_a.name}: Tooling {process_a.tooling_complexity}, Tolerance {process_a.tolerance_capability}",
            f"{process_b.name}: Tooling {process_b.tooling_complexity}, Tolerance {process_b.tolerance_capability}",
        ]
        return ProcessCapabilityComparison(
            candidate_process_a=process_a,
            candidate_process_b=process_b,
            comparison_summary=summary,
            recommended_process=rec,
            tradeoffs=tradeoffs,
        )
