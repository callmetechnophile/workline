"""Tests for FastAPI document endpoints and CLI document subcommands."""

import os
from fastapi.testclient import TestClient
import pytest
from typer.testing import CliRunner
from backend.main import app as fastapi_app
from backend.workline.documents.service import document_service
from cli.wline.main import app as cli_app

client = TestClient(fastapi_app)
runner = CliRunner()


def test_fastapi_document_endpoints():
    # 1. Ingest
    payload = {
        "document_id": "DOC-API-101",
        "project_id": "rover_v2",
        "content": "# Battery System\nLiPo 4S battery with 14.8V nominal and 5000mAh capacity.",
        "filename": "battery.md",
        "source_type": "DATASHEET",
    }
    res = client.post("/api/documents/ingest", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["document_id"] == "DOC-API-101"
    assert data["status"] == "INDEXED"

    # 2. Get document
    res_get = client.get("/api/documents/DOC-API-101")
    assert res_get.status_code == 200
    assert res_get.json()["title"] == "Battery System"

    # 3. Get entities
    res_ent = client.get("/api/documents/DOC-API-101/entities")
    assert res_ent.status_code == 200
    entities = res_ent.json()
    assert any(e["normalized_value"] == "14.8 V" for e in entities)

    # 4. Get structure
    res_struct = client.get("/api/documents/DOC-API-101/structure")
    assert res_struct.status_code == 200
    assert len(res_struct.json()["sections"]) >= 1

    # 5. Delete
    res_del = client.delete("/api/documents/DOC-API-101")
    assert res_del.status_code == 200
    assert res_del.json()["status"] == "DELETED"


def test_cli_document_subcommands(tmp_path):
    doc_file = tmp_path / "sensor.md"
    doc_file.write_text("# IMU Sensor\nMPU6050 6-axis gyro operates at 3.3V.", encoding="utf-8")

    # Ingest CLI
    res = runner.invoke(cli_app, ["document", "ingest", str(doc_file), "-p", "rover_v2", "--id", "DOC-IMU"])
    assert res.exit_code == 0
    assert "Document Ingested Successfully" in res.stdout

    # List CLI
    res_list = runner.invoke(cli_app, ["document", "list"])
    assert res_list.exit_code == 0
    assert "DOC-IMU" in res_list.stdout

    # Info CLI
    res_info = runner.invoke(cli_app, ["document", "info", "DOC-IMU"])
    assert res_info.exit_code == 0
    assert "IMU Sensor" in res_info.stdout

    # Entities CLI
    res_ent = runner.invoke(cli_app, ["document", "entities", "DOC-IMU"])
    assert res_ent.exit_code == 0
    assert "MPU6050" in res_ent.stdout

    # Reindex CLI
    res_re = runner.invoke(cli_app, ["document", "reindex", "DOC-IMU"])
    assert res_re.exit_code == 0
    assert "reindexed successfully" in res_re.stdout

    # Remove CLI
    res_rem = runner.invoke(cli_app, ["document", "remove", "DOC-IMU"])
    assert res_rem.exit_code == 0
    assert "removed" in res_rem.stdout
