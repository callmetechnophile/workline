/**
 * Supplier offers, pricing breaks, and availability tracking.
 */

export interface QuantityBreak {
  quantity: number;
  unitPrice: number;
}

export interface SupplierOffer {
  supplierId: string;
  supplierItemId: string;
  manufacturer: string;
  partNumber: string;
  orderingCode: string;
  description: string;
  package: string;
  unitPrice: number;
  currency: string;
  quantityBreaks: QuantityBreak[];
  stock: number;
  leadTimeDays?: number;
  moq: number;
  urlReference?: string;
  retrievedAt: number;
  source: string;
  confidence: "HIGH" | "MEDIUM" | "LOW";
}

export class SupplierOfferEvaluator {
  public static isStale(offer: SupplierOffer, maxAgeHours: number = 24): boolean {
    const ageMs = Date.now() - offer.retrievedAt;
    return ageMs > maxAgeHours * 3600 * 1000;
  }

  public static getUnitPriceForQuantity(offer: SupplierOffer, qty: number): number {
    if (!offer.quantityBreaks || offer.quantityBreaks.length === 0) {
      return offer.unitPrice;
    }

    const sortedBreaks = [...offer.quantityBreaks].sort((a, b) => b.quantity - a.quantity);
    for (const qb of sortedBreaks) {
      if (qty >= qb.quantity) {
        return qb.unitPrice;
      }
    }

    return offer.unitPrice;
  }
}
