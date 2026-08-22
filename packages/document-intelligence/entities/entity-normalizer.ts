/**
 * Normalizes electrical and engineering quantities consistently.
 */

export class EntityNormalizer {
  public static normalizeVoltage(text: string): { normalized: string; unit: string } {
    const clean = text.trim();
    // Match 3V3 pattern
    const vMatch = clean.match(/^(\d+)V(\d+)$/i);
    if (vMatch) {
      return { normalized: `${vMatch[1]}.${vMatch[2]} V`, unit: "V" };
    }
    // Match 3.3V or 3.3 V
    const stdMatch = clean.match(/^([\d.]+)\s*(V|mV|kV)$/i);
    if (stdMatch) {
      return { normalized: `${stdMatch[1]} ${stdMatch[2].toUpperCase()}`, unit: stdMatch[2].toUpperCase() };
    }
    return { normalized: clean, unit: "V" };
  }

  public static normalizeCurrent(text: string): { normalized: string; unit: string } {
    const clean = text.trim();
    const match = clean.match(/^([\d.]+)\s*(A|mA|uA|µA)$/i);
    if (match) {
      return { normalized: `${match[1]} ${match[2]}`, unit: match[2] };
    }
    return { normalized: clean, unit: "A" };
  }

  public static normalizeTemperature(text: string): { normalized: string; unit: string } {
    const clean = text.trim();
    const match = clean.match(/^([+-]?[\d.]+)\s*(°C|C|K|°F|F)$/i);
    if (match) {
      return { normalized: `${match[1]} °C`, unit: "°C" };
    }
    return { normalized: clean, unit: "°C" };
  }
}
