/**
 * Multi-Physics Simulation Solver types and standardized physical result metrics.
 */

export enum SimulationSolverType {
  SPICE = "SPICE",
  THERMAL_SOLVER = "THERMAL_SOLVER",
  SI_PI_SOLVER = "SI_PI_SOLVER",
  PINN_SURROGATE = "PINN_SURROGATE",
}

export enum PhysicalDomain {
  ELECTRICAL = "ELECTRICAL",
  THERMAL = "THERMAL",
  SIGNAL_INTEGRITY = "SIGNAL_INTEGRITY",
  POWER_INTEGRITY = "POWER_INTEGRITY",
}

export interface PhysicalMetric {
  name: string;
  domain: PhysicalDomain;
  value: number;
  unit: "V" | "A" | "W" | "degC" | "Ohm" | "ps" | "V/m";
  targetRange?: { min?: number; max?: number };
}

export interface SolverResult {
  solverType: SimulationSolverType;
  domain: PhysicalDomain;
  metrics: PhysicalMetric[];
  executionTimeMs: number;
  converged: boolean;
  notes?: string;
}
