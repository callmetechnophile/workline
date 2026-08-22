"""Unit and integration tests for PaymentProvider, x402 Protocol, and Payment Verification."""

import asyncio
import pytest
from backend.workline.orders.models import (
    ApprovalStatus,
    Order,
    OrderStatus,
    PaymentStatus,
)
from backend.workline.orders.payment.mock import MockPaymentProvider
from backend.workline.orders.payment.verification import PaymentVerificationService
from backend.workline.orders.payment.x402 import X402PaymentProvider
from backend.workline.orders.service import OrderService


def test_x402_payment_request_generation():
    """Test x402 payment challenge construction with amount, asset, network, recipient, and expiry."""
    async def _run():
        provider = X402PaymentProvider(network="base-sepolia", asset="USDC")
        order = Order(
            order_id="WL-ORD-X402-TEST",
            project_id="test_proj",
            vendor="DigiKey",
            currency="INR",
            subtotal=865.0,
            shipping_cost=0.0,
            total=865.0,
        )

        req = await provider.create_payment_request(order)
        assert req.order_id == "WL-ORD-X402-TEST"
        assert req.asset == "USDC"
        assert req.network == "base-sepolia"
        assert req.amount == 10.0  # 865 INR / 86.50 = $10.00
        assert req.status == PaymentStatus.REQUIRED
        assert "challenge" in req.metadata
        assert req.metadata["challenge"]["pay_to"] is not None

    asyncio.run(_run())


def test_x402_payment_verification_success():
    """Test cryptographic payment verification and settlement."""
    async def _run():
        provider = X402PaymentProvider()
        order = Order(
            order_id="WL-ORD-VERIFY",
            project_id="test_proj",
            vendor="Mouser",
            currency="INR",
            subtotal=1000.0,
            shipping_cost=0.0,
            total=1000.0,
        )
        req = await provider.create_payment_request(order)

        proof = {
            "tx_hash": "0x402_test_transaction_hash_verified",
            "signature": "0x_sig_proof_789",
        }

        ok, err, session = await provider.verify_payment(req.payment_request_id, proof)
        assert ok is True
        assert err is None
        assert session is not None
        assert session.status == PaymentStatus.AUTHORIZED
        assert session.external_payment_id == "0x402_test_transaction_hash_verified"

    asyncio.run(_run())


def test_payment_verification_enforcement():
    """Test that PaymentVerificationService blocks unverified/invalid proofs."""
    async def _run():
        provider = X402PaymentProvider()
        verifier = PaymentVerificationService(provider=provider)

        order = Order(
            order_id="WL-ORD-FAIL",
            project_id="p1",
            vendor="Robu",
            currency="INR",
            subtotal=500.0,
            shipping_cost=0.0,
            total=500.0,
        )
        req = await provider.create_payment_request(order)

        # Invalid proof (missing tx_hash / signature)
        bad_proof = {}
        ok, err, session = await verifier.verify_payment_proof(order, req.payment_request_id, bad_proof)
        assert ok is False
        assert "Invalid proof" in err

    asyncio.run(_run())


def test_mock_payment_provider_states():
    """Test MockPaymentProvider simulation for authorization, failure, and expiry."""
    async def _run():
        # 1. Successful simulation
        mock_ok = MockPaymentProvider(default_status=PaymentStatus.AUTHORIZED)
        order = Order(
            order_id="WL-MOCK-1",
            project_id="p1",
            vendor="Robu",
            currency="INR",
            subtotal=100.0,
            shipping_cost=0.0,
            total=100.0,
        )
        req1 = await mock_ok.create_payment_request(order)
        ok, _, sess1 = await mock_ok.verify_payment(req1.payment_request_id, {"tx_hash": "0xMockHash"})
        assert ok is True
        assert sess1.status == PaymentStatus.AUTHORIZED

        # 2. Failed simulation
        mock_fail = MockPaymentProvider(default_status=PaymentStatus.FAILED)
        req2 = await mock_fail.create_payment_request(order)
        ok_fail, _, sess2 = await mock_fail.verify_payment(req2.payment_request_id, {})
        assert ok_fail is False
        assert sess2.status == PaymentStatus.FAILED

    asyncio.run(_run())
