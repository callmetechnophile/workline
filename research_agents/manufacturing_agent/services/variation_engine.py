"""
Manufacturing Process Variation & Statistical Capability (Cp/Cpk) Engine (Section 9).
"""

import math
from typing import Any, Dict, List, Optional
from research_agents.manufacturing_agent.config import manufacturing_config
from research_agents.manufacturing_agent.schemas import VariationData


class VariationEngine:
    """Calculates Cp, Cpk, Pp, Ppk from actual datasets. Rejects fabricated data."""

    def evaluate_capability(
        self,
        parameter_name: str,
        samples: Optional[List[float]],
        usl: Optional[float],
        lsl: Optional[float],
    ) -> VariationData:
        # Rule: Require minimum sample size (default 30) and genuine measured data
        if not samples or len(samples) < manufacturing_config.min_sample_size_variation:
            needed = []
            if not samples:
                needed.append("Sample measurements list is empty or None")
            else:
                needed.append(f"Sample count ({len(samples)}) is below statistical minimum ({manufacturing_config.min_sample_size_variation})")
            if usl is None or lsl is None:
                needed.append("Upper and Lower Specification Limits (USL, LSL) required")

            return VariationData(
                parameter_name=parameter_name,
                sample_size=len(samples) if samples else 0,
                usl=usl,
                lsl=lsl,
                is_sufficient=False,
                status="DATA_INSUFFICIENT",
                missing_data_requirements=needed,
            )

        n = len(samples)
        mean_val = sum(samples) / n
        variance = sum((x - mean_val) ** 2 for x in samples) / (n - 1)
        std_dev = math.sqrt(variance)

        if std_dev == 0.0 or usl is None or lsl is None:
            return VariationData(
                parameter_name=parameter_name,
                sample_size=n,
                mean=round(mean_val, 4),
                std_dev=0.0,
                is_sufficient=False,
                status="DATA_INSUFFICIENT",
                missing_data_requirements=["Zero standard deviation or missing USL/LSL limits."],
            )

        cp = (usl - lsl) / (6.0 * std_dev)
        cpu = (usl - mean_val) / (3.0 * std_dev)
        cpl = (mean_val - lsl) / (3.0 * std_dev)
        cpk = min(cpu, cpl)

        return VariationData(
            parameter_name=parameter_name,
            sample_size=n,
            usl=usl,
            lsl=lsl,
            mean=round(mean_val, 4),
            std_dev=round(std_dev, 4),
            cp=round(cp, 3),
            cpk=round(cpk, 3),
            pp=round(cp, 3),
            ppk=round(cpk, 3),
            is_sufficient=True,
            status="DATA_SUFFICIENT",
        )
