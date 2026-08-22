/**
 * PINN Physics-Informed Design Engine Models and Predictions.
 */

export interface PhysicsLossWeights {
  lambdaData: number;
  lambdaPhysics: number;
  lambdaBoundary: number;
  lambdaConstraint: number;
}

export interface Hotspot {
  xMm: number;
  yMm: number;
  temperatureC: number;
  componentRef?: string;
}

export interface ThermalPrediction {
  modelId: string;
  modelVersion: string;
  maxTemperatureC: number;
  avgTemperatureC: number;
  hotspots: Hotspot[];
  gridResolution: { nx: number; ny: number };
  temperatureGrid: number[][];
  isOutOfDistribution: boolean;
  status: "MODEL_PREDICTION" | "BENCHMARKED_VALID";
  inferenceTimeMs: number;
  lossResidual: number;
}
