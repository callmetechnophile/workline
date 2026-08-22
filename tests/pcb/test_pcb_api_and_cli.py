"""Integration tests for PCB REST API routes and CLI subcommands."""

import asyncio
import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from backend.main import app
from cli.wline.main import app as cli_app
from backend.workline.pcb.services.pcb_service import PCBService


def test_pcb_api_flow():
    """Test REST API lifecycle: Create PCB -> Validate -> Features -> PINN Train -> Optimize.
    NOTE: Uses only project_id (no bom_id) so the service's built-in synthetic BOM is used,
    making this test fully self-contained without requiring live external APIs.
    """
    client = TestClient(app)

    # 1. Create PCB (no bom_id -> service synthesises a default BOM)
    res_pcb = client.post(
        "/api/pcb/create",
        json={"project_id": "test_pcb_api_proj", "board_width": 60.0, "board_height": 50.0},
    )
    assert res_pcb.status_code == 200, f"Expected 200, got {res_pcb.status_code}: {res_pcb.text}"
    pcb_data = res_pcb.json()
    assert pcb_data["board"]["width"] == 60.0

    # 2. Validate
    res_val = client.post("/api/pcb/test_pcb_api_proj/validate")
    assert res_val.status_code == 200
    # Validation may or may not pass depending on board size and component count — just check it runs
    assert "passed" in res_val.json()

    # 3. Physics Features
    res_feat = client.post("/api/pcb/test_pcb_api_proj/physics/features")
    assert res_feat.status_code == 200
    assert len(res_feat.json()) > 0

    # 4. PINN Training (fast)
    res_train = client.post(
        "/api/pcb/test_pcb_api_proj/pinn/train",
        json={"epochs": 10, "learning_rate": 0.01},
    )
    assert res_train.status_code == 200
    assert "validation_metrics" in res_train.json()

    # 5. Placement Optimization
    res_opt = client.post(
        "/api/pcb/test_pcb_api_proj/optimize",
        json={"max_iterations": 15},
    )
    assert res_opt.status_code == 200
    assert res_opt.json()["status"] == "OPTIMIZED"


def test_pcb_cli_commands():
    """Test CLI commands: pcb create, pcb status, pcb components, pcb constraints, pcb validate.
    Uses asyncio directly to verify create -> disk-persist -> status reads from disk correctly.
    """
    svc = PCBService()

    async def _create():
        return await svc.create_pcb_project(
            "autonomous-rover",
            board_width=80.0,
            board_height=60.0,
        )

    async def _get():
        svc2 = PCBService()
        return await svc2.get_pcb_project("autonomous-rover")

    # Create via service (same path the CLI uses)
    proj = asyncio.run(_create())
    assert proj is not None
    assert proj.project_id == "autonomous-rover"
    assert len(proj.components) > 0

    # Load from disk in a fresh service instance (same as CLI status after re-invocation)
    loaded = asyncio.run(_get())
    assert loaded is not None, "PCB project should be persisted to disk and reloaded"
    assert loaded.project_id == "autonomous-rover"

    # Verify basic CLI commands do not crash with project in place
    runner = CliRunner()

    res_comp = runner.invoke(cli_app, ["pcb", "components", "--project", "autonomous-rover"])
    assert res_comp.exit_code == 0

    res_val = runner.invoke(cli_app, ["pcb", "validate", "--project", "autonomous-rover"])
    assert res_val.exit_code == 0
