/**
 * Provider-Neutral EDA Adapter Interface.
 */

import { PCBProject } from "../design/board-model";
import { PCBConstraints } from "../constraints/pcb-constraints";

export interface DRCValidationResult {
  passed: boolean;
  errorCount: number;
  warningCount: number;
  violations: Array<{ rule: string; severity: "ERROR" | "WARNING"; description: string }>;
}

export interface EDAAdapter {
  name: string;
  format: "kicad" | "altium" | "generic";
  exportProject(project: PCBProject, constraints?: PCBConstraints): string;
  importProject(data: string): PCBProject;
  runDRC(project: PCBProject, constraints: PCBConstraints): DRCValidationResult;
}
