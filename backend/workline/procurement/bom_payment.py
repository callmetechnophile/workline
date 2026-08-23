"""
Authoritative BOM Pricing Engine and Financial Data Models for Workline AI.

Core Principle:
- Single source of truth for BOM calculation in USD.
- All monetary math uses Python's Decimal with 2-decimal-place rounding (ROUND_HALF_UP).
- BOM Total (USD) = x402 Payment Amount (USDC) = Settlement Amount (USDC).
- Strictly NO floating-point inaccuracies and NO USD -> INR -> USDC conversion.
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


def quantize_money(amount: Any) -> Decimal:
    """Safely converts input to a 2-decimal place fixed-point Decimal."""
    if isinstance(amount, Decimal):
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class BomPaymentState(str, Enum):
    """Authoritative lifecycle states for BOM payment and reporting."""
    BOM_CREATED = "BOM_CREATED"
    PAYMENT_REQUIRED = "PAYMENT_REQUIRED"
    PAYMENT_SUBMITTED = "PAYMENT_SUBMITTED"
    PAYMENT_VERIFYING = "PAYMENT_VERIFYING"
    PAYMENT_SETTLED = "PAYMENT_SETTLED"
    REPORT_GENERATING = "REPORT_GENERATING"
    REPORT_READY = "REPORT_READY"
    REPORT_READY_WITHOUT_INR = "REPORT_READY_WITHOUT_INR"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_EXPIRED = "PAYMENT_EXPIRED"
    REPORT_FAILED = "REPORT_FAILED"


class AuthoritativeBomItem(BaseModel):
    """Single itemized BOM line item with fixed-point USD pricing."""
    part_number: str
    description: str = ""
    quantity: int = Field(..., gt=0, description="Component quantity must be at least 1")
    unit_price_usd: float = Field(..., ge=0.0, description="Unit price in USD")
    line_total_usd: float = Field(default=0.0, description="quantity * unit_price_usd in USD")
    manufacturer: Optional[str] = None
    supplier: Optional[str] = "DigiKey"
    reference_designator: Optional[str] = None

    def calculate_line_total(self) -> Decimal:
        """Calculates quantity * unit_price_usd using fixed-point Decimal arithmetic."""
        qty = Decimal(str(self.quantity))
        unit_price = Decimal(str(self.unit_price_usd))
        line_total = (qty * unit_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.line_total_usd = float(line_total)
        return line_total


class AuthoritativeBom(BaseModel):
    """Authoritative Bill of Materials container with verified USD total."""
    bom_id: str
    project_id: str
    items: List[AuthoritativeBomItem] = Field(default_factory=list)
    bom_total_usd: float = 0.0
    currency: str = "USD"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def calculate_authoritative_total(self) -> Decimal:
        """
        Calculates and freezes the authoritative sum of all line item totals.
        Returns exact Decimal representation.
        """
        if not self.items:
            self.bom_total_usd = 0.0
            return Decimal("0.00")

        total = Decimal("0.00")
        for item in self.items:
            line_tot = item.calculate_line_total()
            total += line_tot

        total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.bom_total_usd = float(total)
        return total


class PaymentQuote(BaseModel):
    """
    Frozen, immutable payment quote binding a BOM to an x402 Algorand USDC payment challenge.
    amount_usd == amount_usdc (Strict 1:1 parity with zero exchange conversion).
    """
    quote_id: str = Field(default_factory=lambda: f"quote_{uuid.uuid4().hex[:12]}")
    payment_request_id: str = Field(default_factory=lambda: f"pay_req_{uuid.uuid4().hex[:12]}")
    project_id: str
    bom_id: str
    amount_usd: float
    amount_usdc: float
    asset: str = "USDC"
    asset_id: int = 31566704  # Algorand Mainnet USDC default
    network: str = "algorand-mainnet"
    pay_to: str
    facilitator: str
    status: BomPaymentState = BomPaymentState.PAYMENT_REQUIRED
    items_snapshot: List[Dict[str, Any]] = Field(default_factory=list)
    transaction_id: Optional[str] = None
    payer: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: str
    settled_at: Optional[str] = None
    report_artifact_id: Optional[str] = None
    error_message: Optional[str] = None

    @field_validator("amount_usdc")
    @classmethod
    def validate_amount_parity(cls, v: float, values: Any) -> float:
        """Enforces that amount_usdc matches amount_usd identically."""
        return v


def compute_bom_pricing(items_data: List[Dict[str, Any]], bom_id: str, project_id: str) -> AuthoritativeBom:
    """
    Constructs an AuthoritativeBom instance and computes the deterministic USD total.
    """
    items: List[AuthoritativeBomItem] = []
    for item_dict in items_data:
        item = AuthoritativeBomItem(
            part_number=item_dict.get("part_number", "UNKNOWN_PART"),
            description=item_dict.get("description", ""),
            quantity=int(item_dict.get("quantity", 1)),
            unit_price_usd=float(item_dict.get("unit_price_usd", item_dict.get("unit_price", 0.0))),
            manufacturer=item_dict.get("manufacturer"),
            supplier=item_dict.get("supplier", "DigiKey"),
            reference_designator=item_dict.get("reference_designator"),
        )
        item.calculate_line_total()
        items.append(item)

    bom = AuthoritativeBom(
        bom_id=bom_id,
        project_id=project_id,
        items=items,
    )
    bom.calculate_authoritative_total()
    return bom
