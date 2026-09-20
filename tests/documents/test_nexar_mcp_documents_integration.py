"""
Tests for Octopart / Nexar MCP integration into Knowledge Base / Documents Index.
Verifies MCP client, knowledge bridge, deduplication, BOM integration, ArmorIQ governance,
FastAPI endpoints, and AI Copilot assistance.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient

from backend.main import app as fastapi_app
from backend.mcp.nexar_client import NexarMCPClient, nexar_mcp_client
from backend.workline.documents.models import SourceType
from backend.workline.documents.nexar_bridge import NexarKnowledgeBridge, nexar_knowledge_bridge
from backend.workline.documents.service import document_service
from backend.armoriq.receipts import generate_receipt
from backend.armoriq.scope_map import AGENT_SCOPES
from backend.armoriq.delegation import invoke_tool
from backend.services.connection_chatbot_service import ask_connection_assistant

client = TestClient(fastapi_app)


@pytest.fixture
def clean_test_env():
    """Ensure clean document index for testing."""
    original_docs = dict(document_service._documents)
    yield
    document_service._documents = original_docs


def test_nexar_mcp_client_search_and_lookup():
    """Test Nexar MCP client tool endpoints with mock/offline fallback data."""
    test_client = NexarMCPClient()

    # 1. Search components
    search_res = asyncio.run(test_client.search_components("TPS62130", limit=5))
    assert isinstance(search_res, list)
    assert len(search_res) > 0
    item = search_res[0]
    mpn_val = item.get("manufacturer_part_number") or item.get("mpn", "")
    assert "TPS62130" in mpn_val
    assert "Texas Instruments" in item.get("manufacturer", "")
    assert item["electrical"]["nominal_voltage"] == 3.3
    assert item["datasheet"]["url"] is not None

    # 2. Lookup exact MPN
    lookup_res = asyncio.run(test_client.lookup_mpn("ESP32-S3-WROOM-1-N8R8"))
    assert lookup_res is not None
    lookup_mpn = lookup_res.get("manufacturer_part_number") or lookup_res.get("mpn", "")
    assert "ESP32-S3" in lookup_mpn
    assert "Module" in lookup_res["physical"]["package"]

    # 3. Get datasheet
    ds = asyncio.run(test_client.get_datasheet("TPS62130RGTR"))
    assert ds is not None
    assert "ti.com" in ds.get("url", "") or "datasheet" in ds.get("url", "")

    # 4. Get pricing & availability
    pricing = asyncio.run(test_client.get_pricing_availability("TPS62130RGTR"))
    assert pricing is not None
    assert "stock" in pricing
    assert "unit_price" in pricing
    assert pricing["stock"] > 0

    # 5. Cache verification
    cached = asyncio.run(test_client.lookup_mpn("ESP32-S3-WROOM-1-N8R8"))
    cached_mpn = cached.get("manufacturer_part_number") or cached.get("mpn", "")
    assert cached_mpn == lookup_mpn


def test_armoriq_governance_nexar_tools():
    """Verify Nexar tools are registered in AGENT_SCOPES and executable via invoke_tool."""
    # Check registration
    assert "nexar_mcp_search" in AGENT_SCOPES["Retrieval Agent"]
    assert "nexar_mcp_lookup_mpn" in AGENT_SCOPES["Retrieval Agent"]
    assert "nexar_mcp_get_datasheet" in AGENT_SCOPES["Retrieval Agent"]

    assert "nexar_mcp_search" in AGENT_SCOPES["ProcurementAgent"]
    assert "nexar_mcp_search" in AGENT_SCOPES["EngineeringCopilotAgent"]

    # Generate cryptographic receipt
    receipt = generate_receipt(
        agent="Retrieval Agent",
        scope=["nexar_mcp_search"],
        parent_receipt_id=None,
        input_data={"query": "TPS62130", "limit": 2},
    )

    # Test invoke_tool routing with audit trail
    tool_result = invoke_tool(
        agent_name="Retrieval Agent",
        tool_name="nexar_mcp_search",
        args={"query": "TPS62130", "limit": 2},
        receipt_dict=receipt.model_dump(),
    )
    assert tool_result["success"] is True
    assert len(tool_result["data"]) > 0


def test_nexar_knowledge_bridge_deduplication(clean_test_env):
    """Test converting Nexar parts into Documents and verifying deduplication."""
    bridge = NexarKnowledgeBridge()
    mpn = "BME280"
    project_id = "test_env_project"

    # Save once
    res1 = asyncio.run(
        bridge.save_to_knowledge_base(
            project_id=project_id,
            comp_dict={
                "mpn": mpn,
                "manufacturer": "Bosch Sensortec",
                "description": "Digital humidity, pressure and temperature sensor",
                "category": "Sensors",
                "datasheet": {"url": "https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf"},
                "electrical": {"nominal_voltage": 3.3},
                "pricing": {"unit_price": 4.12, "currency": "USD"},
                "availability": {"stock": 18200},
            },
        )
    )
    assert res1["status"] == "INDEXED"
    doc_id = res1["document_id"]
    assert doc_id in document_service._documents
    doc_record = document_service._documents[doc_id]
    assert doc_record.source_type == SourceType.OCTOPART_NEXAR
    assert doc_record.metadata.get("mpn") == mpn

    # Save second time (same MPN) -> Must detect duplicate (status == "EXISTING")
    res2 = asyncio.run(
        bridge.save_to_knowledge_base(
            project_id=project_id,
            comp_dict={
                "mpn": mpn,
                "manufacturer": "Bosch Sensortec",
                "description": "Duplicate attempt",
            },
        )
    )
    assert res2["status"] == "EXISTING"
    assert res2["document_id"] == doc_id


def test_nexar_add_to_bom():
    """Test adding a Nexar component directly into the project BOM."""
    bridge = NexarKnowledgeBridge()
    project_id = "test_bom_project"

    comp = {
        "mpn": "ESP32-S3-WROOM-1-N8R8",
        "manufacturer": "Espressif Systems",
        "description": "WiFi + Bluetooth 5.0 Dual-Core MCU Module",
        "pricing": {"unit_price": 3.45, "currency": "USD"},
        "availability": {"stock": 42000},
        "datasheet": {"url": "https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_datasheet_en.pdf"},
        "vendor": {"name": "Mouser Electronics"},
    }

    res = asyncio.run(bridge.add_to_bom(project_id=project_id, comp_dict=comp, quantity=2))
    assert res["status"] == "ADDED_TO_BOM"
    bom_item = res["item"]
    assert bom_item["part_number"] == "ESP32-S3-WROOM-1-N8R8"
    assert bom_item["manufacturer"] == "Espressif Systems"
    assert bom_item["unit_price"] == 3.45
    assert bom_item["quantity"] == 2


def test_fastapi_nexar_documents_endpoints(clean_test_env):
    """Test REST API endpoints for Nexar search, save to knowledge, and add to BOM."""
    # 1. Search endpoint
    search_payload = {"query": "TPS62130", "limit": 3}
    res_search = client.post("/api/documents/nexar/search", json=search_payload)
    assert res_search.status_code == 200
    search_json = res_search.json()
    assert search_json["query"] == "TPS62130"
    assert len(search_json["results"]) > 0

    first_part = search_json["results"][0]

    # 2. Save to knowledge base
    save_payload = {
        "project_id": "api_test_project",
        "component_data": first_part,
    }
    res_save = client.post("/api/documents/nexar/save-to-knowledge", json=save_payload)
    assert res_save.status_code == 200
    save_json = res_save.json()
    assert save_json["status"] == "INDEXED"
    assert "document_id" in save_json

    # 3. Save duplicate
    res_save_dup = client.post("/api/documents/nexar/save-to-knowledge", json=save_payload)
    assert res_save_dup.status_code == 200
    assert res_save_dup.json()["status"] == "EXISTING"

    # 4. Add to BOM endpoint
    bom_payload = {
        "project_id": "api_test_project",
        "component_data": first_part,
        "quantity": 5,
    }
    res_bom = client.post("/api/documents/nexar/add-to-bom", json=bom_payload)
    assert res_bom.status_code == 200
    bom_json = res_bom.json()
    assert bom_json["status"] == "ADDED_TO_BOM"
    assert bom_json["item"]["part_number"] == (first_part.get("manufacturer_part_number") or first_part.get("mpn"))


def test_ai_copilot_nexar_assistant_query():
    """Verify AI Copilot queries Nexar MCP and provides explicit confirmation advice."""
    answer = ask_connection_assistant(
        message="Find a 3.3V buck regulator for my project power supply",
        context={"project_id": "copilot_test_proj"},
    )
    assert isinstance(answer, str)
    assert "TPS62130" in answer or "3.3V" in answer or "Regulator" in answer
    assert "Add to BOM" in answer or "Save to Knowledge Base" in answer
