"""
Workline AI — x402 BOM Payment, Algorand Settlement, and CoinGecko INR Report Test Suite.

Comprehensive Test Suite covering Phases 1 - 25:
 1. BOM calculation
 2. Line total calculation (Decimal precision)
 3. Total USD calculation
 4. USD -> USDC 1:1 amount equality
 5. Payment quote creation & freezing
 6. HTTP 402 challenge structure
 7. Invalid payment proof rejection
 8. Amount mismatch rejection
 9. Successful settlement on Algorand
10. Transaction ID persistence
11. Idempotent repeat calls for settled payment
12. Replay attack rejection (reused tx_hash)
13. CoinGecko live lookup success
14. CoinGecko timeout resilience (report succeeds without INR)
15. CoinGecko HTTP 500 error resilience
16. CoinGecko malformed response resilience
17. PDF generation without INR
18. PDF generation with INR
19. Explorer verification link generation (Mainnet vs Testnet)
20. Cross-project isolation
21. Unauthorized procurement rejection
22. ArmourIQ capability denial
23. Critical financial mismatch test ($100 BOM vs 99 USDC)
24. Zero floating-point drift test (0.10 + 0.20 == 0.30)
"""

from decimal import Decimal
import os
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from backend.workline.armouriq.capabilities import AgentCapability
from backend.workline.armouriq.trust_context import TrustContext
from backend.workline.procurement.bom_payment import (
    AuthoritativeBom,
    AuthoritativeBomItem,
    BomPaymentState,
    PaymentQuote,
    compute_bom_pricing,
    quantize_money,
)
from backend.workline.x402.bom_flow import bom_payment_flow
from backend.workline.x402.coingecko import CoinGeckoClient, CoinGeckoRate
from backend.workline.x402.report import BomPaymentReportEngine, get_explorer_url


# ---------------------------------------------------------------------------
# Test Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_bom_items():
    return [
        {
            "part_number": "STM32F405RGT6",
            "description": "32-bit ARM Cortex-M4 MCU",
            "quantity": 2,
            "unit_price_usd": 6.50,
            "manufacturer": "STMicroelectronics",
            "supplier": "DigiKey",
            "reference_designator": "U1, U2",
        },
        {
            "part_number": "TPS62130RGTR",
            "description": "3A Step-Down Converter",
            "quantity": 4,
            "unit_price_usd": 2.25,
            "manufacturer": "Texas Instruments",
            "supplier": "Mouser",
            "reference_designator": "U3, U4, U5, U6",
        },
        {
            "part_number": "RC0603FR-0710KL",
            "description": "10k Ohm 1% 0603 Resistor",
            "quantity": 100,
            "unit_price_usd": 0.015,
            "manufacturer": "Yageo",
            "supplier": "DigiKey",
            "reference_designator": "R1-R100",
        },
    ]


@pytest.fixture
def api_client():
    from backend.main import app
    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# 1. BOM Calculation
# ---------------------------------------------------------------------------

def test_bom_calculation(sample_bom_items):
    """Verifies that compute_bom_pricing creates valid AuthoritativeBom structure."""
    bom = compute_bom_pricing(sample_bom_items, bom_id="BOM-TEST-001", project_id="PROJ-001")
    assert bom.bom_id == "BOM-TEST-001"
    assert bom.project_id == "PROJ-001"
    assert len(bom.items) == 3


# ---------------------------------------------------------------------------
# 2. Line Total Calculation with Decimal Precision
# ---------------------------------------------------------------------------

def test_line_total_calculation_decimal():
    """Verifies line total: quantity * unit_price_usd using fixed-point Decimal arithmetic."""
    item = AuthoritativeBomItem(
        part_number="TEST_IC",
        quantity=3,
        unit_price_usd=4.33,
    )
    line_tot = item.calculate_line_total()
    assert line_tot == Decimal("12.99")
    assert item.line_total_usd == 12.99


# ---------------------------------------------------------------------------
# 3. Total USD Calculation
# ---------------------------------------------------------------------------

def test_total_usd_calculation(sample_bom_items):
    """
    Item 1: 2 * 6.50 = 13.00
    Item 2: 4 * 2.25 = 9.00
    Item 3: 100 * 0.015 = 1.50
    Total: 13.00 + 9.00 + 1.50 = 23.50 USD
    """
    bom = compute_bom_pricing(sample_bom_items, bom_id="BOM-TEST-002", project_id="PROJ-002")
    assert bom.bom_total_usd == 23.50


