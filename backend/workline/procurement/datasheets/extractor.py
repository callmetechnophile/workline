"""Technical text and specification extractor for verified engineering datasheets."""

import re
from typing import Any, Dict, List, Optional
from backend.workline.procurement.models import (
    ElectricalSpecs,
    EnvironmentSpecs,
    InterfaceSpecs,
    PhysicalSpecs,
)


class DatasheetExtractor:
    """Extracts electrical limits, pinouts, and hardware specifications from datasheet text chunks."""

    def extract_specs_from_text(self, text: str) -> Dict[str, Any]:
        """Parse raw extracted datasheet text into structured specifications."""
        electrical = ElectricalSpecs()
        physical = PhysicalSpecs()
        interfaces = InterfaceSpecs()

        clean_text = text.lower()

        # Voltages
        v_match = re.search(r'([0-9.]+)\s*v\s*(?:to|-)\s*([0-9.]+)\s*v', clean_text)
        if v_match:
            try:
                electrical.voltage_min = float(v_match.group(1))
                electrical.voltage_max = float(v_match.group(2))
            except ValueError:
                pass

        v_nom = re.search(r'(?:output|nominal)?\s*voltage[:\s-]*([0-9.]+)\s*v', clean_text)
        if v_nom:
            try:
                electrical.nominal_voltage = float(v_nom.group(1))
            except ValueError:
                pass

        # Currents
        cur_match = re.search(r'(?:output\s+)?current[:\s-]*([0-9.]+)\s*(a|ma)', clean_text) or re.search(r'([0-9.]+)\s*(a|ma)\s*(?:output|max|current)', clean_text)
        if cur_match:
            try:
                val = float(cur_match.group(1))
                unit = cur_match.group(2) if len(cur_match.groups()) > 1 else ""
                if "ma" in unit.lower() or "ma" in cur_match.group(0):
                    val = val / 1000.0
                electrical.current_max = val
            except ValueError:
                pass

        # Interfaces
        interfaces.i2c = "i2c" in clean_text
        interfaces.spi = "spi" in clean_text
        interfaces.uart = "uart" in clean_text
        interfaces.can = "can" in clean_text
        interfaces.usb = "usb" in clean_text

        return {
            "electrical": electrical.model_dump(),
            "physical": physical.model_dump(),
            "interfaces": interfaces.model_dump(),
        }

    def chunk_document_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split datasheet text into overlapping chunks for semantic Qdrant vector indexing."""
        words = text.split()
        chunks: List[str] = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks or [text]
