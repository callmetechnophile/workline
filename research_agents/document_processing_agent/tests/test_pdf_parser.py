"""
Unit tests for PyMuPDF PDF parser (page boundaries, metadata, headings, tables, links).
"""

import pymupdf as fitz
from research_agents.document_processing_agent.parsers.pdf_parser import PDFDocumentParser


def create_sample_pdf_bytes() -> bytes:
    """Synthesizes a 2-page academic research PDF in-memory using PyMuPDF."""
    doc = fitz.open()
    doc.set_metadata({
        "title": "Thermal Human Detection on Edge UAVs",
        "author": "Alice Smith; Bob Jones",
        "creationDate": "D:20240501000000",
    })

    # Page 1
    page1 = doc.new_page()
    page1.insert_text((50, 60), "Thermal Human Detection on Edge UAVs", fontsize=18)
    page1.insert_text((50, 90), "Abstract", fontsize=14)
    page1.insert_text(
        (50, 110),
        "We present an autonomous thermal human detection pipeline for edge UAVs operating at 3.3 V supply voltage.\n"
        "The system runs YOLOv8 on Jetson Orin Nano hardware clocked at 240 MHz.\n",
        fontsize=11,
    )
    page1.insert_text((50, 170), "1. Introduction", fontsize=14)
    page1.insert_text(
        (50, 190),
        "Disaster search and rescue operations require rapid localization of victims.\n"
        "FLIR Lepton 3.5 thermal camera communicates with the MCU over SPI and I2C interfaces.\n"
        "Peak current consumption is 350 mA under maximum inference load.\n",
        fontsize=11,
    )

    # Page 2
    page2 = doc.new_page()
    page2.insert_text((50, 60), "2. Experimental Results", fontsize=14)
    page2.insert_text(
        (50, 80),
        "Figure 1: Thermal human detection precision vs frame rate.\n"
        "The edge inference model achieved 45 FPS on Jetson Orin Nano with 15 W power consumption.\n",
        fontsize=11,
    )
    page2.insert_text((50, 150), "References", fontsize=14)
    page2.insert_text(
        (50, 170),
        "[1] A. Smith, 'Edge Vision in Robotics,' IEEE Trans. Robotics, 2024, doi: 10.1109/TRO.2024.001.\n"
        "[2] B. Jones, 'Thermal UAV Search,' ICRA, 2023.\n",
        fontsize=10,
    )

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_pdf_parser_page_boundaries_and_metadata():
    pdf_bytes = create_sample_pdf_bytes()
    parser = PDFDocumentParser()

    meta, blocks, tables, figures, links, refs = parser.parse(
        content_bytes=pdf_bytes,
        source_url="https://example.com/paper.pdf",
    )

    assert meta.page_count == 2
    assert meta.title == "Thermal Human Detection on Edge UAVs"
    assert len(meta.authors) == 2
    assert "Alice Smith" in meta.authors[0]

    # Verify page distribution
    p1_blocks = [b for b in blocks if b.page_number == 1]
    p2_blocks = [b for b in blocks if b.page_number == 2]
    assert len(p1_blocks) >= 2
    assert len(p2_blocks) >= 2

    # Verify figures & references
    assert len(figures) >= 1
    assert "precision vs frame rate" in figures[0].caption

    assert len(refs) >= 2
    assert refs[0].doi == "10.1109/TRO.2024.001"
