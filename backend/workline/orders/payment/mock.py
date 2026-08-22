"""Mock Payment Provider for testing and local deterministic CI runs."""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple
import uuid

from backend.workline.orders.models import (
    Order,
    PaymentRequest,
    PaymentSession,
    PaymentStatus,
)
from backend.workline.orders.payment.base import PaymentProvider


class MockPaymentProvider(PaymentProvider):
    """Simulated payment provider that supports instant authorization, failures, and expirations for testing."""

    def __init__(self, default_status: PaymentStatus = PaymentStatus.AUTHORIZED):
        self.default_status = default_status
        self._requests: Dict[str, PaymentRequest] = {}
        self._sessions: Dict[str, PaymentSession] = {}

    @property
    def name(self) -> str:
        return "MockPayment"

    @property
    def is_enabled(self) -> bool:
        return True

    async def create_payment_request(
        self, order: Order, metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentRequest:
        req_id = f"mock_pay_{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)
        expires = (now + timedelta(minutes=15)).isoformat()

        req = PaymentRequest(
            payment_request_id=req_id,
            order_id=order.order_id,
            amount=round(order.total / 86.50, 2),
            currency="USD",
            network="mock-network",
            asset="USDC",
            recipient="0xMockTreasury",
            expires_at=expires,
            status=PaymentStatus.REQUIRED,
            provider=self.name,
            idempotency_key=order.idempotency_key,
            created_at=now.isoformat(),
        )

        session = PaymentSession(
            payment_session_id=f"sess_{uuid.uuid4().hex[:8]}",
            order_id=order.order_id,
            payment_request_id=req_id,
            amount=req.amount,
            currency="USD",
            network="mock-network",
            asset="USDC",
            recipient="0xMockTreasury",
            status=PaymentStatus.REQUIRED,
            created_at=now.isoformat(),
            expires_at=expires,
        )

        self._requests[req_id] = req
        self._requests[order.order_id] = req
        self._sessions[req_id] = session
        self._sessions[order.order_id] = session

        return req

    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        session = self._sessions.get(payment_id)
        if session:
            return session.status
        return PaymentStatus.REQUIRED

    async def verify_payment(
        self, payment_id: str, signed_proof: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Optional[PaymentSession]]:
        session = self._sessions.get(payment_id)
        if not session:
            return False, "Session not found", None

        if self.default_status == PaymentStatus.FAILED or signed_proof.get("simulate_failure"):
            session.status = PaymentStatus.FAILED
            return False, "Simulated payment failure", session

        if self.default_status == PaymentStatus.EXPIRED or signed_proof.get("simulate_expiry"):
            session.status = PaymentStatus.EXPIRED
            return False, "Simulated payment expiry", session

        now = datetime.now(timezone.utc).isoformat()
        session.status = PaymentStatus.AUTHORIZED
        session.authorized_at = now
        session.settled_at = now
        session.external_payment_id = signed_proof.get("tx_hash", f"mock_tx_{uuid.uuid4().hex[:8]}")

        req = self._requests.get(session.payment_request_id)
        if req:
            req.status = PaymentStatus.AUTHORIZED

        return True, None, session

    async def handle_payment_failure(self, payment_id: str, reason: str) -> bool:
        session = self._sessions.get(payment_id)
        if session:
            session.status = PaymentStatus.FAILED
            return True
        return False

    async def handle_payment_expiry(self, payment_id: str) -> bool:
        session = self._sessions.get(payment_id)
        if session:
            session.status = PaymentStatus.EXPIRED
            return True
        return False
