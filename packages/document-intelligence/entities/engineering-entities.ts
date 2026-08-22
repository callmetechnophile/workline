/**
 * Engineering entity types and models.
 */

export enum EngineeringEntityType {
  COMPONENT = "COMPONENT",
  MANUFACTURER = "MANUFACTURER",
  MODEL_NUMBER = "MODEL_NUMBER",
  PART_NUMBER = "PART_NUMBER",
  VOLTAGE = "VOLTAGE",
  CURRENT = "CURRENT",
  POWER = "POWER",
  RESISTANCE = "RESISTANCE",
  CAPACITANCE = "CAPACITANCE",
  INDUCTANCE = "INDUCTANCE",
  FREQUENCY = "FREQUENCY",
  TEMPERATURE = "TEMPERATURE",
  PACKAGE = "PACKAGE",
  PROTOCOL = "PROTOCOL",
  INTERFACE = "INTERFACE",
  MATERIAL = "MATERIAL",
  DIMENSION = "DIMENSION",
  UNIT = "UNIT",
  STANDARD = "STANDARD",
  TOOL = "TOOL",
  SOFTWARE = "SOFTWARE",
  DATASET = "DATASET",
  MODEL = "MODEL",
  ALGORITHM = "ALGORITHM",
}

export interface EngineeringEntity {
  entityId: string;
  projectId: string;
  documentId: string;
  entityType: EngineeringEntityType;
  originalText: string;
  normalizedValue: string;
  unit?: string;
  pageNumber: number;
  section: string;
  confidence: number;
  sourceSpan: string;
  createdAt: number;
}
