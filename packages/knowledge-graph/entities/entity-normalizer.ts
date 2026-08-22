/**
 * Deterministic unit and value normalizer for engineering quantities.
 */

export interface NormalizedQuantity {
  originalValue: string;
  originalUnit: string;
  normalizedValue: number;
  baseUnit: string;
}

export class EntityNormalizer {
  public static parseQuantity(text: string): NormalizedQuantity | null {
    const clean = text.trim();

    // Voltage (e.g. 3V3, 3.3V, 500mV)
    const v3Match = clean.match(/^(\d+)V(\d+)$/i);
    if (v3Match) {
      const val = parseFloat(`${v3Match[1]}.${v3Match[2]}`);
      return { originalValue: clean, originalUnit: "V", normalizedValue: val, baseUnit: "V" };
    }

    const voltMatch = clean.match(/^([\d.]+)\s*(V|mV|kV)$/i);
    if (voltMatch) {
      const rawVal = parseFloat(voltMatch[1]);
      const unit = voltMatch[2].toUpperCase();
      let scale = 1.0;
      if (unit === "MV") scale = 0.001;
      if (unit === "KV") scale = 1000.0;
      return { originalValue: clean, originalUnit: voltMatch[2], normalizedValue: rawVal * scale, baseUnit: "V" };
    }

    // Current (e.g. 3A, 500mA, 20uA)
    const currMatch = clean.match(/^([\d.]+)\s*(A|mA|uA|µA)$/i);
    if (currMatch) {
      const rawVal = parseFloat(currMatch[1]);
      const unit = currMatch[2];
      let scale = 1.0;
      if (unit.toLowerCase() === "ma") scale = 0.001;
      if (unit.toLowerCase() === "ua" || unit === "µA") scale = 0.000001;
      return { originalValue: clean, originalUnit: unit, normalizedValue: rawVal * scale, baseUnit: "A" };
    }

    // Resistance (e.g. 10kΩ, 100R, 4.7M)
    const resMatch = clean.match(/^([\d.]+)\s*(Ω|kΩ|MΩ|ohm|kohm|Mohm|R|k|M)$/i);
    if (resMatch) {
      const rawVal = parseFloat(resMatch[1]);
      const unit = resMatch[2];
      let scale = 1.0;
      if (unit.startsWith("k") || unit.startsWith("K")) scale = 1000.0;
      if (unit.startsWith("M") || unit.startsWith("m")) scale = 1000000.0;
      return { originalValue: clean, originalUnit: unit, normalizedValue: rawVal * scale, baseUnit: "Ω" };
    }

    // Frequency (e.g. 16MHz, 100kHz, 2.4GHz)
    const freqMatch = clean.match(/^([\d.]+)\s*(Hz|kHz|MHz|GHz)$/i);
    if (freqMatch) {
      const rawVal = parseFloat(freqMatch[1]);
      const unit = freqMatch[2].toUpperCase();
      let scale = 1.0;
      if (unit === "KHZ") scale = 1000.0;
      if (unit === "MHZ") scale = 1000000.0;
      if (unit === "GHZ") scale = 1000000000.0;
      return { originalValue: clean, originalUnit: freqMatch[2], normalizedValue: rawVal * scale, baseUnit: "Hz" };
    }

    // Temperature (e.g. 125°C, -40C)
    const tempMatch = clean.match(/^([+-]?[\d.]+)\s*(°C|C|K)$/i);
    if (tempMatch) {
      const rawVal = parseFloat(tempMatch[1]);
      return { originalValue: clean, originalUnit: "°C", normalizedValue: rawVal, baseUnit: "°C" };
    }

    return null;
  }
}
