/**
 * Engineering Unit Dimensions and scaling factors.
 */

export enum PhysicalDimension {
  VOLTAGE = "VOLTAGE",
  CURRENT = "CURRENT",
  POWER = "POWER",
  RESISTANCE = "RESISTANCE",
  CAPACITANCE = "CAPACITANCE",
  INDUCTANCE = "INDUCTANCE",
  FREQUENCY = "FREQUENCY",
  TEMPERATURE = "TEMPERATURE",
  LENGTH = "LENGTH",
  WEIGHT = "WEIGHT",
  DIMENSIONLESS = "DIMENSIONLESS",
}

export interface UnitDefinition {
  symbol: string;
  dimension: PhysicalDimension;
  scaleToBase: number;
}

export class UnitDimensions {
  public static readonly UNIT_TABLE: Record<string, UnitDefinition> = {
    // Voltage
    V: { symbol: "V", dimension: PhysicalDimension.VOLTAGE, scaleToBase: 1.0 },
    MV: { symbol: "mV", dimension: PhysicalDimension.VOLTAGE, scaleToBase: 0.001 },
    KV: { symbol: "kV", dimension: PhysicalDimension.VOLTAGE, scaleToBase: 1000.0 },

    // Current
    A: { symbol: "A", dimension: PhysicalDimension.CURRENT, scaleToBase: 1.0 },
    MA: { symbol: "mA", dimension: PhysicalDimension.CURRENT, scaleToBase: 0.001 },
    UA: { symbol: "uA", dimension: PhysicalDimension.CURRENT, scaleToBase: 0.000001 },
    "µA": { symbol: "µA", dimension: PhysicalDimension.CURRENT, scaleToBase: 0.000001 },

    // Power
    W: { symbol: "W", dimension: PhysicalDimension.POWER, scaleToBase: 1.0 },
    MW: { symbol: "mW", dimension: PhysicalDimension.POWER, scaleToBase: 0.001 },
    KW: { symbol: "kW", dimension: PhysicalDimension.POWER, scaleToBase: 1000.0 },

    // Resistance
    OHM: { symbol: "Ω", dimension: PhysicalDimension.RESISTANCE, scaleToBase: 1.0 },
    "Ω": { symbol: "Ω", dimension: PhysicalDimension.RESISTANCE, scaleToBase: 1.0 },
    KOHM: { symbol: "kΩ", dimension: PhysicalDimension.RESISTANCE, scaleToBase: 1000.0 },
    "KΩ": { symbol: "kΩ", dimension: PhysicalDimension.RESISTANCE, scaleToBase: 1000.0 },
    MOHM: { symbol: "MΩ", dimension: PhysicalDimension.RESISTANCE, scaleToBase: 1000000.0 },
    "MΩ": { symbol: "MΩ", dimension: PhysicalDimension.RESISTANCE, scaleToBase: 1000000.0 },

    // Frequency
    HZ: { symbol: "Hz", dimension: PhysicalDimension.FREQUENCY, scaleToBase: 1.0 },
    KHZ: { symbol: "kHz", dimension: PhysicalDimension.FREQUENCY, scaleToBase: 1000.0 },
    MHZ: { symbol: "MHz", dimension: PhysicalDimension.FREQUENCY, scaleToBase: 1000000.0 },
    GHZ: { symbol: "GHz", dimension: PhysicalDimension.FREQUENCY, scaleToBase: 1000000000.0 },

    // Temperature
    "°C": { symbol: "°C", dimension: PhysicalDimension.TEMPERATURE, scaleToBase: 1.0 },
    C: { symbol: "°C", dimension: PhysicalDimension.TEMPERATURE, scaleToBase: 1.0 },
  };

  public static getUnit(symbol: string): UnitDefinition | undefined {
    return this.UNIT_TABLE[symbol.toUpperCase()] || this.UNIT_TABLE[symbol];
  }
}
