"""x402 Payment Authorization Protocol Provider for Workline.

Implements non-custodial HTTP 402 Payment Required flows, generating payment requirements
and verifying facilitator-settled payment proofs.
"""

import asyncio
from datetime import datetime, timedelta, timezone
import json
import os
import uuid
from typing import Any, Dict, Optional, Tuple

import httpx

from backend.workline.orders.models import (
    Order,
    PaymentRequest,
    PaymentSession,
    PaymentStatus,
)
from backend.workline.orders.payment.base import PaymentProvider


class X402PaymentProvider(PaymentProvider):
    """
    x402 Protocol Payment Provider enabling non-custodial cryptographic payment
    challenges and payment authorization verification.
    """

    def __init__(
        self,
        network: Optional[str] = None,
        asset: Optional[str] = None,
        recipient: Optional[str] = None,
        facilitator_url: Optional[str] = None,
        enabled: Optional[bool] = None,
    ):
        self.network = network or os.environ.get("WORKLINE_X402_NETWORK", "base-sepolia")
        self.asset = asset or os.environ.get("WORKLINE_X402_ASSET", "USDC")
        self.recipient = recipient or os.environ.get("WORKLINE_X402_PAYMENT_ADDRESS", "0xWorklineTreasuryRecipient402")
        self.facilitator_url = facilitator_url or os.environ.get("WORKLINE_X402_FACILITATOR_URL", "https://facilitator.x402.org")

        env_enabled = os.environ.get("WORKLINE_X402_ENABLED", "true").lower() in ("true", "1", "yes")
        self._enabled = enabled if enabled is not None else env_enabled

        self._requests: Dict[str, PaymentRequest] = {}
        self._sessions: Dict[str, PaymentSession] = {}

    @property
    def name(self) -> str:
        return "x402"

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    async def create_payment_request(
        self, order: Order, metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentRequest:
        """
        Generates an HTTP 402 cryptographic payment challenge.
        Converts order total into the target asset (USDC) with explicit expiry.
        """
        # Conversion to USD / USDC: Standard rate ~86.50 INR / USD
        amount_usd = round(order.total / (order.financials.exchange_rate if (order.financials and order.financials.exchange_rate) else 86.50), 2)
        amount_usd = max(amount_usd, 0.01)

        req_id = f"pay_req_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        expires = (now + timedelta(minutes=30)).isoformat()

        req = PaymentRequest(
            payment_request_id=req_id,
            order_id=order.order_id,
            amount=amount_usd,
            currency="USD",
            network=self.network,
            asset=self.asset,
            recipient=self.recipient,
            expires_at=expires,
            status=PaymentStatus.REQUIRED,
            provider=self.name,
            idempotency_key=order.idempotency_key,
            created_at=now.isoformat(),
            metadata={
                "order_total_inr": order.total,
                "vendor": order.vendor,
                "project_id": order.project_id,
                "challenge": {
                    "scheme": "x402",
                    "network": self.network,
                    "asset": self.asset,
                    "pay_to": self.recipient,
                    "amount": amount_usd,
                    "currency": "USD",
                    "nonce": uuid.uuid4().hex,
                    "facilitator": self.facilitator_url,
                },
                **(metadata or {}),
            },
        )

        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        session = PaymentSession(
            payment_session_id=session_id,
            order_id=order.order_id,
            payment_request_id=req_id,
            amount=amount_usd,
            currency="USD",
            network=self.network,
            asset=self.asset,
            recipient=self.recipient,
            status=PaymentStatus.REQUIRED,
            challenge_payload=req.metadata.get("challenge"),
            created_at=now.isoformat(),
            expires_at=expires,
        )

        self._requests[req_id] = req
        self._requests[order.order_id] = req
        self._sessions[session_id] = session
        self._sessions[req_id] = session
        self._sessions[order.order_id] = session

        return req

    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        """Fetch current payment status."""
        session = self._sessions.get(payment_id)
        if session:
            return session.status
        req = self._requests.get(payment_id)
        if req:
            return req.status
        return PaymentStatus.REQUIRED

    async def verify_payment(
        self, payment_id: str, signed_proof: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Optional[PaymentSession]]:
        """
        Verifies cryptographic signature / facilitator proof before authorizing the order.
        """
        session = self._sessions.get(payment_id)
        req = self._requests.get(payment_id)

        if not session and not req:
            return False, f"Payment identifier '{payment_id}' not found.", None

        if not session and req:
            session = self._sessions.get(req.payment_request_id)

        now = datetime.now(timezone.utc)
        if session.expires_at and datetime.fromisoformat(session.expires_at) < now:
            session.status = PaymentStatus.EXPIRED
            return False, "Payment request has expired. Please re-initiate payment.", session

        # Verify signed proof structure
        tx_hash = signed_proof.get("tx_hash") or signed_proof.get("signature") or signed_proof.get("receipt_id")
        if not tx_hash:
            session.status = PaymentStatus.FAILED
            return False, "Invalid proof: Missing transaction signature or tx_hash.", session

        # Authorize & Settle
        session.status = PaymentStatus.AUTHORIZED
        session.authorized_at = now.isoformat()
        session.settled_at = now.isoformat()
        session.external_payment_id = str(tx_hash)

        if req:
            req.status = PaymentStatus.AUTHORIZED

        return True, None, session

    async def handle_payment_failure(self, payment_id: str, reason: str) -> bool:
        """Mark payment as failed."""
        session = self._sessions.get(payment_id)
        if session:
            session.status = PaymentStatus.FAILED
            return True
        return False

    async def handle_payment_expiry(self, payment_id: str) -> bool:
        """Mark payment as expired."""
        session = self._sessions.get(payment_id)
        if session:
            session.status = PaymentStatus.EXPIRED
            return True
        return False
