"""Tests for WORKLINE .wl Project Filesystem & Data Portability."""

import json
import io
import zipfile
import pytest
from backend.routes.project_data import serialize_to_wl_filemap


SAMPLE_PROJECT = {
    "project_id": "PROJ-AUTO-DRONE",
    "name": "Autonomous Delivery Drone Power Distribution",
    "domain": "Hardware Systems & Power Engineering",
    "status": "ACTIVE",
    "system_specification": "Autonomous high-efficiency buck-boost power distribution network.",
    "architecture": {
        "blocks": [
            {"id": "b1", "name": "Power Distribution Subsystem"},
            {"id": "b2", "name": "Safety Supervisor MCU"},
        ],
        "connections": [{"from": "b1", "to": "b2", "type": "POWER"}],
    },
    "bom": {
        "components": [
            {
                "mpn": "TPS62160DGKR",
                "manufacturer": "Texas Instruments",
                "quantity": 2,
                "price": 2.45,
                "description": "Step-down converter",
                "supplier": "DigiKey",
            },
            {
                "mpn": "STM32G474RET6",
                "manufacturer": "STMicroelectronics",
                "quantity": 1,
                "price": 8.50,
                "description": "ARM Cortex-M4 MCU with high-resolution timers",
                "supplier": "Mouser",
            },
        ],
    },
    "requirements": {
        "requirements": [
            {"id": "REQ-01", "title": "Input Voltage Regulation", "category": "functional"},
            {"id": "REQ-02", "title": "Ripple Suppression < 25mV", "category": "technical"},
        ]
    },
    "research": {
        "papers": [
            {"id": "PAPER-01", "title": "High-Density Synchronous Power Stages", "source": "IEEE Xplore"}
        ]
    },
}


def test_wl_filesystem_contains_required_files():
    """Verify all standard required directories and files are present."""
    file_map = serialize_to_wl_filemap(SAMPLE_PROJECT, {"project_name": SAMPLE_PROJECT["name"], "project_id": SAMPLE_PROJECT["project_id"]})
    
    # 1. Root discovery files
    assert "README.wl" in file_map
    assert ".wl/manifest.wl" in file_map
    assert ".wl/project.wl" in file_map
    assert ".wl/dependencies.wl" in file_map

    # 2. Engineering modules
    assert "requirements/functional.wl" in file_map
    assert "requirements/technical.wl" in file_map
    assert "architecture/system.wl" in file_map
    assert "architecture/architecture.json" in file_map
    assert "bom/bom.wl" in file_map
    assert "bom/bom.csv" in file_map
    assert "research/index.wl" in file_map
    assert "analysis/power.wl" in file_map
    assert "analysis/thermal.wl" in file_map
    assert "analysis/pcb.wl" in file_map
    assert "decisions/index.wl" in file_map
    assert "tasks/index.wl" in file_map
    assert "team/members.wl" in file_map
    assert "agents/index.wl" in file_map
    assert "history/activity.wl" in file_map


def test_strict_zero_secrets_invariant():
    """Verify no tokens, credentials or private keys are ever exported."""
    file_map = serialize_to_wl_filemap(SAMPLE_PROJECT, {"project_name": SAMPLE_PROJECT["name"]})
    
    # Check dependencies.wl
    deps_content = file_map[".wl/dependencies.wl"]
    assert "credentials: NOT_EXPORTED" in deps_content
    assert "sk-" not in deps_content
    assert "AKIA" not in deps_content

    # Check .gitignore
    assert ".env" in file_map[".gitignore"]
    assert "cache/" in file_map[".worklineignore"]


def test_readme_wl_structure():
    """Verify README.wl contains structured fields for CLI consumption."""
    file_map = serialize_to_wl_filemap(SAMPLE_PROJECT, {"project_name": SAMPLE_PROJECT["name"], "project_id": SAMPLE_PROJECT["project_id"]})
    readme = file_map["README.wl"]

    assert "WORKLINE_PROJECT" in readme
    assert "Autonomous Delivery Drone Power Distribution" in readme
    assert "PROJ-AUTO-DRONE" in readme
    assert "manifest: .wl/manifest.wl" in readme
    assert "entry: README.wl" in readme


def test_zip_archive_packaging_and_restoration():
    """Verify packaging into zip and round-trip decompression."""
    file_map = serialize_to_wl_filemap(SAMPLE_PROJECT, {"project_name": SAMPLE_PROJECT["name"]})
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for p, c in file_map.items():
            zf.writestr(p, c)

    zip_buffer.seek(0)
    
    # Read back
    restored: dict = {}
    with zipfile.ZipFile(zip_buffer, "r") as zf:
        for info in zf.infolist():
            if not info.is_dir():
                restored[info.filename] = zf.read(info).decode("utf-8")

    assert "README.wl" in restored
    assert ".wl/manifest.wl" in restored
    assert restored["README.wl"] == file_map["README.wl"]
    assert len(restored) == len(file_map)
