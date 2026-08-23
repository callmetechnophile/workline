"""
Pydantic Models for x402 Payment Protocol, Challenges, Proofs, and Records.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PaymentStatus(str, Enum):
    """Lifecycle states of an x402 payment record."""
    PAYMENT_REQUIRED = "PAYMENT_REQUIRED"
    PENDING = "PENDING"
    VERIFYING = "VERIFYING"
    SETTLED = "SETTLED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class X402Challenge(BaseModel):
    """HTTP 402 Payment Required Challenge structure."""
    scheme: str = "x402"
    network: str
    asset: str
    asset_id: int
    amount: float
    currency: str = "USD"
    pay_to: str
    nonce: str
    payment_request_id: str
    expires_at: str
    facilitator: str
    service_id: str


class PaymentProof(BaseModel):
    """Cryptographic or transaction proof submitted by client to redeem service."""
    payment_request_id: str
    tx_hash: Optional[str] = None
    signature: Optional[str] = None
    receipt_id: Optional[str] = None
    facilitator_settlement_id: Optional[str] = None
    payer_address: Optional[str] = None


class PaymentRecord(BaseModel):
    """Persistent ledger record of an x402 payment challenge and settlement."""
    id: str
    payment_request_id: str
    service_id: str
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    amount: float
    asset: str = "USDC"
    asset_id: int
    network: str
    payer: Optional[str] = None
    pay_to: str
    transaction_id: Optional[str] = None
    facilitator: str
    status: PaymentStatus = PaymentStatus.PAYMENT_REQUIRED
    idempotency_key: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: str
    settled_at: Optional[str] = None
    executed_at: Optional[str] = None
    error_message: Optional[str] = None
    result_reference: Optional[Dict[str, Any]] = None


class ServiceExecutionRequest(BaseModel):
    """Payload for invoking a payable Workline engineering service."""
    project_id: Optional[str] = "default_project"
    user_id: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: Optional[str] = None


class ServiceExecutionResponse(BaseModel):
    """Successful result returned after verified payment and execution."""
    status: str = "SUCCESS"
    service_id: str
    payment: Dict[str, Any]
    result: Dict[str, Any]
    executed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
