/**
 * Pricing Engine and Currency Normalization.
 */

import { BomItem } from "../bom/bom-schema";
import { SupplierOffer, SupplierOfferEvaluator } from "../suppliers/supplier-offer";

export class PriceEngine {
  public static calculateLineItem(item: BomItem, offer?: SupplierOffer): { lineTotal: number; unitPrice: number } {
    if (!offer) {
      return { lineTotal: 0.0, unitPrice: item.unitPrice || 0.0 };
    }

    const unitPrice = SupplierOfferEvaluator.getUnitPriceForQuantity(offer, item.quantity);
    const lineTotal = Number((unitPrice * item.quantity).toFixed(2));
    return { lineTotal, unitPrice };
  }

  public static calculateBomSubtotal(items: BomItem[]): number {
    const total = items.reduce((acc, item) => acc + (item.unitPrice || 0.0) * item.quantity, 0.0);
    return Number(total.toFixed(2));
  }
}
