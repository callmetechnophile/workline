"""Unit tests for OrderPlan compilation, Order generation, and Price/Stock Revalidation."""

import asyncio
import pytest
from backend.workline.orders.models import (
    ApprovalStatus,
    CostBreakdownItem,
    Order,
    OrderItem,
    OrderPolicy,
    OrderStatus,
    OrderTotal,
)
from backend.workline.orders.policies.limits import SpendingLimitValidator
from backend.workline.orders.service import OrderService
from backend.workline.orders.validator import OrderValidator
from backend.workline.procurement.engine import ProcurementEngine
from backend.workline.procurement.models import (
    BOM,
    BOMItem,
    BOMStatus,
    ComponentRequirement,
)


def test_order_plan_creation_from_bom():
    """Test generating an itemized OrderPlan from an approved BOM."""
    async def _run():
        procurement = ProcurementEngine()
        order_svc = OrderService(procurement=procurement)

        reqs = [
            ComponentRequirement(requirement_id="req_mcu", category="Microcontroller", quantity=1),
            ComponentRequirement(requirement_id="req_reg", category="Power Management", quantity=2),
        ]
        bom, _ = await procurement.generate_project_bom("test_rover_orders", reqs)

        plan = await order_svc.create_order_plan("test_rover_orders", bom.bom_id)
        assert plan.bom_id == bom.bom_id
        assert len(plan.items) >= 2
        assert plan.financials.subtotal.value > 0.0
        assert plan.financials.shipping.value >= 0.0
        assert plan.financials.total.value > plan.financials.subtotal.value

    asyncio.run(_run())


def test_orders_creation_from_plan():
    """Test splitting an OrderPlan into per-vendor Order records in READY_FOR_APPROVAL status."""
    async def _run():
        procurement = ProcurementEngine()
        order_svc = OrderService(procurement=procurement)

        reqs = [ComponentRequirement(requirement_id="req_1", category="Sensors", quantity=1)]
        bom, _ = await procurement.generate_project_bom("test_split_proj", reqs)
        plan = await order_svc.create_order_plan("test_split_proj", bom.bom_id)

        orders = await order_svc.create_orders_from_plan(plan, user_role="ENGINEER")
        assert len(orders) >= 1
        order = orders[0]
        assert order.status == OrderStatus.READY_FOR_APPROVAL
        assert order.approval_status == ApprovalStatus.PENDING
        assert order.total > 0.0
        assert len(order.items) >= 1

    asyncio.run(_run())


def test_price_and_stock_revalidation():
    """Test live price and stock verification before order approval."""
    async def _run():
        procurement = ProcurementEngine()
        validator = OrderValidator(procurement=procurement)

        order = Order(
            order_id="WL-ORD-TEST-001",
            project_id="test_proj",
            vendor="Texas Instruments",
            currency="INR",
            subtotal=200.0,
            shipping_cost=90.0,
            total=290.0,
            items=[
                OrderItem(
                    order_item_id="item_tps",
                    order_id="WL-ORD-TEST-001",
                    component_id="component:texas_instruments_tps62130rgtr",
                    manufacturer="Texas Instruments",
                    mpn="TPS62130RGTR",
                    quantity=1,
                    unit_price=200.0,
                    extended_price=200.0,
                    vendor_name="DigiKey",
                )
            ],
        )

        report = await validator.revalidate_order_data(order)
        assert report.order_id == "WL-ORD-TEST-001"
        assert len(report.items) == 1
        assert report.is_valid is True

    asyncio.run(_run())


def test_spending_limits_enforcement():
    """Test blocking orders that exceed maximum per-order budget limits."""
    spending_validator = SpendingLimitValidator(policy=OrderPolicy(maximum_order_value=5000.0))

    # Order within budget
    order_ok = Order(
        order_id="WL-ORD-OK",
        project_id="p1",
        vendor="Robu",
        currency="INR",
        subtotal=1000.0,
        shipping_cost=90.0,
        total=1090.0,
    )
    ok, err = spending_validator.validate_spending_limits(order_ok)
    assert ok is True
    assert err is None

    # Order exceeding budget limit
    order_over = Order(
        order_id="WL-ORD-OVER",
        project_id="p1",
        vendor="Robu",
        currency="INR",
        subtotal=6000.0,
        shipping_cost=90.0,
        total=6090.0,
    )
    ok_over, err_over = spending_validator.validate_spending_limits(order_over)
    assert ok_over is False
    assert "exceeds maximum order limit" in err_over
