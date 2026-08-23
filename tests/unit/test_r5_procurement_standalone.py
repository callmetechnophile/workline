"""
Unit and Integration Tests for Workline R5 Procurement & x402 Payment Standalone Service.
Verifies health check, Bearer service token authentication, component search, order state machine, and x402 payment challenge creation.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from backend.r5.main import app
from backend.workline.procurement.models import ComponentCandidate, VendorListing
from backend.workline.orders.models import (
    CostBreakdownItem,
    Order,
    OrderItem,
    OrderPlan,
    OrderStatus,
    OrderTotal,
    PaymentRequest,
    PaymentStatus,
)


@pytest.fixture
def client():
    """Provides TestClient for R5 FastAPI application."""
    return TestClient(app)


def test_r5_health_endpoint(client):
    """Verifies that R5 /health returns HTTP 200 without executing live orders or transactions."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "workline-r5"
    assert data["version"] == "1.0.0-rc1"


def test_r5_search_unauthorized_without_token(client):
    """Verifies that POST /internal/procurement/search returns 401 without token."""
    with patch("backend.r5.main.R5_SERVICE_TOKEN", "r5-secret-token-xyz"):
        response = client.post(
            "/internal/procurement/search",
            json={"query": "STM32F405RGT6", "limit": 5}
        )
        assert response.status_code == 401


def test_r5_search_unauthorized_with_invalid_token(client):
    """Verifies that POST /internal/procurement/search returns 401 with invalid Bearer token."""
    with patch("backend.r5.main.R5_SERVICE_TOKEN", "r5-secret-token-xyz"):
        response = client.post(
            "/internal/procurement/search",
            json={"query": "STM32F405RGT6", "limit": 5},
            headers={"Authorization": "Bearer bad-token-999"},
        )
        assert response.status_code == 401


def test_r5_search_authorized(client):
    """Verifies component search with valid Bearer token."""
    mock_candidates = [
        ComponentCandidate(
            component_id="comp_mock_stm32",
            manufacturer="STMicroelectronics",
            manufacturer_part_number="STM32F405RGT6",
            product_name="ARM Cortex-M4 Microcontroller",
            listings=[
                VendorListing(
                    listing_id="list_dk_01",
                    vendor_name="DigiKey",
                    unit_price=12.50,
                    stock_quantity=450,
                    in_stock=True
                )
            ]
        )
    ]

    with patch("backend.r5.main.R5_SERVICE_TOKEN", "r5-secret-token-xyz"), \
         patch("backend.workline.procurement.engine.procurement_engine.search_engine.search_vendors", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_candidates

        response = client.post(
            "/internal/procurement/search",
            json={"query": "STM32F405RGT6", "limit": 5},
            headers={"Authorization": "Bearer r5-secret-token-xyz"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "STM32F405RGT6"
        assert data["count"] == 1
        assert data["candidates"][0]["manufacturer_part_number"] == "STM32F405RGT6"


def test_r5_order_plan_creation(client):
    """Verifies itemized OrderPlan generation."""
    sample_financials = OrderTotal(
        subtotal=CostBreakdownItem(value=12.50),
        shipping=CostBreakdownItem(value=15.00),
        tax=CostBreakdownItem(value=0.0),
        fees=CostBreakdownItem(value=0.0),
        total=CostBreakdownItem(value=27.50),
    )

    sample_plan = OrderPlan(
        plan_id="plan_test_123",
        project_id="proj_xyz",
        bom_id="bom_abc",
        selected_vendors=["DigiKey"],
        selected_listings=["list_dk_01"],
        items=[
            OrderItem(
                order_item_id="item_1",
                order_id="ord_test_01",
                component_id="comp_mock_stm32",
                manufacturer="STMicroelectronics",
                mpn="STM32F405RGT6",
                quantity=1,
                unit_price=12.50,
                extended_price=12.50,
                vendor_name="DigiKey",
            )
        ],
        financials=sample_financials,
    )

    with patch("backend.r5.main.R5_SERVICE_TOKEN", "r5-secret-token-xyz"), \
         patch("backend.workline.orders.service.order_service.create_order_plan", new_callable=AsyncMock) as mock_create_plan:
        mock_create_plan.return_value = sample_plan

        response = client.post(
            "/internal/procurement/orders/plan",
            json={"project_id": "proj_xyz", "bom_id": "bom_abc"},
            headers={"Authorization": "Bearer r5-secret-token-xyz"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["plan_id"] == "plan_test_123"
        assert data["financials"]["total"]["value"] == 27.50
        assert len(data["items"]) == 1


def test_r5_x402_payment_request(client):
    """Verifies x402 non-custodial cryptographic payment challenge creation."""
    sample_order = Order(
        order_id="ord_test_999",
        project_id="proj_xyz",
        vendor="DigiKey",
        items=[],
        subtotal=12.50,
        shipping_cost=15.00,
        total=27.50,
        status=OrderStatus.APPROVED,
    )

    sample_payment_req = PaymentRequest(
        payment_request_id="pay_x402_001",
        order_id="ord_test_999",
        amount=27.50,
        currency="USDC",
        recipient="0xWorklineTreasuryRecipient402",
        network="base-sepolia",
        asset="USDC",
        expires_at="2026-12-31T23:59:59Z",
        idempotency_key="idemp_pay_001",
        status=PaymentStatus.REQUIRED,
    )

    with patch("backend.r5.main.R5_SERVICE_TOKEN", "r5-secret-token-xyz"), \
         patch.object(app, "dependency_overrides", {}):
        from backend.workline.orders.service import order_service
        order_service._orders["ord_test_999"] = sample_order

        with patch.object(order_service.payment_provider, "create_payment_request", new_callable=AsyncMock) as mock_pay_req:
            mock_pay_req.return_value = sample_payment_req

            response = client.post(
                "/internal/procurement/payments/request",
                json={"order_id": "ord_test_999"},
                headers={"Authorization": "Bearer r5-secret-token-xyz"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["payment_request_id"] == "pay_x402_001"
            assert data["currency"] == "USDC"
            assert data["amount"] == 27.50
            assert data["recipient"] == "0xWorklineTreasuryRecipient402"
