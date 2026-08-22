"""Comprehensive round-trip test: Project A -> Export -> .wlipjt -> Import -> Project B -> Verify Equivalence."""

import json
from pathlib import Path
import pytest

from backend.workline.git.repository import ProjectRepositoryManager
from backend.workline.project.export_service import ExportService
from backend.workline.project.import_service import ImportService
from backend.workline.project.inspector import PackageInspector
from backend.workline.project.models import ExportOptions, ImportStrategy


def test_complete_project_roundtrip(tmp_path: Path):
    """
    Round-trip verification:
    1. Construct Project A with complex state (PCB, BOM, components, nets, artifacts)
    2. Export to .wlipjt
    3. Import into Project B
    4. Assert state equivalence
    """
    ws = tmp_path / "workspace"
    ws.mkdir(parents=True)

    # 1. Setup Project A
    proj_a = ws / "autonomous-rover-v1"
    proj_a.mkdir(parents=True)
    mgr = ProjectRepositoryManager()
    mgr.init_project_git(proj_a, "autonomous-rover-v1", "Autonomous Rover", project_version="0.4.0")

    pcb_state = {
        "board": {"width": 100.0, "height": 80.0, "layers": 4},
        "components": [
            {"id": "U1", "mpn": "STM32H743ZI", "footprint": "LQFP144"},
            {"id": "U2", "mpn": "DRV8833", "footprint": "TSSOP16"},
            {"id": "R1", "mpn": "RC0603FR-0710KL", "footprint": "0603"},
        ],
        "nets": [
            {"name": "VCC_3V3", "pins": ["U1:1", "R1:1"]},
            {"name": "GND", "pins": ["U1:2", "U2:2", "R1:2"]},
            {"name": "MOTOR_PWM", "pins": ["U1:10", "U2:5"]},
        ],
        "bom": [
            {"mpn": "STM32H743ZI", "quantity": 1, "unit_price": 12.50},
            {"mpn": "DRV8833", "quantity": 2, "unit_price": 2.10},
        ],
        "power_tree": {"rails": ["3.3V", "5V"], "max_power": 8.5},
        "thermal": {"max_temp_c": 55.0},
    }
    (proj_a / ".workline" / "pcb.wlpcb").write_text(json.dumps(pcb_state, indent=2), encoding="utf-8")

    # Artifacts
    art_dir = proj_a / "artifacts"
    art_dir.mkdir(parents=True)
    (art_dir / "pinn_thermal_model.pt").write_bytes(b"PYTORCH_PINN_CHECKPOINT_DATA_12345")

    # 2. Export Project A
    exporter = ExportService()
    pkg_file, manifest_a, warnings = exporter.export_project(
        proj_a,
        output_file=tmp_path / "rover.wlipjt",
        options=ExportOptions(include_artifacts=True),
    )

    assert pkg_file.exists()
    assert manifest_a.components_count == 3
    assert manifest_a.nets_count == 3
    assert manifest_a.bom_count == 2
    assert manifest_a.artifacts_count == 1

    # 3. Import into Project B
    importer = ImportService()
    proj_b, manifest_b = importer.import_project(
        package_path=pkg_file,
        target_project_name="autonomous-rover-v2",
        strategy=ImportStrategy.NEW_PROJECT,
        workspace_path=ws,
    )

    assert proj_b.exists()
    assert manifest_b.project_id == "autonomous-rover-v2"
    assert manifest_b.project_version == "0.4.0"

    # 4. Verify Equivalence
    # Read restored PCB state
    restored_pcb_file = proj_b / ".workline" / "pcb.wlpcb"
    assert restored_pcb_file.exists()
    restored_pcb = json.loads(restored_pcb_file.read_text(encoding="utf-8"))

    assert len(restored_pcb["components"]) == 3
    assert len(restored_pcb["nets"]) == 3
    assert len(restored_pcb["bom"]) == 2
    assert restored_pcb["board"]["width"] == 100.0

    # Verify restored artifact
    restored_art = proj_b / "artifacts" / "pinn_thermal_model.pt"
    assert restored_art.exists()
    assert restored_art.read_bytes() == b"PYTORCH_PINN_CHECKPOINT_DATA_12345"

    # Verify Git state
    assert (proj_b / ".git").exists()
    assert (proj_b / ".workline" / "project.toon").exists()
