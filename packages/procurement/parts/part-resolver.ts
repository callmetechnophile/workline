/**
 * Canonical component to ordering-code and variant resolver.
 */

export interface PartVariant {
  canonicalPart: string;
  orderingCode: string;
  manufacturer: string;
  package: string;
  packaging: string; // e.g. "Tape & Reel", "Cut Tape", "Tube"
  temperatureRange?: string;
  rohsCompliant: boolean;
}

export class PartResolver {
  public static resolveOrderingCode(
    canonicalPart: string,
    variants: PartVariant[]
  ): { resolved: boolean; exactMatch?: PartVariant; possibleVariants: PartVariant[]; isAmbiguous: boolean } {
    const matches = variants.filter(
      (v) =>
        v.canonicalPart.toUpperCase() === canonicalPart.toUpperCase() ||
        v.orderingCode.toUpperCase().startsWith(canonicalPart.toUpperCase())
    );

    if (matches.length === 0) {
      return { resolved: false, possibleVariants: [], isAmbiguous: false };
    }

    if (matches.length === 1) {
      return { resolved: true, exactMatch: matches[0], possibleVariants: matches, isAmbiguous: false };
    }

    return {
      resolved: false,
      possibleVariants: matches,
      isAmbiguous: true, // Multiple variants exist (e.g. RGTR vs RGTT)
    };
  }
}
