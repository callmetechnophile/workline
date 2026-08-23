"""
Unit & Integration tests for the 402 Handshake, GoPlausible/Algorand Settlement, Idempotency, and Replay Protection.
"""

from datetime import datetime, timedelta, timezone
import json
import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.workline.x402.storage import x402_storage
from backend.workline.x402.models import PaymentRecord, PaymentStatus


@pytest.fixture(autouse=True)
def clean_storage():
    """Reset x402 storage before and after each test."""
    x402_storage.clear()
    yield
    x402_storage.clear()


@pytest.mark.asyncio
async def test_unpaid_request_returns_402_challenge():
    """Test that calling an x402 endpoint without payment returns HTTP 402 with structured challenge."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/x402/bom/optimize",
            json={"project_id": "test_board_1", "bom_items": [{"ref": "U1", "part_number": "TPS62130"}]},
        )

        assert res.status_code == 402
        assert "X-Payment-Required" in res.headers

        data = res.json()
        assert data["status_code"] == 402
        assert data["service_id"] == "bom.optimize"
        assert "challenge" in data

        challenge = data["challenge"]
        assert challenge["scheme"] == "x402"
        assert challenge["amount"] == 0.50
        assert challenge["asset"] == "USDC"
        assert challenge["asset_id"] in (31566704, 10458941)
        assert challenge["pay_to"] is not None
        assert challenge["payment_request_id"].startswith("pay_req_")
        assert challenge["nonce"] is not None


@pytest.mark.asyncio
async def test_invalid_payment_proof_rejected():
    """Test that submitting an invalid or empty proof is rejected with 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Trigger 402 challenge
        res_402 = await client.post("/api/x402/component/analyze", json={"part_number": "LM2596"})
        req_id = res_402.json()["challenge"]["payment_request_id"]

        # 2. Submit bad proof (missing tx_hash)
        res_bad = await client.post(
            "/api/x402/component/analyze",
            json={"part_number": "LM2596"},
            headers={"X-PAYMENT": json.dumps({"payment_request_id": req_id, "tx_hash": ""})},
        )

        assert res_bad.status_code == 400
        assert "Invalid proof" in res_bad.json()["detail"]


@pytest.mark.asyncio
async def test_valid_algorand_settlement_executes_service():
    """Test that submitting a valid settlement proof verifies payment and returns service result."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Trigger 402 challenge
        res_402 = await client.post(
            "/api/x402/simulation/thermal",
            json={"project_id": "rover_v2", "ambient_c": 25.0},
        )
        assert res_402.status_code == 402
        req_id = res_402.json()["challenge"]["payment_request_id"]

        # 2. Submit valid Algorand transaction settlement proof
        proof = {
            "payment_request_id": req_id,
            "tx_hash": "ALGO_TX_PROOF_TEST_SETTLED_88921",
            "payer_address": "ALGO_CLIENT_WALLET_9921",
        }
        res_paid = await client.post(
            "/api/x402/simulation/thermal",
            json={"project_id": "rover_v2", "ambient_c": 25.0},
            headers={"X-PAYMENT": json.dumps(proof)},
        )

        assert res_paid.status_code == 200
        data = res_paid.json()
        assert data["status"] == "SUCCESS"
        assert data["service_id"] == "simulation.thermal"
        assert data["payment"]["status"] == "EXECUTED"
        assert data["payment"]["tx_hash"] == "ALGO_TX_PROOF_TEST_SETTLED_88921"
        assert "result" in data
        assert data["result"]["solver"] == "PINN-Surrogate-v1"


@pytest.mark.asyncio
async def test_idempotency_returns_cached_result():
    """Test that a repeated request with the same idempotency key returns the settled result without re-charging."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        idempotency_key = "idemp_key_unique_test_1001"

        # 1. Initial 402 with idempotency key
        res_402 = await client.post(
            "/api/x402/research/engineering",
            json={"query": "Buck Converter Design"},
            headers={"X-Idempotency-Key": idempotency_key},
        )
        assert res_402.status_code == 402
        req_id = res_402.json()["challenge"]["payment_request_id"]

        # 2. Settle payment
        proof = {
            "payment_request_id": req_id,
            "tx_hash": "ALGO_TX_IDEMPOTENT_TEST_1001",
        }
        res_first = await client.post(
            "/api/x402/research/engineering",
            json={"query": "Buck Converter Design"},
            headers={
                "X-PAYMENT": json.dumps(proof),
                "X-Idempotency-Key": idempotency_key,
            },
        )
        assert res_first.status_code == 200
        first_data = res_first.json()

        # 3. Retry same request with same idempotency key
        res_retry = await client.post(
            "/api/x402/research/engineering",
            json={"query": "Buck Converter Design"},
            headers={"X-Idempotency-Key": idempotency_key},
        )
        assert res_retry.status_code == 200
        retry_data = res_retry.json()
        assert retry_data.get("idempotent") is True
        assert retry_data["result"] == first_data["result"]


@pytest.mark.asyncio
async def test_replay_attack_rejected():
    """Test that reusing the same transaction hash for a different challenge is rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        shared_tx_hash = "ALGO_REUSED_TX_HASH_ATTACK_999"

        # 1. First challenge & settlement
        res1_402 = await client.post("/api/x402/component/analyze", json={"part_number": "U1"})
        req1_id = res1_402.json()["challenge"]["payment_request_id"]
        res1_paid = await client.post(
            "/api/x402/component/analyze",
            json={"part_number": "U1"},
            headers={"X-PAYMENT": json.dumps({"payment_request_id": req1_id, "tx_hash": shared_tx_hash})},
        )
        assert res1_paid.status_code == 200

        # 2. Second challenge -> Attacker tries to reuse the same tx_hash
        res2_402 = await client.post("/api/x402/bom/optimize", json={"bom_items": []})
        req2_id = res2_402.json()["challenge"]["payment_request_id"]
        res2_attack = await client.post(
            "/api/x402/bom/optimize",
            json={"bom_items": []},
            headers={"X-PAYMENT": json.dumps({"payment_request_id": req2_id, "tx_hash": shared_tx_hash})},
        )

        assert res2_attack.status_code == 400
        assert "Replay rejected" in res2_attack.json()["detail"]


@pytest.mark.asyncio
async def test_expired_challenge_rejected():
    """Test that attempting to settle an expired 402 challenge fails."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create expired challenge directly in storage
        expired_req_id = "pay_req_expired_test_01"
        past_time = (datetime.now(timezone.utc) - timedelta(minutes=45)).isoformat()
        record = PaymentRecord(
            id="pay_rec_exp",
            payment_request_id=expired_req_id,
            service_id="bom.optimize",
            amount=0.50,
            asset="USDC",
            asset_id=31566704,
            network="algorand-mainnet",
            pay_to="WORKLINE24E...",
            facilitator="https://facilitator.goplausible.com",
            status=PaymentStatus.PAYMENT_REQUIRED,
            expires_at=past_time,
        )
        x402_storage.save_record(record)

        # Attempt to redeem expired challenge
        res = await client.post(
            "/api/x402/bom/optimize",
            json={"bom_items": []},
            headers={"X-PAYMENT": json.dumps({"payment_request_id": expired_req_id, "tx_hash": "ALGO_TX_EXPIRED_99"})},
        )

        assert res.status_code == 400
        assert "expired" in res.json()["detail"].lower()
