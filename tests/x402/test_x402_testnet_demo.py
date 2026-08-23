"""
Unit and integration tests for the dedicated x402 Hackathon Testnet Demo Endpoint.
Tests:
- GET /api/x402/demo (Unpaid -> HTTP 402 Challenge)
- POST /api/x402/demo (Unpaid -> HTTP 402 Challenge)
- Automated retry with X-PAYMENT proof -> HTTP 200 Settled + Transaction ID
- Replay prevention on demo endpoint
- Server-side price enforcement (0.01 USDC on Algorand Testnet)
"""

import json
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.workline.x402.config import x402_config
from backend.workline.x402.storage import x402_storage

client = TestClient(app)


def test_get_demo_unpaid_returns_402():
    """Verify that calling GET /api/x402/demo without payment returns a real HTTP 402 challenge."""
    response = client.get("/api/x402/demo")
    assert response.status_code == 402

    # Check x402 header
    assert "X-Payment-Required" in response.headers
    payment_header = response.headers["X-Payment-Required"]
    assert "x402" in payment_header
    assert "amount=0.01" in payment_header
    assert "asset=USDC" in payment_header
    assert "payment_request_id=pay_req_" in payment_header

    # Check JSON body
    data = response.json()
    assert data["status_code"] == 402
    assert "challenge" in data
    challenge = data["challenge"]
    assert challenge["scheme"] == "x402"
    assert challenge["amount"] == 0.01
    assert challenge["asset"] == "USDC"
    assert challenge["asset_id"] in (10458941, 31566704)
    assert challenge["pay_to"] is not None
    assert challenge["payment_request_id"].startswith("pay_req_")
    assert challenge["nonce"] is not None


def test_post_demo_unpaid_returns_402():
    """Verify that calling POST /api/x402/demo without payment also produces HTTP 402."""
    response = client.post("/api/x402/demo", json={})
    assert response.status_code == 402
    data = response.json()
    assert data["status_code"] == 402
    assert "challenge" in data


def test_demo_payment_retry_and_settlement():
    """
    Test the complete 402 -> sign -> retry -> settle flow on the demo endpoint.
    """
    # 1. Trigger 402 challenge
    init_res = client.get("/api/x402/demo")
    assert init_res.status_code == 402
    challenge = init_res.json()["challenge"]
    req_id = challenge["payment_request_id"]

    # 2. Simulate signed transaction proof from Pera Wallet
    tx_hash = f"TXALGOTESTNET{req_id.replace('pay_req_', '')}ABCDEF123456789"
    proof_payload = {
        "payment_request_id": req_id,
        "tx_hash": tx_hash,
        "signature": "simulated_pera_ed25519_signature_bytes",
        "payer_address": "PERAWALLETTESTNETADDRESS58CHARSXXXXXXXXXXXXXXXXXXXXX",
    }

    # 3. Retry GET /api/x402/demo with X-PAYMENT header
    retry_res = client.get(
        "/api/x402/demo",
        headers={"X-PAYMENT": json.dumps(proof_payload)},
    )
    assert retry_res.status_code == 200
    settled = retry_res.json()

    assert settled["status"] == "SUCCESS"
    assert settled["service_id"] == "workline.test.verified"
    assert settled["payment"]["status"] == "EXECUTED"
    assert settled["payment"]["amount_usdc"] == 0.01
    assert settled["payment"]["tx_hash"] == tx_hash
    assert settled["payment"]["payment_id"] == req_id
    assert "result" in settled
    assert settled["result"]["status"] == "VERIFIED"
    assert "engineering_attestation" in settled["result"]


def test_demo_replay_attack_prevention():
    """Verify that the same tx_hash cannot be redeemed for a second challenge."""
    # 1. Challenge A
    res_a = client.get("/api/x402/demo")
    assert res_a.status_code == 402
    req_id_a = res_a.json()["challenge"]["payment_request_id"]

    tx_hash = "TXALGO_UNIQUE_TESTNET_HASH_99999"
    proof_a = {
        "payment_request_id": req_id_a,
        "tx_hash": tx_hash,
        "signature": "sig_a",
        "payer_address": "PERAWALLETTESTNETADDRESS58CHARSXXXXXXXXXXXXXXXXXXXXX",
    }

    settle_a = client.get("/api/x402/demo", headers={"X-PAYMENT": json.dumps(proof_a)})
    assert settle_a.status_code == 200

    # 2. Challenge B (new challenge)
    res_b = client.get("/api/x402/demo")
    assert res_b.status_code == 402
    req_id_b = res_b.json()["challenge"]["payment_request_id"]

    # Attempt to replay tx_hash for Challenge B
    proof_b = {
        "payment_request_id": req_id_b,
        "tx_hash": tx_hash,
        "signature": "sig_b",
        "payer_address": "PERAWALLETTESTNETADDRESS58CHARSXXXXXXXXXXXXXXXXXXXXX",
    }

    replay_res = client.get("/api/x402/demo", headers={"X-PAYMENT": json.dumps(proof_b)})
    assert replay_res.status_code == 400
    assert "Replay rejected" in replay_res.json()["detail"]
