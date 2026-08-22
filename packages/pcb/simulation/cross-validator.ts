/**
 * Multi-Physics Cross-Validation Engine.
 * Compares fast PINN surrogate predictions against reference numerical solvers.
 */

import { SolverResult, PhysicalMetric } from "./solvers";

export type CrossValidationStatus = "PASS" | "FAIL" | "WARNING" | "UNKNOWN";

export interface MetricComparison {
  metricName: string;
  referenceValue: number;
  surrogateValue: number;
  unit: string;
  absoluteDiscrepancy: number;
  relativeDiscrepancy: number; // e.g. 0.04 = 4%
  status: CrossValidationStatus;
}

export interface CrossValidationReport {
  overallStatus: CrossValidationStatus;
  comparisons: MetricComparison[];
  mae: number;
  rmse: number;
  maxRelativeDiscrepancy: number;
  evaluatedAt: number;
}

export class SimulationCrossValidator {
  public static validate(
    referenceResults: SolverResult[],
    surrogateResult: SolverResult
  ): CrossValidationReport {
    const comparisons: MetricComparison[] = [];
    const surrogateMap = new Map<string, PhysicalMetric>();

    for (const m of surrogateResult.metrics) {
      surrogateMap.set(m.name, m);
    }

    let sumAbsError = 0.0;
    let sumSqError = 0.0;
    let maxRelError = 0.0;
    let validPairs = 0;

    for (const refRes of referenceResults) {
      for (const refMetric of refRes.metrics) {
        const surMetric = surrogateMap.get(refMetric.name);
        if (!surMetric) continue;

        const absDiff = Math.abs(surMetric.value - refMetric.value);
        const relDiff = refMetric.value !== 0 ? absDiff / Math.abs(refMetric.value) : absDiff;

        sumAbsError += absDiff;
        sumSqError += absDiff * absDiff;
        maxRelError = Math.max(maxRelError, relDiff);
        validPairs++;

        let status: CrossValidationStatus = "PASS";
        if (relDiff > 0.15) {
          status = "FAIL";
        } else if (relDiff > 0.05) {
          status = "WARNING";
        }

        comparisons.push({
          metricName: refMetric.name,
          referenceValue: refMetric.value,
          surrogateValue: surMetric.value,
          unit: refMetric.unit,
          absoluteDiscrepancy: Number(absDiff.toFixed(3)),
          relativeDiscrepancy: Number(relDiff.toFixed(4)),
          status,
        });
      }
    }

    if (validPairs === 0) {
      return {
        overallStatus: "UNKNOWN",
        comparisons: [],
        mae: 0,
        rmse: 0,
        maxRelativeDiscrepancy: 0,
        evaluatedAt: Date.now(),
      };
    }

    const mae = Number((sumAbsError / validPairs).toFixed(3));
    const rmse = Number(Math.sqrt(sumSqError / validPairs).toFixed(3));

    let overallStatus: CrossValidationStatus = "PASS";
    if (comparisons.some((c) => c.status === "FAIL")) {
      overallStatus = "FAIL";
    } else if (comparisons.some((c) => c.status === "WARNING")) {
      overallStatus = "WARNING";
    }

    return {
      overallStatus,
      comparisons,
      mae,
      rmse,
      maxRelativeDiscrepancy: Number(maxRelError.toFixed(4)),
      evaluatedAt: Date.now(),
    };
  }
}
