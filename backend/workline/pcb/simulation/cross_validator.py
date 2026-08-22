"""Cross-validation between PINN surrogate predictions and reference numerical solvers."""

import math
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.workline.pcb.simulation.solvers import PhysicalMetric, SolverResult


class CrossValidationStatus(str):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    UNKNOWN = "UNKNOWN"


class MetricComparison(BaseModel):
    metric_name: str
    reference_value: float
    surrogate_value: float
    unit: str
    absolute_discrepancy: float
    relative_discrepancy: float
    status: str  # PASS, FAIL, WARNING, UNKNOWN


class CrossValidationReport(BaseModel):
    overall_status: str
    comparisons: List[MetricComparison] = Field(default_factory=list)
    mae: float = 0.0
    rmse: float = 0.0
    max_relative_discrepancy: float = 0.0
    evaluated_at: float = Field(default_factory=time.time)


class SimulationCrossValidator:
    """Evaluates surrogate model fidelity against reference simulation outputs."""

    @classmethod
    def validate(
        cls, reference_results: List[SolverResult], surrogate_result: SolverResult
    ) -> CrossValidationReport:
        comparisons: List[MetricComparison] = []
        surrogate_map: Dict[str, PhysicalMetric] = {m.name: m for m in surrogate_result.metrics}

        sum_abs_err = 0.0
        sum_sq_err = 0.0
        max_rel_err = 0.0
        valid_pairs = 0

        for ref_res in reference_results:
            for ref_m in ref_res.metrics:
                sur_m = surrogate_map.get(ref_m.name)
                if not sur_m:
                    continue

                abs_diff = abs(sur_m.value - ref_m.value)
                rel_diff = abs_diff / abs(ref_m.value) if ref_m.value != 0 else abs_diff

                sum_abs_err += abs_diff
                sum_sq_err += abs_diff ** 2
                max_rel_err = max(max_rel_err, rel_diff)
                valid_pairs += 1

                status = "PASS"
                if rel_diff > 0.15:
                    status = "FAIL"
                elif rel_diff > 0.05:
                    status = "WARNING"

                comparisons.append(
                    MetricComparison(
                        metric_name=ref_m.name,
                        reference_value=ref_m.value,
                        surrogate_value=sur_m.value,
                        unit=ref_m.unit,
                        absolute_discrepancy=round(abs_diff, 3),
                        relative_discrepancy=round(rel_diff, 4),
                        status=status,
                    )
                )

        if valid_pairs == 0:
            return CrossValidationReport(
                overall_status="UNKNOWN",
                comparisons=[],
                mae=0.0,
                rmse=0.0,
                max_relative_discrepancy=0.0,
            )

        mae = round(sum_abs_err / valid_pairs, 3)
        rmse = round(math.sqrt(sum_sq_err / valid_pairs), 3)

        overall_status = "PASS"
        if any(c.status == "FAIL" for c in comparisons):
            overall_status = "FAIL"
        elif any(c.status == "WARNING" for c in comparisons):
            overall_status = "WARNING"

        return CrossValidationReport(
            overall_status=overall_status,
            comparisons=comparisons,
            mae=mae,
            rmse=rmse,
            max_relative_discrepancy=round(max_rel_err, 4),
        )
