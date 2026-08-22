/**
 * Engineering Requirement schemas and category enums.
 */

export enum RequirementCategory {
  ELECTRICAL = "ELECTRICAL",
  POWER = "POWER",
  MECHANICAL = "MECHANICAL",
  THERMAL = "THERMAL",
  COMMUNICATION = "COMMUNICATION",
  COMPUTE = "COMPUTE",
  MEMORY = "MEMORY",
  SENSOR = "SENSOR",
  ACTUATOR = "ACTUATOR",
  SAFETY = "SAFETY",
  ENVIRONMENTAL = "ENVIRONMENTAL",
  PCB = "PCB",
  SOFTWARE = "SOFTWARE",
  PERFORMANCE = "PERFORMANCE",
  PROCUREMENT = "PROCUREMENT",
  OTHER = "OTHER",
}

export enum ValidationStatus {
  PASS = "PASS",
  FAIL = "FAIL",
  UNKNOWN = "UNKNOWN",
  CONFLICT = "CONFLICT",
  NOT_APPLICABLE = "NOT_APPLICABLE",
}

export enum ConstraintOperator {
  EQ = "=",
  NEQ = "!=",
  GT = ">",
  GTE = ">=",
  LT = "<",
  LTE = "<=",
  IN = "IN",
  NOT_IN = "NOT_IN",
  BETWEEN = "BETWEEN",
  CONTAINS = "CONTAINS",
  NOT_CONTAINS = "NOT_CONTAINS",
}

export interface EngineeringConstraint {
  constraintId: string;
  property: string;
  operator: ConstraintOperator;
  requiredValue: string;
  requiredUnit?: string;
  normalizedValue: number;
  dimension: string;
  tolerance?: {
    type: "ABSOLUTE" | "RELATIVE";
    value: number; // e.g. 0.05 for 5%
  };
  source?: string;
}

export interface EngineeringRequirement {
  requirementId: string;
  projectId: string;
  teamId: string;
  category: RequirementCategory;
  description: string;
  constraints: EngineeringConstraint[];
  priority: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  status: "ACTIVE" | "SUPERSEDED" | "DRAFT";
  source?: string;
  createdAt: number;
  updatedAt: number;
}
