/**
 * PCB Schematic, Net, Pin, and Connectivity models.
 */

export enum ElectricalPinType {
  POWER_IN = "POWER_IN",
  POWER_OUT = "POWER_OUT",
  GROUND = "GROUND",
  DIGITAL_IN = "DIGITAL_IN",
  DIGITAL_OUT = "DIGITAL_OUT",
  ANALOG_IN = "ANALOG_IN",
  ANALOG_OUT = "ANALOG_OUT",
  BIDIRECTIONAL = "BIDIRECTIONAL",
  CLOCK = "CLOCK",
  RESET = "RESET",
  CONTROL = "CONTROL",
  NC = "NC",
  UNKNOWN = "UNKNOWN",
}

export enum NetType {
  POWER = "POWER",
  GROUND = "GROUND",
  ANALOG = "ANALOG",
  DIGITAL = "DIGITAL",
  CLOCK = "CLOCK",
  HIGH_SPEED = "HIGH_SPEED",
  DIFFERENTIAL = "DIFFERENTIAL",
  CONTROL = "CONTROL",
  RESET = "RESET",
  OTHER = "OTHER",
}

export interface PCBPin {
  pinId: string;
  componentId: string;
  pinNumber: string;
  pinName: string;
  electricalType: ElectricalPinType;
  signalType?: string;
  voltageDomain?: number;
  currentDomain?: number;
  defaultState?: string;
  sourceDocument?: string;
  sourcePage?: number;
}

export interface Net {
  netId: string;
  name: string;
  netType: NetType;
  voltage?: number;
  current?: number;
  sourcePin?: string;
  destinationPins: string[];
  constraints: string[];
}
