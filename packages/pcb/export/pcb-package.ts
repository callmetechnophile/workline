/**
 * PCB Release Package schema.
 */

import { PCBProject } from "../design/board-model";
import { DRCValidationResult } from "../eda/adapter";
import { ThermalPrediction } from "../pinn/model";

export interface PCBReleasePackage {
  packageId: string;
  projectId: string;
  teamId: string;
  pcbId: string;
  version: number;
  boardName: string;
  schematicVersion: string;
  bomVersion: string;
  constraintVersion: string;
  drcReport: DRCValidationResult;
  thermalReport?: ThermalPrediction;
  approvedBy: string;
  approvedAt: number;
  generatedAt: number;
}
