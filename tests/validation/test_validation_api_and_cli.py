"""Tests for Validation FastAPI endpoints and Typer CLI commands."""

from fastapi.testclient import TestClient
import pytest
from typer.testing import CliRunner
from backend.main import app as fastapi_app
from backend.workline.knowledge.graph.models import EntityType
from backend.workline.knowledge.graph.service import knowledge_graph_service
from backend.workline.validation.models import (
    ConstraintOperator,
    EngineeringConstraint,
    ValidationStatus,
)
from backend.workline.validation.service import validation_service
from cli.wline.main import app as cli_app

client = TestClient(fastapi_app)
runner = CliRunner()


@pytest.fixture(autouse=True)
def setup_api_and_cli_fixtures():
    c1 = EngineeringConstraint(
        constraint_id="c_vout",
        property="output_voltage",
        operator=ConstraintOperator.EQ,
        required_value="3.3V",
        required_unit="V",
        normalized_value=3.3,
    )
    validation_service.create_requirement(
        requirement_id="REQ-API-101",
        project_id="rover_v2",
        description="3.3V Output Regulator",
        constraints=[c1],
    )
    knowledge_graph_service.create_entity("ENT-TPS62130", EntityType.COMPONENT, "TPS62130", "rover_v2")
    knowledge_graph_service.add_specification("S_API", "ENT-TPS62130", "output_voltage", "3.3 V", "ds.pdf", 1)


def test_fastapi_validation_endpoints():
    # 1. Create requirement
    payload = {
        "requirement_id": "REQ-POST-1",
        "project_id": "rover_v2",
        "description": "5V system rail",
        "category": "POWER",
    }
    res_post = client.post("/api/requirements", json=payload)
    assert res_post.status_code == 200
    assert res_post.json()["requirement_id"] == "REQ-POST-1"

    # 2. List requirements
    res_list = client.get("/api/requirements?project_id=rover_v2")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # 3. Validate candidate
    res_val = client.post("/api/requirements/REQ-API-101/validate", json={"candidate_component_id": "ENT-TPS62130"})
    assert res_val.status_code == 200
    assert res_val.json()["overall_status"] == "PASS"


def test_cli_requirement_and_component_commands():
    # 1. requirement list
    res_list = runner.invoke(cli_app, ["requirement", "list", "-p", "rover_v2"])
    assert res_list.exit_code == 0
    assert "REQ-API-101" in res_list.stdout

    # 2. requirement inspect
    res_insp = runner.invoke(cli_app, ["requirement", "inspect", "REQ-API-101"])
    assert res_insp.exit_code == 0
    assert "output_voltage" in res_insp.stdout

    # 3. requirement validate
    res_val = runner.invoke(cli_app, ["requirement", "validate", "REQ-API-101", "-c", "ENT-TPS62130"])
    assert res_val.exit_code == 0
    assert "PASS" in res_val.stdout

    # 4. component validate
    res_comp = runner.invoke(cli_app, ["component", "validate", "ENT-TPS62130", "-r", "REQ-API-101"])
    assert res_comp.exit_code == 0
    assert "PASS" in res_comp.stdout
