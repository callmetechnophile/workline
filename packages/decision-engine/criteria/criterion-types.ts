/**
 * Decision Criteria types, directions, and model definitions.
 */

export enum DecisionStatus {
  DRAFT = "DRAFT",
  UNDER_REVIEW = "UNDER_REVIEW",
  RECOMMENDED = "RECOMMENDED",
  APPROVED = "APPROVED",
  REJECTED = "REJECTED",
  SUPERSEDED = "SUPERSEDED",
  CANCELLED = "CANCELLED",
}

export enum DecisionType {
  COMPONENT_SELECTION = "COMPONENT_SELECTION",
  ARCHITECTURE_SELECTION = "ARCHITECTURE_SELECTION",
  PROTOCOL_SELECTION = "PROTOCOL_SELECTION",
  MATERIAL_SELECTION = "MATERIAL_SELECTION",
  TOOL_SELECTION = "TOOL_SELECTION",
  MODEL_SELECTION = "MODEL_SELECTION",
  PCB_OPTION = "PCB_OPTION",
  POWER_ARCHITECTURE = "POWER_ARCHITECTURE",
  SOFTWARE_ARCHITECTURE = "SOFTWARE_ARCHITECTURE",
  PROCUREMENT_SELECTION = "PROCUREMENT_SELECTION",
  OTHER = "OTHER",
}

export enum CriterionCategory {
  TECHNICAL_FIT = "TECHNICAL_FIT",
  POWER = "POWER",
  PERFORMANCE = "PERFORMANCE",
  THERMAL = "THERMAL",
  SIZE = "SIZE",
  WEIGHT = "WEIGHT",
  RELIABILITY = "RELIABILITY",
  AVAILABILITY = "AVAILABILITY",
  COST = "COST",
  LEAD_TIME = "LEAD_TIME",
  MANUFACTURER = "MANUFACTURER",
  PACKAGE = "PACKAGE",
  EFFICIENCY = "EFFICIENCY",
  COMPLEXITY = "COMPLEXITY",
  RISK = "RISK",
  DOCUMENTATION = "DOCUMENTATION",
  MAINTAINABILITY = "MAINTAINABILITY",
  SUPPLY_CHAIN = "SUPPLY_CHAIN",
  LIFECYCLE = "LIFECYCLE",
}

export enum CriterionDirection {
  MAXIMIZE = "MAXIMIZE",
  MINIMIZE = "MINIMIZE",
  TARGET = "TARGET",
  PREFERENCE = "PREFERENCE",
}

export interface DecisionCriterion {
  criterionId: string;
  name: string;
  category: CriterionCategory;
  weight: number; // e.g. 0.40
  direction: CriterionDirection;
  mandatory: boolean;
  targetValue?: number;
  description?: string;
}

export interface DecisionCandidate {
  candidateId: string;
  entityId: string;
  name: string;
  eligibilityStatus: "ELIGIBLE" | "INELIGIBLE" | "UNKNOWN" | "CONFLICTED";
  score: number;
  criterionScores: Record<string, number>;
  tradeoffs: string[];
  warnings: string[];
}

export interface EngineeringDecision {
  decisionId: string;
  projectId: string;
  teamId: string;
  title: string;
  description: string;
  status: DecisionStatus;
  decisionType: DecisionType;
  selectedCandidate?: string;
  alternatives: string[];
  criteria: DecisionCriterion[];
  recommendation?: string;
  rationale?: string;
  confidence: number;
  version: number;
  supersededBy?: string;
  createdBy: string;
  approvedBy?: string;
  approvedAt?: number;
  createdAt: number;
  updatedAt: number;
}
