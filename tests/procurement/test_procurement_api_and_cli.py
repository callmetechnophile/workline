"""Integration tests for Procurement REST API endpoints and CLI commands."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


def test_procurement_api_endpoints():
    """Test /api/procurement/search, /api/procurement/validate, and /api/bom endpoints."""
    client = TestClient(app)

    # 1. Search
    res_search = client.post("/api/procurement/search", json={"query": "TPS62130", "limit": 2})
    assert res_search.status_code == 200
    search_data = res_search.json()
    assert search_data["count"] >= 1

    # 2. Validate
    cand = search_data["candidates"][0]
    res_val = client.post(
        "/api/procurement/validate",
        json={
            "candidate": cand,
            "requirement": {
                "requirement_id": "req_1",
                "category": "Voltage Regulator",
                "nominal_voltage": 3.3,
                "required_current_min_a": 2.0,
            },
        },
    )
    assert res_val.status_code == 200
    val_report = res_val.json()
    assert val_report["is_compatible"] is True

    # 3. Generate BOM
    res_bom = client.post(
        "/api/bom/generate",
        json={
            "project_id": "test_api_proj",
            "requirements": [
                {
                    "requirement_id": "req_mcu",
                    "category": "Microcontroller",
                    "quantity": 1,
                }
            ],
        },
    )
    assert res_bom.status_code == 200
    bom_data = res_bom.json()
    assert "bom_id" in bom_data
    bom_id = bom_data["bom_id"]

    # 4. Approve BOM
    res_appr = client.post(f"/api/bom/{bom_id}/approve", json={"approved_by": "Lead Engineer"})
    assert res_appr.status_code == 200
    assert res_appr.json()["status"] == "APPROVED"
