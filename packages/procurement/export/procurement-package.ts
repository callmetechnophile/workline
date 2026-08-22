/**
 * Procurement Package schema for Phase 5 x402 handoff.
 */

export interface ProcurementPackageItem {
  manufacturer: string;
  partNumber: string;
  orderingCode: string;
  supplier: string;
  supplierItemId: string;
  quantity: number;
  unitPrice: number;
  currency: string;
  estimatedTotal: number;
  stock: number;
  leadTimeDays?: number;
  moq: number;
  validationStatus: "VALID" | "INCOMPLETE" | "BLOCKED";
}

export interface SupplierBreakdown {
  supplierId: string;
  itemCount: number;
  subtotal: number;
}

export interface ProcurementPackage {
  packageId: string;
  projectId: string;
  teamId: string;
  bomId: string;
  bomVersion: number;
  items: ProcurementPackageItem[];
  subtotal: number;
  currency: string;
  supplierBreakdown: SupplierBreakdown[];
  validationStatus: "READY" | "REVALIDATION_REQUIRED" | "BLOCKED";
  generatedAt: number;
}
