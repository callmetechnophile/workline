/**
 * Safe dimensional and unit conversion engine.
 */

import { PhysicalDimension, UnitDimensions } from "./unit-dimensions";

export interface ConversionResult {
  success: boolean;
  convertedValue?: number;
  error?: string;
}

export class UnitConverter {
  public static convert(
    value: number,
    fromUnitStr: string,
    toUnitStr: string
  ): ConversionResult {
    const fromUnit = UnitDimensions.getUnit(fromUnitStr);
    const toUnit = UnitDimensions.getUnit(toUnitStr);

    if (!fromUnit || !toUnit) {
      return {
        success: false,
        error: `Unrecognized unit(s): '${fromUnitStr}' or '${toUnitStr}'`,
      };
    }

    if (fromUnit.dimension !== toUnit.dimension) {
      return {
        success: false,
        error: `Incompatible dimensions: Cannot convert ${fromUnit.dimension} ('${fromUnitStr}') to ${toUnit.dimension} ('${toUnitStr}')`,
      };
    }

    // Convert from source to base, then base to target
    const baseValue = value * fromUnit.scaleToBase;
    const targetValue = baseValue / toUnit.scaleToBase;

    return {
      success: true,
      convertedValue: targetValue,
    };
  }
}
