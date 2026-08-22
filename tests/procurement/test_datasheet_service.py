"""Unit and integration tests for Datasheet discovery, verification, and indexing."""

import asyncio
import pytest
from backend.workline.database.repositories.graph_repository import GraphRepository
from backend.workline.procurement.datasheets.extractor import DatasheetExtractor
from backend.workline.procurement.datasheets.service import DatasheetService
from backend.workline.procurement.datasheets.verifier import DatasheetVerifier
from backend.workline.procurement.models import DatasheetMetadata, DatasheetStatus


def test_datasheet_verifier():
    """Test verification rules: trusted domains, reachability, and MPN matching."""
    verifier = DatasheetVerifier()

    # Verified TI datasheet
    ds_ti = DatasheetMetadata(
        datasheet_id="ds_ti",
        url="https://www.ti.com/lit/ds/symlink/tps62130.pdf",
        manufacturer="Texas Instruments",
        mpn="TPS62130",
    )
    status, msg = verifier.verify(ds_ti, "Texas Instruments", "TPS62130")
    assert status == DatasheetStatus.VERIFIED

    # Invalid URL scheme
    ds_bad = DatasheetMetadata(
        datasheet_id="ds_bad",
        url="ftp://invalid.com/file.bin",
    )
    status_bad, _ = verifier.verify(ds_bad)
    assert status_bad == DatasheetStatus.FAILED


def test_datasheet_extractor():
    """Test text spec parsing and document chunking."""
    extractor = DatasheetExtractor()
    sample_text = "Input Voltage 3.0V to 17.0V. Output Current 3A max. I2C and SPI supported."
    specs = extractor.extract_specs_from_text(sample_text)

    assert specs["electrical"]["voltage_min"] == 3.0
    assert specs["electrical"]["voltage_max"] == 17.0
    assert specs["electrical"]["current_max"] == 3.0
    assert specs["interfaces"]["i2c"] is True
    assert specs["interfaces"]["spi"] is True


def test_datasheet_service_indexing():
    """Test end-to-end datasheet verification and graph/vector indexing."""
    async def _run():
        graph_repo = GraphRepository()
        service = DatasheetService(graph_repo=graph_repo)

        ds = DatasheetMetadata(
            datasheet_id="ds_esp32",
            url="https://www.espressif.com/documentation/esp32-s3_datasheet_en.pdf",
            manufacturer="Espressif Systems",
            mpn="ESP32-S3",
            title="ESP32-S3 Datasheet",
            document_type="Datasheet",
        )

        verified_ds = await service.verify_and_index(
            ds, project_id="rover_proj", component_id="component:espressif_esp32_s3"
        )
        assert verified_ds.verification_status == DatasheetStatus.VERIFIED

        # Verify SurrealDB node and edge
        graph = await graph_repo.get_project_graph("rover_proj")
        node_types = [n.type for n in graph.nodes]
        edge_rels = [e.relationship for e in graph.edges]
        assert "Datasheet" in node_types
        assert "HAS_DATASHEET" in edge_rels

    asyncio.run(_run())
