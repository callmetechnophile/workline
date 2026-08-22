"""Extracts electrical, physical, and interface parameters from raw vendor specification tables."""

import re
from typing import Any, Dict, Optional, Tuple
from backend.workline.scraping.models import (
    ElectricalSpecs,
    EnvironmentSpecs,
    InterfaceSpecs,
    PhysicalSpecs,
)


class ComponentExtractor:
    """Parses raw text and key-value spec tables into structured hardware specifications."""

    def extract_electrical(self, spec_table: Dict[str, str], text: str = "") -> ElectricalSpecs:
        combined = " ".join([f"{k}: {v}" for k, v in spec_table.items()]) + " " + text
        specs = ElectricalSpecs(raw_specs=dict(spec_table))

        # Extract nominal voltage / output voltage
        v_nom_patterns = [
            r'voltage\s*-\s*output\s*(?:\(nom\))?[:\s-]*([0-9.]+)\s*v',
            r'(?:output|nominal)\s*voltage[:\s-]*([0-9.]+)\s*v',
            r'([0-9.]+)\s*v\s*(?:output|nominal)',
        ]
        for pat in v_nom_patterns:
            m = re.search(pat, combined, re.IGNORECASE)
            if m:
                try:
                    specs.nominal_voltage = float(m.group(1))
                    break
                except ValueError:
                    pass

        # Extract min input voltage
        v_min_patterns = [
            r'voltage\s*-\s*input\s*(?:\(min\))?[:\s-]*([0-9.]+)\s*v',
            r'(?:input|supply|operating)?\s*voltage\s*(?:min)?[:\s-]*([0-9.]+)\s*v',
        ]
        for pat in v_min_patterns:
            m = re.search(pat, combined, re.IGNORECASE)
            if m:
                try:
                    specs.voltage_min = float(m.group(1))
                    break
                except ValueError:
                    pass

        # Extract max input voltage
        v_max_patterns = [
            r'voltage\s*-\s*input\s*(?:\(max\))?[:\s-]*([0-9.]+)\s*v',
            r'to\s*([0-9.]+)\s*v',
            r'([0-9.]+)\s*v\s*(?:max)',
        ]
        for pat in v_max_patterns:
            m = re.search(pat, combined, re.IGNORECASE)
            if m:
                try:
                    specs.voltage_max = float(m.group(1))
                    break
                except ValueError:
                    pass

        # Extract currents
        cur_patterns = [
            r'current\s*-\s*output[:\s-]*([0-9.]+)\s*(?:a|ma)?',
            r'(?:current|output current)[:\s-]*([0-9.]+)\s*(?:a|ma)',
            r'([0-9.]+)\s*a\s*(?:output|max|current)',
        ]
        for pat in cur_patterns:
            m = re.search(pat, combined, re.IGNORECASE)
            if m:
                try:
                    val = float(m.group(1))
                    if "ma" in m.group(0).lower():
                        val = val / 1000.0
                    specs.current_max = val
                    break
                except ValueError:
                    pass

        return specs

    def extract_physical(self, spec_table: Dict[str, str], text: str = "") -> PhysicalSpecs:
        combined = " ".join([f"{k}: {v}" for k, v in spec_table.items()]) + " " + text
        physical = PhysicalSpecs()

        pkg_match = re.search(r'(?:package|case|mounting style)[:\s-]*([A-Za-z0-9_/-]+)', combined, re.IGNORECASE)
        if pkg_match:
            physical.package = pkg_match.group(1).strip()

        if "smd" in combined.lower() or "smt" in combined.lower():
            physical.mounting_type = "SMD"
        elif "through-hole" in combined.lower() or "dip" in combined.lower():
            physical.mounting_type = "Through-Hole"
        elif "module" in combined.lower():
            physical.mounting_type = "Module"

        return physical

    def extract_interfaces(self, spec_table: Dict[str, str], text: str = "") -> InterfaceSpecs:
        combined = (" ".join([f"{k}: {v}" for k, v in spec_table.items()]) + " " + text).lower()
        return InterfaceSpecs(
            i2c="i2c" in combined or "iic" in combined,
            spi="spi" in combined,
            uart="uart" in combined or "usart" in combined or "serial" in combined,
            can="can bus" in combined or " can " in combined,
            usb="usb" in combined or "type-c" in combined,
            ethernet="ethernet" in combined or "rj45" in combined,
            adc_channels=1 if ("adc" in combined or "analog" in combined) else None,
            pwm_channels=2 if ("pwm" in combined or "motor" in combined) else None,
        )

    def extract_environment(self, spec_table: Dict[str, str], text: str = "") -> EnvironmentSpecs:
        combined = " ".join([f"{k}: {v}" for k, v in spec_table.items()]) + " " + text
        env = EnvironmentSpecs()

        temp_match = re.search(r'(-?[0-9]+)\s*°?c\s*(?:~|to|-)\s*(\+?[0-9]+)\s*°?c', combined, re.IGNORECASE)
        if temp_match:
            try:
                env.temperature_min_c = float(temp_match.group(1))
                env.temperature_max_c = float(temp_match.group(2))
                env.operating_temp_range = f"{temp_match.group(1)}°C to {temp_match.group(2)}°C"
            except ValueError:
                pass

        return env
