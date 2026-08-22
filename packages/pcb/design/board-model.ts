/**
 * PCB Project, Board Dimensions, Layer Stack, and Placement models.
 */

import { PCBPin } from "../schematic/schematic-model";

export enum PCBStatus {
  DRAFT = "DRAFT",
  SCHEMATIC = "SCHEMATIC",
  PLACEMENT = "PLACEMENT",
  ROUTING = "ROUTING",
  VALIDATION = "VALIDATION",
  REVIEW = "REVIEW",
  APPROVED = "APPROVED",
  RELEASED = "RELEASED",
  BLOCKED = "BLOCKED",
  SUPERSEDED = "SUPERSEDED",
}

export interface BoardDimensions {
  width: number;
  height: number;
  thickness: number;
  units: "mm" | "mil" | "inch";
}

export interface LayerInfo {
  layerId: number;
  name: string;
  type: "copper" | "dielectric" | "silkscreen" | "solder_mask";
  thicknessUm: number;
  material: string;
}

export interface PCBComponent {
  componentEntityId: string;
  bomItemId: string;
  referenceDesignator: string;
  symbol: string;
  footprint: string;
  package: string;
  pins: PCBPin[];
  position: { x: number; y: number };
  rotation: number;
  layer: string;
  placementStatus: "PLACED" | "UNPLACED" | "LOCKED";
  powerDissipationW?: number;
}

export interface PCBProject {
  pcbId: string;
  projectId: string;
  teamId: string;
  version: number;
  boardName: string;
  dimensions: BoardDimensions;
  layerCount: number;
  layerStack: LayerInfo[];
  units: "mm" | "mil" | "inch";
  status: PCBStatus;
  schematicVersion: string;
  bomVersion: string;
  constraintVersion: string;
  components: PCBComponent[];
  createdAt: number;
  updatedAt: number;
}
