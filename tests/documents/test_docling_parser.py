"""Tests for Docling document structure extraction, tables, and page provenance."""

import pytest
from backend.workline.documents.docling.parser import DoclingParser
from backend.workline.documents.models import DocumentStatus, SourceType


def test_docling_structure_and_table_extraction():
    content = """# TPS62130 3A Step-Down Converter
This is the introduction to the synchronous step-down DC-DC converter.

## Electrical Characteristics
The device operates from 3V to 17V input supply rails.

| Parameter | Min | Typ | Max | Unit |
| --- | --- | --- | --- | --- |
| Input Voltage | 3.0 | - | 17.0 | V |
| Output Current | - | - | 3.0 | A |
| Quiescent Current | - | 17 | 30 | uA |

Page 2
## Application Information
Typical output voltage is set to 3.3V or 5V using an external resistor divider network.
"""

    doc = DoclingParser.parse(
        document_id="DOC-TPS62130",
        project_id="rover_v2",
        raw_content=content,
        filename="TPS62130_Datasheet.pdf",
        source_type=SourceType.DATASHEET,
    )

    assert doc.document_id == "DOC-TPS62130"
    assert doc.status == DocumentStatus.PARSED
    assert len(doc.sections) >= 3

    # Check Electrical Characteristics section and table
    elec_sec = next((s for s in doc.sections if "Electrical" in s.heading), None)
    assert elec_sec is not None
    assert len(elec_sec.tables) == 1

    tbl = elec_sec.tables[0]
    assert tbl.headers == ["Parameter", "Min", "Typ", "Max", "Unit"]
    assert len(tbl.rows) == 3
    assert tbl.rows[0] == ["Input Voltage", "3.0", "-", "17.0", "V"]
    assert tbl.rows[1] == ["Output Current", "-", "-", "3.0", "A"]

    # Check page numbering
    app_sec = next((s for s in doc.sections if "Application" in s.heading), None)
    assert app_sec is not None
    assert app_sec.page_number == 2
