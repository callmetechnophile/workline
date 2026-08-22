"""Tests for Knowledge Graph FastAPI endpoints and Typer CLI commands."""

from fastapi.testclient import TestClient
import pytest
from typer.testing import CliRunner
from backend.main import app as fastapi_app
from backend.workline.knowledge.graph.models import EntityType
from backend.workline.knowledge.graph.service import knowledge_graph_service
from cli.wline.main import app as cli_app

client = TestClient(fastapi_app)
runner = CliRunner()


@pytest.fixture(autouse=True)
def setup_test_graph():
    knowledge_graph_service.create_entity(
        entity_id="ENT-TPS62130",
        entity_type=EntityType.COMPONENT,
        canonical_name="TPS62130",
        aliases=["TPS62130RGTR"],
        project_id="rover_v2",
        manufacturer="Texas Instruments",
    )
    knowledge_graph_service.add_specification(
        specification_id="SPEC-TPS-1",
        entity_id="ENT-TPS62130",
        property_name="Output Current",
        value_str="3 A",
        source_document="TPS62130.pdf",
        page=1,
        section="Features",
        confidence=1.0,
    )


def test_fastapi_entity_and_graph_endpoints():
    # 1. Search
    res_search = client.get("/api/entities/search?q=TPS62130")
    assert res_search.status_code == 200
    assert len(res_search.json()) >= 1

    # 2. Get Entity
    res_get = client.get("/api/entities/ENT-TPS62130")
    assert res_get.status_code == 200
    assert res_get.json()["canonical_name"] == "TPS62130"

    # 3. Get Specifications
    res_specs = client.get("/api/entities/ENT-TPS62130/specifications")
    assert res_specs.status_code == 200
    assert any(s["property"] == "Output Current" for s in res_specs.json())

    # 4. Get Evidence
    res_ev = client.get("/api/entities/ENT-TPS62130/evidence")
    assert res_ev.status_code == 200
    assert len(res_ev.json()) >= 1

    # 5. Graph Related
    res_rel = client.get("/api/graph/related/ENT-TPS62130")
    assert res_rel.status_code == 200
    assert "entity" in res_rel.json()


def test_cli_entity_and_graph_commands():
    # 1. entity find
    res_find = runner.invoke(cli_app, ["entity", "find", "TPS62130"])
    assert res_find.exit_code == 0
    assert "TPS62130" in res_find.stdout

    # 2. entity inspect
    res_insp = runner.invoke(cli_app, ["entity", "inspect", "ENT-TPS62130"])
    assert res_insp.exit_code == 0
    assert "Output Current" in res_insp.stdout

    # 3. entity resolve
    res_res = runner.invoke(cli_app, ["entity", "resolve", "TPS62130RGTR", "--mfr", "Texas Instruments"])
    assert res_res.exit_code == 0
    assert "ALIAS_VARIANT" in res_res.stdout or "RESOLVED" in res_res.stdout

    # 4. graph related
    res_rel = runner.invoke(cli_app, ["graph", "related", "ENT-TPS62130"])
    assert res_rel.exit_code == 0

    # 5. graph evidence
    res_ev = runner.invoke(cli_app, ["graph", "evidence", "ENT-TPS62130"])
    assert res_ev.exit_code == 0
    assert "Output Current" in res_ev.stdout
