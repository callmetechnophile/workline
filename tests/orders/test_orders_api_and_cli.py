"""Integration tests for Orders REST API and CLI commands."""

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from backend.main import app
from cli.wline.main import app as cli_app


def test_orders_api_full_flow():
    """Test full REST API lifecycle: BOM -> Plan -> Order -> Revalidate -> Approve -> Payment -> Verify."""
    client = TestClient(app)

    # 1. Generate BOM
    res_bom = client.post(
        "/api/bom/generate",
        json={
            "project_id": "test_api_flow_proj",
            "requirements": [
                {"requirement_id": "req_mcu", "category": "Microcontroller", "quantity": 1},
                {"requirement_id": "req_reg", "category": "Power Management", "quantity": 2},
            ],
        },
    )
    assert res_bom.status_code == 200
    bom_id = res_bom.json()["bom_id"]

    # 2. Create Order Plan
    res_plan = client.post(
        "/api/orders/plan",
        json={"project_id": "test_api_flow_proj", "bom_id": bom_id},
    )
    assert res_plan.status_code == 200
    plan_data = res_plan.json()
    plan_id = plan_data["plan_id"]

    # 3. Create Orders from Plan
    res_orders = client.post(
        "/api/orders",
        json={"plan_id": plan_id, "user_role": "ENGINEER"},
    )
    assert res_orders.status_code == 200
    orders = res_orders.json()
    assert len(orders) >= 1
    order_id = orders[0]["order_id"]

    # 4. Revalidate
    res_val = client.post(f"/api/orders/{order_id}/validate")
    assert res_val.status_code == 200

    # 5. Approve
    res_appr = client.post(
        f"/api/orders/{order_id}/approve",
        json={"user_role": "OWNER", "approved_by": "Chief Engineer"},
    )
    assert res_appr.status_code == 200
    assert res_appr.json()["status"] == "APPROVED"

    # 6. Payment Challenge
    res_pay = client.post(f"/api/orders/{order_id}/payment")
    assert res_pay.status_code == 200
    pay_id = res_pay.json()["payment_request_id"]

    # 7. Payment Verification & Execution
    res_verify = client.post(
        f"/api/payments/{pay_id}/verify",
        json={
            "order_id": order_id,
            "signed_proof": {"tx_hash": "0x402_api_proof_hash"},
        },
    )
    assert res_verify.status_code == 200
    assert res_verify.json()["status"] == "SUCCESS"


def test_orders_cli_commands():
    """Test CLI commands: order create, order preview, order approve, order status."""
    runner = CliRunner()

    # 1. Order create
    res_create = runner.invoke(cli_app, ["order", "create", "autonomous-rover"])
    assert res_create.exit_code == 0
    assert "ORDER PLAN CREATED" in res_create.stdout or "WL-ORD" in res_create.stdout
