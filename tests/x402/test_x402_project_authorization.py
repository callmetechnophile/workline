"""
Tests for Project Association, User Isolation, and Payment Audit Log Queries.
"""

import json
import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.workline.x402.storage import x402_storage


@pytest.fixture(autouse=True)
def clean_storage():
    x402_storage.clear()
    yield
    x402_storage.clear()


@pytest.mark.asyncio
async def test_payment_record_stores_project_and_user_association():
    """Verify that x402 challenges and settlements maintain strict project and user metadata."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Challenge with project & user ID
        payload = {
            "project_id": "proj_rover_solar_board",
            "user_id": "user_lead_engineer_42",
            "parameters": {"part_number": "TPS62130"},
        }
        res_402 = await client.post("/api/x402/component/analyze", json=payload)
        req_id = res_402.json()["challenge"]["payment_request_id"]

        # 2. Settle payment
        proof = {
            "payment_request_id": req_id,
            "tx_hash": "ALGO_TX_USER_PROJ_ASSOC_99",
            "payer_address": "ALGORAND_CLIENT_ADDR_77",
        }
        res_paid = await client.post(
            "/api/x402/component/analyze",
            json=payload,
            headers={"X-PAYMENT": json.dumps(proof)},
        )
        assert res_paid.status_code == 200

        # 3. Query payments filtered by project_id
        res_list = await client.get("/api/x402/payments?project_id=proj_rover_solar_board")
        assert res_list.status_code == 200
        data = res_list.json()
        assert data["count"] == 1
        record = data["payments"][0]
        assert record["project_id"] == "proj_rover_solar_board"
        assert record["user_id"] == "user_lead_engineer_42"
        assert record["status"] == "EXECUTED"
        assert record["transaction_id"] == "ALGO_TX_USER_PROJ_ASSOC_99"


@pytest.mark.asyncio
async def test_payment_status_inspection_by_id():
    """Verify inspecting single payment challenge status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res_402 = await client.post("/api/x402/bom/optimize", json={"bom_items": []})
        req_id = res_402.json()["challenge"]["payment_request_id"]

        res_inspect = await client.get(f"/api/x402/payments/{req_id}")
        assert res_inspect.status_code == 200
        rec = res_inspect.json()
        assert rec["payment_request_id"] == req_id
        assert rec["status"] == "PAYMENT_REQUIRED"
        assert rec["amount"] == 0.50