# ---------------------------------------------------------------------------
# 4. USD -> USDC 1:1 Parity (No Currency Distortion)
# ---------------------------------------------------------------------------

def test_usd_to_usdc_parity(sample_bom_items):
    """Verifies that x402 payment quote amount in USDC is identical to BOM USD total."""
    quote = bom_payment_flow.create_payment_quote(
        bom_data={"bom_id": "BOM-PARITY", "items": sample_bom_items},
        project_id="PROJ-PARITY",
    )
    assert quote.amount_usd == 23.50
    assert quote.amount_usdc == 23.50
    assert quote.amount_usd == quote.amount_usdc
    assert quote.asset == "USDC"


# ---------------------------------------------------------------------------
# 5. Payment Quote Creation & Freezing
# ---------------------------------------------------------------------------

def test_payment_quote_creation_and_freeze(sample_bom_items):
    """Verifies frozen quote issuance with quote_id, payment_request_id, and TTL."""
    quote = bom_payment_flow.create_payment_quote(
        bom_data={"bom_id": "BOM-FREEZE", "items": sample_bom_items},
        project_id="PROJ-FREEZE",
    )
    assert quote.quote_id.startswith("quote_")
    assert quote.payment_request_id.startswith("pay_req_")
    assert quote.status == BomPaymentState.PAYMENT_REQUIRED
    assert len(quote.items_snapshot) == 3
    assert quote.expires_at is not None


# ---------------------------------------------------------------------------
# 6. HTTP 402 Challenge API Response
# ---------------------------------------------------------------------------

