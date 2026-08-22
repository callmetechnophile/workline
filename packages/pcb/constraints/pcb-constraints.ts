/**
 * PCB Constraints and Design Rules.
 */

export interface TraceConstraints {
  minWidthMm: number;
  minSpacingMm: number;
  viaDiameterMm: number;
  viaDrillMm: number;
  clearanceMm: number;
}

export interface DifferentialPairConstraint {
  name: string;
  positiveNet: string;
  negativeNet: string;
  targetImpedanceOhm: number;
  maxSkewPs: number;
  traceSpacingMm: number;
  traceWidthMm: number;
}

export interface PowerRailConstraint {
  railName: string;
  voltageV: number;
  maxCurrentA: number;
  maxVoltageDropV: number;
  minCopperWeightOz: number;
}

export interface ThermalConstraints {
  ambientTempC: number;
  maxComponentTempC: number;
  maxBoardTempC: number;
  thermalConductivityWmk: number;
}

export interface PCBConstraints {
  constraintVersion: string;
  trace: TraceConstraints;
  powerRails: PowerRailConstraint[];
  diffPairs: DifferentialPairConstraint[];
  thermal: ThermalConstraints;
}
