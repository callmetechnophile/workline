"""Unit tests for Order Execution (Automated vs Manual Mode), Idempotency, and Receipts."""

import asyncio
import pytest
from backend.workline.orders.executor import OrderExecutor
from backend.workline.orders.models import (
    ApprovalStatus,
    Order,
    OrderExecutionMode,
    OrderItem,
    OrderStatus,
    PaymentSession,
    PaymentStatus,
    ReceiptVerificationStatus,
)
from backend.workline.orders.receipts import ReceiptService


def test_automated_order_execution():
    """Test automated vendor API order execution (DigiKey) resulting in CONFIRMED and verified Receipt."""
    async def _run():
        executor = OrderExecutor()
        order = Order(
            order_id="WL-ORD-EXEC-AUTO",
            project_id="rover_proj",
            vendor="DigiKey",
            currency="INR",
            subtotal=450.0,
            shipping_cost=0.0,
            total=450.0,
            execution_mode=OrderExecutionMode.AUTOMATED,
            status=OrderStatus.PAYMENT_AUTHORIZED,
            items=[
                OrderItem(
                    order_item_id="item_1",
                    order_id="WL-ORD-EXEC-AUTO",
                    component_id="component:texas_instruments_tps62130rgtr",
                    manufacturer="Texas Instruments",
                    mpn="TPS62130RGTR",
                    quantity=2,
                    unit_price=225.0,
                    extended_price=450.0,
                    vendor_name="DigiKey",
                )
            ],
        )

        session = PaymentSession(
            payment_session_id="sess_1",
            order_id=order.order_id,
            payment_request_id="pay_1",
            amount=5.20,
            currency="USD",
            network="base-sepolia",
            asset="USDC",
            recipient="0xTreasury",
            status=PaymentStatus.AUTHORIZED,
            expires_at="2026-12-31T00:00:00Z",
        )

        ok, updated_order, receipt, err = await executor.execute_order(order, session)
        assert ok is True
        assert err is None
        assert updated_order.status == OrderStatus.CONFIRMED
        assert updated_order.external_order_id is not None
        assert receipt is not None
        assert receipt.verification_status == ReceiptVerificationStatus.VERIFIED

    asyncio.run(_run())


def test_manual_checkout_order_execution():
    """Test manual checkout vendor order execution (Robu) resulting in MANUAL_CHECKOUT_REQUIRED."""
    async def _run():
        executor = OrderExecutor()
        order = Order(
            order_id="WL-ORD-EXEC-MANUAL",
            project_id="rover_proj",
            vendor="Robu",
            currency="INR",
            subtotal=349.0,
            shipping_cost=90.0,
            total=439.0,
            execution_mode=OrderExecutionMode.MANUAL,
            status=OrderStatus.PAYMENT_AUTHORIZED,
            items=[
                OrderItem(
                    order_item_id="item_bme",
                    order_id="WL-ORD-EXEC-MANUAL",
                    component_id="component:bosch_sensortec_bme280",
                    manufacturer="Bosch Sensortec",
                    mpn="BME280",
                    quantity=1,
                    unit_price=349.0,
                    extended_price=349.0,
                    vendor_name="Robu",
                )
            ],
        )

        session = PaymentSession(
            payment_session_id="sess_2",
            order_id=order.order_id,
            payment_request_id="pay_2",
            amount=5.07,
            currency="USD",
            network="base-sepolia",
            asset="USDC",
            recipient="0xTreasury",
            status=PaymentStatus.AUTHORIZED,
            expires_at="2026-12-31T00:00:00Z",
        )

        ok, updated_order, receipt, err = await executor.execute_order(order, session)
        assert ok is True
        assert updated_order.status == OrderStatus.MANUAL_CHECKOUT_REQUIRED
        assert "MANUAL" in updated_order.external_order_id

    asyncio.run(_run())


def test_order_execution_idempotency():
    """Test idempotency prevents duplicate execution attempts on the same order attempt."""
    async def _run():
        executor = OrderExecutor()
        order = Order(
            order_id="WL-ORD-IDEMP",
            project_id="p1",
            vendor="DigiKey",
            currency="INR",
            subtotal=100.0,
            shipping_cost=0.0,
            total=100.0,
            idempotency_key="idemp_unique_key_12345",
        )
        session = PaymentSession(
            payment_session_id="sess_3",
            order_id=order.order_id,
            payment_request_id="pay_3",
            amount=1.15,
            currency="USD",
            network="base-sepolia",
            asset="USDC",
            recipient="0xTreasury",
            status=PaymentStatus.AUTHORIZED,
            expires_at="2026-12-31T00:00:00Z",
        )

        # 1st attempt
        ok1, ord1, _, _ = await executor.execute_order(order, session)
        assert ok1 is True
        assert ord1.status == OrderStatus.CONFIRMED

        # 2nd duplicate attempt (must return cached result without re-executing)
        ok2, ord2, _, _ = await executor.execute_order(order, session)
        assert ok2 is True
        assert ord2.status == OrderStatus.CONFIRMED

    asyncio.run(_run())
