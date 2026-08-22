/**
 * Bill of Materials (BOM) schemas, item structures, and statuses.
 */

export enum BomStatus {
  DRAFT = "DRAFT",
  GENERATED = "GENERATED",
  VALIDATED = "VALIDATED",
  READY_FOR_PROCUREMENT = "READY_FOR_PROCUREMENT",
  PARTIALLY_RESOLVED = "PARTIALLY_RESOLVED",
  BLOCKED = "BLOCKED",
  SUPERSEDED = "SUPERSEDED",
}

export enum ProcurementStatus {
  UNRESOLVED = "UNRESOLVED",
  RESOLVED = "RESOLVED",
  AVAILABLE = "AVAILABLE",
  PARTIAL = "PARTIAL",
  OUT_OF_STOCK = "OUT_OF_STOCK",
  AMBIGUOUS = "AMBIGUOUS",
  BLOCKED = "BLOCKED",
}

export interface BomItem {
  bomItemId: string;
  bomId: string;
  referenceDesignator: string; // e.g. "U1", "R1, R2, R3"
  description: string;
  componentEntityId: string;
  partNumber: string;
  manufacturer: string;
  orderingCode: string;
  package: string;
  quantity: number;
  unit: string;
  requiredQuantity: number;
  selectedSupplier?: string;
  supplierItemId?: string;
  unitPrice?: number;
  currency: string;
  stock: number;
  leadTimeDays?: number;
  moq: number;
  status: ProcurementStatus;
  confidence: "HIGH" | "MEDIUM" | "LOW";
  evidence: string[];
  createdAt: number;
  updatedAt: number;
}

export interface BillOfMaterials {
  bomId: string;
  projectId: string;
  teamId: string;
  version: number;
  status: BomStatus;
  sourceDecisions: string[];
  items: BomItem[];
  currency: string;
  estimatedTotal: number;
  createdAt: number;
  updatedAt: number;
}
