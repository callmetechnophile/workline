"""
Tests verifying the architectural separation between:
1. Workline x402 Service Revenue (Algorand USDC micro-fee for AI services)
2. Physical Component Procurement (Purchase Orders & Distributor Commercial Rails)
"""

import json
import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.workline.orders.models import Order
from backend.workline.orders.service import order_service
from backend.workline.x402.storage import x402_storage


@pytest.fixture(autouse=True)
def clean_storage():
    x402_storage.clear()
    yield
    x402_storage.clear()


@pytest.mark.asyncio
async def test_x402_procurement_quote_service_pays_workline_only():
    """
    Verify that calling POST /api/x402/procurement/quote charges the fixed $0.25 USDC Workline fee
    and does NOT charge or pay the distributor component subtotal ($42.50).
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Unpaid request triggers 402 challenge for 0.25 USDC
        res_402 = await client.post(
            "/api/x402/procurement/quote",
            json={"project_id": "test_rfq_board", "parameters": {"target_qty": 100}},
        )
        assert res_402.status_code == 402
        challenge = res_402.json()["challenge"]

        # Workline fee is $0.25 USDC
        assert challenge["amount"] == 0.25
        assert challenge["asset"] == "USDC"
        req_id = challenge["payment_request_id"]

        # 2. Settle 0.25 USDC Workline fee
        res_paid = await client.post(
            "/api/x402/procurement/quote",
            json={"project_id": "test_rfq_board", "parameters": {"target_qty": 100}},
            headers={"X-PAYMENT": json.dumps({"payment_request_id": req_id, "tx_hash": "ALGO_TX_QUOTE_FEE_778"})},
        )
        assert res_paid.status_code == 200
        data = res_paid.json()

        # Check that x402 payment was for 0.25 USDC service revenue
        assert data["payment"]["amount_usdc"] == 0.25
        assert data["payment"]["tx_hash"] == "ALGO_TX_QUOTE_FEE_778"

        # Check that result contains distributor quote output for downstream PO generation
        assert data["result"]["status"] == "READY_FOR_PURCHASE_ORDER"
        assert "vendors_queried" in data["result"]
        assert data["result"]["consolidated_quote_usd"] == 42.50


@pytest.mark.asyncio
async def test_physical_distributor_orders_use_distributor_rails():
    """
    Verify that Order objects for physical distributors (DigiKey, Mouser, Robu)
    maintain their native currency and PO state machine independently of x402.
    """
    order = Order(
        order_id="WL-ORD-DIST-TEST-01",
        project_id="rover_v2",
        vendor="DigiKey",
        currency="INR",
        subtotal=14250.0,
        shipping_cost=250.0,
        total=14500.0,
    )

    # The order has vendor details and physical totals
    assert order.vendor == "DigiKey"
    assert order.total == 14500.0
    assert order.currency == "INR"
    assert order.status.value == "DRAFT"