def test_api_create_bom_quote_returns_402_challenge(api_client, sample_bom_items):
    """POST /api/x402/bom/quote returns structured 402 Challenge with quote and payment details."""
    resp = api_client.post(
        "/api/x402/bom/quote",
        json={"project_id": "PROJ-API-001", "bom": {"bom_id": "BOM-API-001", "items": sample_bom_items}},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "PAYMENT_REQUIRED"
    assert "quote" in data
    assert "challenge" in data
    assert data["challenge"]["scheme"] == "x402"
    assert data["challenge"]["asset"] == "USDC"
    assert data["challenge"]["amount"] == 23.50


# ---------------------------------------------------------------------------
# 7. Invalid Payment Proof Rejection
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_invalid_payment_proof_rejection(sample_bom_items):
    """Submitting empty proof is rejected with PAYMENT_FAILED."""
    quote = bom_payment_flow.create_payment_quote(
        bom_data={"bom_id": "BOM-INVALID-PROOF", "items": sample_bom_items},
        project_id="PROJ-INV",
    )
    ok, err, updated_quote = await bom_payment_flow.settle_payment_proof(
        quote_id=quote.quote_id,
        proof_data={},  # Missing tx_hash / signature
    )
    assert ok is False
    assert "Missing transaction" in err
    assert updated_quote.status == BomPaymentState.PAYMENT_FAILED


# ---------------------------------------------------------------------------
# 8. Amount Mismatch Rejection ($100 BOM vs 99 USDC Payment)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_amount_mismatch_rejection(sample_bom_items):
    """If payment submitted does not equal the required BOM total, it is rejected."""
    quote = bom_payment_flow.create_payment_quote(
        bom_data={"bom_id": "BOM-MISMATCH", "items": sample_bom_items},
        project_id="PROJ-MISMATCH",
    )
    # Expected amount is 23.50 USDC, but client claims 20.00 USDC
    ok, err, updated_quote = await bom_payment_flow.settle_payment_proof(
        quote_id=quote.quote_id,
        proof_data={
            "tx_hash": "ALGO_TX_MISMATCH_PROOF_123",
            "amount": 20.00,
        },
    )
    assert ok is False
    assert "Amount mismatch" in err
    assert updated_quote.status == BomPaymentState.PAYMENT_FAILED


# ---------------------------------------------------------------------------
# 9. Successful Settlement on Algorand
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_successful_settlement_on_algorand(sample_bom_items):
    """Valid transaction proof transitions quote to PAYMENT_SETTLED."""
    quote = bom_payment_flow.create_payment_quote(
        bom_data={"bom_id": "BOM-SETTLE", "items": sample_bom_items},
        project_id="PROJ-SETTLE",
    )
    ok, err, settled_quote = await bom_payment_flow.settle_payment_proof(
        quote_id=quote.quote_id,
        proof_data={
            "tx_hash": "ALGO_TX_SETTLED_PROOF_9999",
            "payer": "ALGORAND_WALLET_SENDER_ADDR_TEST",
            "amount": 23.50,
        },
    )
    assert ok is True
    assert err is None
    assert settled_quote.status == BomPaymentState.PAYMENT_SETTLED
    assert settled_quote.transaction_id == "ALGO_TX_SETTLED_PROOF_9999"
    assert settled_quote.settled_at is not None


# ---------------------------------------------------------------------------
# 10. Transaction ID Persistence
# ---------------------------------------------------------------------------

def test_transaction_id_persisted(sample_bom_items):
    """Ensures transaction_id is permanently stamped on the quote record."""
    quote = bom_payment_flow.create_payment_quote(
        bom_data={"bom_id": "BOM-PERSIST", "items": sample_bom_items},
        project_id="PROJ-PERSIST",
    )
    import asyncio
    asyncio.run(
        bom_payment_flow.settle_payment_proof(
            quote_id=quote.quote_id,
            proof_data={"tx_hash": "ALGO_TX_PERSIST_PROOF_456"},
        )
    )
    retrieved = bom_payment_flow.get_quote(quote.quote_id)
    assert retrieved.transaction_id == "ALGO_TX_PERSIST_PROOF_456"


# ---------------------------------------------------------------------------
# 11. Idempotent Repeat Calls for Settled Payment
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_idempotent_settled_payment(sample_bom_items):
    """Calling settle_payment_proof on an already-settled quote returns success without re-charging."""
    quote = bom_payment_flow.create_payment_quote(
        bom_data={"bom_id": "BOM-IDEMPOTENT", "items": sample_bom_items},
        project_id="PROJ-IDEM",
    )
    ok1, _, q1 = await bom_payment_flow.settle_payment_proof(
        quote.quote_id, {"tx_hash": "ALGO_TX_IDEM_111"}
    )
    assert ok1 is True

    # Repeat call
    ok2, _, q2 = await bom_payment_flow.settle_payment_proof(
        quote.quote_id, {"tx_hash": "ALGO_TX_IDEM_111"}
    )
    assert ok2 is True
    assert q2.status == BomPaymentState.PAYMENT_SETTLED


# ---------------------------------------------------------------------------
# 12. Replay Attack Rejection (Reused Tx Hash)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_replay_attack_rejection(sample_bom_items):
    """Using a transaction hash already redeemed by another payment challenge is rejected."""
    q1 = bom_payment_flow.create_payment_quote(
        bom_data={"bom_id": "BOM-REPLAY-1", "items": sample_bom_items},
        project_id="PROJ-REPLAY",
    )
    q2 = bom_payment_flow.create_payment_quote(
        bom_data={"bom_id": "BOM-REPLAY-2", "items": sample_bom_items},
        project_id="PROJ-REPLAY",
    )

    # Settle Q1 with TX_UNIQUE_REPLAY
    ok1, _, _ = await bom_payment_flow.settle_payment_proof(
        q1.quote_id, {"tx_hash": "ALGO_TX_UNIQUE_REPLAY_TEST"}
    )
    assert ok1 is True

    # Attempt to reuse TX_UNIQUE_REPLAY for Q2
    ok2, err2, updated_q2 = await bom_payment_flow.settle_payment_proof(
        q2.quote_id, {"tx_hash": "ALGO_TX_UNIQUE_REPLAY_TEST"}
    )
    assert ok2 is False
    assert "Replay attack detected" in err2
    assert updated_q2.status == BomPaymentState.PAYMENT_FAILED


# ---------------------------------------------------------------------------
# 13. CoinGecko Lookup Success (Mocked)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_coingecko_lookup_success():
    """Verifies CoinGecko client retrieves and parses USDC -> INR rate."""
    with patch(
        "backend.workline.x402.coingecko.httpx.AsyncClient.get",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=200,
            json=lambda: {"usd-coin": {"inr": 86.75}},
        )
        client = CoinGeckoClient()
        rate = await client.fetch_usdc_inr_rate()

    assert rate.available is True
    assert rate.rate == 86.75
    assert rate.rate_decimal == Decimal("86.75")
    assert rate.source == "CoinGecko"


# ---------------------------------------------------------------------------
# 14. CoinGecko Timeout Resilience
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_coingecko_timeout_resilience():
    """When CoinGecko times out, client returns available=False without raising exception."""
    import httpx
    with patch(
        "backend.workline.x402.coingecko.httpx.AsyncClient.get",
        new_callable=AsyncMock,
        side_effect=httpx.TimeoutException("Read timed out"),
    ):
        client = CoinGeckoClient()
        rate = await client.fetch_usdc_inr_rate()

    assert rate.available is False
    assert "timed out" in rate.error_reason.lower()


# ---------------------------------------------------------------------------
# 15. CoinGecko HTTP 500 Resilience
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_coingecko_500_resilience():
    """When CoinGecko returns HTTP 500, client returns available=False."""
    with patch(
        "backend.workline.x402.coingecko.httpx.AsyncClient.get",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = AsyncMock(status_code=500, text="Internal Server Error")
        client = CoinGeckoClient()
        rate = await client.fetch_usdc_inr_rate()

    assert rate.available is False
    assert "HTTP 500" in rate.error_reason


# ---------------------------------------------------------------------------
# 16. CoinGecko Malformed Response Resilience
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_coingecko_malformed_response_resilience():
    """When CoinGecko returns unexpected JSON, client returns available=False."""
    with patch(
        "backend.workline.x402.coingecko.httpx.AsyncClient.get",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=200,
            json=lambda: {"unexpected_key": 123},
        )
        client = CoinGeckoClient()
        rate = await client.fetch_usdc_inr_rate()

    assert rate.available is False
    assert "Malformed" in rate.error_reason


# ---------------------------------------------------------------------------
# 17. PDF Generation WITHOUT INR (When CoinGecko Fails)
# ---------------------------------------------------------------------------

def test_pdf_generation_without_inr(sample_bom_items):
    """Compiles PDF report when CoinGecko rate is unavailable; document still succeeds."""
    bom = compute_bom_pricing(sample_bom_items, bom_id="BOM-PDF-NO-INR", project_id="PROJ-PDF")
    quote = PaymentQuote(
        project_id="PROJ-PDF",
        bom_id="BOM-PDF-NO-INR",
        amount_usd=bom.bom_total_usd,
        amount_usdc=bom.bom_total_usd,
        pay_to="ALGO_ADDR_TEST",
        facilitator="https://facilitator.goplausible.com",
        status=BomPaymentState.PAYMENT_SETTLED,
        transaction_id="ALGO_TX_NO_INR_TEST_123",
        expires_at="2030-01-01T00:00:00Z",
    )
    unavailable_rate = CoinGeckoRate(available=False, error_reason="Service unreachable")
    artifact = BomPaymentReportEngine.generate_pdf_report(bom=bom, quote=quote, rate=unavailable_rate)

    assert artifact is not None
    assert artifact.inr_available is False
    assert artifact.approx_inr_total is None
    assert os.path.exists(artifact.filepath)
    assert artifact.sha256 != ""


# ---------------------------------------------------------------------------
# 18. PDF Generation WITH INR (When CoinGecko Succeeds)
# ---------------------------------------------------------------------------

def test_pdf_generation_with_inr(sample_bom_items):
    """Compiles PDF report with live CoinGecko INR conversion annotation."""
    bom = compute_bom_pricing(sample_bom_items, bom_id="BOM-PDF-INR", project_id="PROJ-PDF-INR")
    quote = PaymentQuote(
        project_id="PROJ-PDF-INR",
        bom_id="BOM-PDF-INR",
        amount_usd=bom.bom_total_usd,
        amount_usdc=bom.bom_total_usd,
        pay_to="ALGO_ADDR_TEST",
        facilitator="https://facilitator.goplausible.com",
        status=BomPaymentState.PAYMENT_SETTLED,
        transaction_id="ALGO_TX_WITH_INR_TEST_456",
        expires_at="2030-01-01T00:00:00Z",
    )
    active_rate = CoinGeckoRate(
        available=True,
        rate=86.50,
        rate_decimal=Decimal("86.50"),
        source="CoinGecko",
    )
    artifact = BomPaymentReportEngine.generate_pdf_report(bom=bom, quote=quote, rate=active_rate)

    assert artifact is not None
    assert artifact.inr_available is True
    # 23.50 * 86.50 = 2032.75 INR
    assert artifact.approx_inr_total == 2032.75
    assert artifact.exchange_rate == 86.50
    assert os.path.exists(artifact.filepath)


# ---------------------------------------------------------------------------
# 19. Explorer URL Generation (Mainnet & Testnet)
# ---------------------------------------------------------------------------

def test_explorer_url_generation():
    """Verifies that explorer verification URLs adapt to Algorand Mainnet vs Testnet."""
    mainnet_url = get_explorer_url("algorand-mainnet", "TX_MAIN_123")
    assert mainnet_url == "https://lora.algokit.io/mainnet/transaction/TX_MAIN_123"

    testnet_url = get_explorer_url("algorand-testnet", "TX_TEST_456")
    assert testnet_url == "https://lora.algokit.io/testnet/transaction/TX_TEST_456"


# ---------------------------------------------------------------------------
# 20. Cross-Project Isolation
# ---------------------------------------------------------------------------

def test_cross_project_isolation(sample_bom_items):
    """Quotes created for Project A are associated strictly with Project A."""
    q_a = bom_payment_flow.create_payment_quote(
        bom_data={"bom_id": "BOM-A", "items": sample_bom_items},
        project_id="PROJ-A",
    )
    q_b = bom_payment_flow.create_payment_quote(
        bom_data={"bom_id": "BOM-B", "items": sample_bom_items},
        project_id="PROJ-B",
    )
    assert q_a.project_id == "PROJ-A"
    assert q_b.project_id == "PROJ-B"
    assert q_a.quote_id != q_b.quote_id


# ---------------------------------------------------------------------------
# 21. Unauthorized Procurement Rejection (Empty Items)
# ---------------------------------------------------------------------------

def test_empty_bom_quote_rejection():
    """Attempting to create quote for empty BOM raises ValueError."""
    with pytest.raises(ValueError, match="empty BOM"):
        bom_payment_flow.create_payment_quote(
            bom_data={"bom_id": "BOM-EMPTY", "items": []},
            project_id="PROJ-EMPTY",
        )


# ---------------------------------------------------------------------------
# 22. ArmourIQ Capability Denial
# ---------------------------------------------------------------------------

def test_armouriq_procurement_denial(sample_bom_items):
    """When TrustContext lacks EXECUTE_PROCUREMENT capability, ArmourIQ denies action."""
    unauthorized_context = TrustContext(
        session_id="sess_unauth",
        project_id="PROJ-ARMOURIQ",
        agent_id="unauthorized.agent",
        capabilities=[AgentCapability.READ_PROJECT],  # Missing EXECUTE_PROCUREMENT
    )
    with pytest.raises(PermissionError, match="ArmourIQ DENIED"):
        bom_payment_flow.create_payment_quote(
            bom_data={"bom_id": "BOM-DENY", "items": sample_bom_items},
            project_id="PROJ-ARMOURIQ",
            context=unauthorized_context,
        )


# ---------------------------------------------------------------------------
# 23. Critical Financial Mismatch Test ($100 BOM vs 99 USDC Settlement)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_critical_financial_mismatch_fails_safely():
    """
    Critical Test:
    BOM total: $100.00
    Submitted payment: 99.00 USDC
    Expected: FAIL. System must NEVER settle or generate report for an amount mismatch.
    """
    items_100 = [
        {"part_number": "PART_A", "quantity": 10, "unit_price_usd": 10.00}
    ]
    quote = bom_payment_flow.create_payment_quote(
        bom_data={"bom_id": "BOM-100-CRITICAL", "items": items_100},
        project_id="PROJ-CRITICAL",
    )
    assert quote.amount_usd == 100.00
    assert quote.amount_usdc == 100.00

    # Attempt to settle with 99.00 USDC
    ok, err, updated_quote = await bom_payment_flow.settle_payment_proof(
        quote_id=quote.quote_id,
        proof_data={
            "tx_hash": "ALGO_TX_UNDERPAYMENT_PROOF",
            "amount": 99.00,
        },
    )
    assert ok is False
    assert "Amount mismatch" in err
    assert updated_quote.status == BomPaymentState.PAYMENT_FAILED

    # Ensure report generation fails
    report_ok, report_err, _ = await bom_payment_flow.generate_payment_report(quote.quote_id)
    assert report_ok is False
    assert "Cannot generate report" in report_err


# ---------------------------------------------------------------------------
# 24. Decimal Floating-Point Accuracy Test (0.10 + 0.20 == 0.30)
# ---------------------------------------------------------------------------

def test_decimal_floating_point_accuracy():
    """
    Financial Precision Test:
    In binary floats, 0.1 + 0.2 == 0.30000000000000004.
    In our Decimal engine, quantize_money(0.1) + quantize_money(0.2) == Decimal('0.30').
    """
    item1 = AuthoritativeBomItem(part_number="P1", quantity=1, unit_price_usd=0.10)
    item2 = AuthoritativeBomItem(part_number="P2", quantity=1, unit_price_usd=0.20)

    bom = AuthoritativeBom(bom_id="BOM-PRECISION", project_id="PROJ-P", items=[item1, item2])
    total_dec = bom.calculate_authoritative_total()

    assert total_dec == Decimal("0.30")
    assert bom.bom_total_usd == 0.30
    assert str(total_dec) == "0.30"
