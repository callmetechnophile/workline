"""Authoritative Pydantic models, state machines, and schemas for Workline Item Ordering and Payment Authorization."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# 1. LIFECYCLE & STATE ENUMS
# ============================================================================

class OrderStatus(str, Enum):
    """Explicit Order Lifecycle States (No state skipping permitted)."""
    DRAFT = "DRAFT"
    VALIDATING = "VALIDATING"
    READY_FOR_APPROVAL = "READY_FOR_APPROVAL"
    APPROVED = "APPROVED"
    PAYMENT_REQUIRED = "PAYMENT_REQUIRED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAYMENT_AUTHORIZED = "PAYMENT_AUTHORIZED"
    SUBMITTING = "SUBMITTING"
    SUBMITTED = "SUBMITTED"
    CONFIRMED = "CONFIRMED"
    MANUAL_CHECKOUT_REQUIRED = "MANUAL_CHECKOUT_REQUIRED"
    PARTIALLY_FULFILLED = "PARTIALLY_FULFILLED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class PaymentStatus(str, Enum):
    """Payment lifecycle states."""
    NOT_REQUIRED = "NOT_REQUIRED"
    REQUIRED = "REQUIRED"
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    SETTLED = "SETTLED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    REFUNDED = "REFUNDED"


class ApprovalStatus(str, Enum):
    """Human approval lifecycle states."""
    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class OrderExecutionMode(str, Enum):
    """Vendor order execution capability."""
    AUTOMATED = "AUTOMATED"
    MANUAL = "MANUAL"
    UNAVAILABLE = "UNAVAILABLE"


class ReceiptVerificationStatus(str, Enum):
    """Receipt verification status."""
    UNVERIFIED = "UNVERIFIED"
    RETRIEVED = "RETRIEVED"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class AuditEventType(str, Enum):
    """Immutable audit trail event types."""
    ORDER_CREATED = "ORDER_CREATED"
    ORDER_VALIDATED = "ORDER_VALIDATED"
    PRICE_REVALIDATED = "PRICE_REVALIDATED"
    USER_APPROVED = "USER_APPROVED"
    USER_REJECTED = "USER_REJECTED"
    PAYMENT_REQUEST_CREATED = "PAYMENT_REQUEST_CREATED"
    PAYMENT_SUBMITTED = "PAYMENT_SUBMITTED"
    PAYMENT_AUTHORIZED = "PAYMENT_AUTHORIZED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_EXPIRED = "PAYMENT_EXPIRED"
    PAYMENT_SETTLED = "PAYMENT_SETTLED"
    ORDER_SUBMITTING = "ORDER_SUBMITTING"
    ORDER_SUBMITTED = "ORDER_SUBMITTED"
    ORDER_CONFIRMED = "ORDER_CONFIRMED"
    MANUAL_CHECKOUT_PREPARED = "MANUAL_CHECKOUT_PREPARED"
    RECEIPT_RECEIVED = "RECEIPT_RECEIVED"
    RECEIPT_VERIFIED = "RECEIPT_VERIFIED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    ORDER_FAILED = "ORDER_FAILED"


# ============================================================================
# 2. ORDER LINE ITEMS & FINANCIAL TOTALS
# ============================================================================

class CostBreakdownItem(BaseModel):
    """Explicit itemized cost with currency, source, and confidence status."""
    value: float
    currency: str = "INR"
    source: str = "vendor"                   # vendor, calculated, carrier, tax_table
    status: str = "ESTIMATED"                # ESTIMATED, VERIFIED, CONFIRMED


class OrderTotal(BaseModel):
    """Complete transparent financial calculation for an order."""
    subtotal: CostBreakdownItem
    shipping: CostBreakdownItem
    tax: CostBreakdownItem
    fees: CostBreakdownItem
    total: CostBreakdownItem
    currency: str = "INR"
    exchange_rate: Optional[float] = 1.0
    rate_source: Optional[str] = "Standard RBI Reference"
    rate_timestamp: Optional[str] = None


class OrderItem(BaseModel):
    """Individual line item in an Order."""
    order_item_id: str
    order_id: str
    component_id: str
    bom_item_id: Optional[str] = None
    manufacturer: str
    mpn: str
    description: Optional[str] = None
    quantity: int = 1
    unit_price: float
    currency: str = "INR"
    extended_price: float
    vendor_listing_id: Optional[str] = None
    vendor_name: str
    product_url: Optional[str] = None
    stock_at_validation: Optional[int] = None
    lead_time_at_validation: Optional[int] = None
    datasheet_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ============================================================================
# 3. REVALIDATION MODELS
# ============================================================================

class PriceRevalidationItem(BaseModel):
    """Comparison between BOM-time price/stock and live vendor data."""
    component_id: str
    mpn: str
    vendor_name: str
    bom_unit_price: float
    current_unit_price: float
    price_difference: float
    percentage_change: float
    bom_stock: Optional[int] = None
    current_stock: Optional[int] = None
    is_available: bool = True
    status: str = "UNCHANGED"                # UNCHANGED, INCREASED, DECREASED, OUT_OF_STOCK


class RevalidationReport(BaseModel):
    """Complete pre-order / pre-payment revalidation report."""
    order_id: str
    is_valid: bool
    requires_reapproval: bool
    price_changes_count: int = 0
    stock_changes_count: int = 0
    total_bom_price: float
    total_current_price: float
    total_percentage_change: float
    items: List[PriceRevalidationItem] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    revalidated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ============================================================================
# 4. ORDER PLAN & ORDER MODELS
# ============================================================================

class OrderPlan(BaseModel):
    """Pre-order preparation blueprint derived from an optimized BOM."""
    plan_id: str
    project_id: str
    bom_id: str
    version: int = 1
    selected_vendors: List[str]
    selected_listings: List[str]
    items: List[OrderItem]
    financials: OrderTotal
    currency: str = "INR"
    data_freshness: str = "FRESH"
    vendor_availability: Dict[str, bool] = Field(default_factory=dict)
    alternative_decisions: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Order(BaseModel):
    """Authoritative Order entity tracking lifecycle, payment, approval, and execution."""
    order_id: str
    project_id: str
    bom_id: Optional[str] = None
    procurement_plan_id: Optional[str] = None
    user_id: str = "user:engineer"
    team_id: Optional[str] = "team:default"

    vendor: str
    currency: str = "INR"

    subtotal: float
    shipping_cost: float
    tax: float = 0.0
    fees: float = 0.0
    total: float

    financials: Optional[OrderTotal] = None
    items: List[OrderItem] = Field(default_factory=list)

    status: OrderStatus = OrderStatus.DRAFT
    payment_status: PaymentStatus = PaymentStatus.REQUIRED
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    execution_mode: OrderExecutionMode = OrderExecutionMode.AUTOMATED

    idempotency_key: str = Field(default_factory=lambda: f"idemp_{datetime.now(timezone.utc).timestamp()}")

    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    approved_at: Optional[str] = None
    approved_by: Optional[str] = None
    payment_authorized_at: Optional[str] = None
    submitted_at: Optional[str] = None
    confirmed_at: Optional[str] = None
    cancelled_at: Optional[str] = None

    external_order_id: Optional[str] = None
    receipt_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# 5. PAYMENT MODELS (x402 & Generic Payment Provider)
# ============================================================================

class PaymentRequest(BaseModel):
    """Payment requirement specification generated for an approved order."""
    payment_request_id: str
    order_id: str
    amount: float
    currency: str = "USD"
    network: str = "base-sepolia"             # base, solana, lightning, base-sepolia
    asset: str = "USDC"                      # USDC, ETH, SOL, SAT
    recipient: str                           # Payment address / smart contract
    expires_at: str
    status: PaymentStatus = PaymentStatus.REQUIRED
    provider: str = "x402"
    idempotency_key: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PaymentSession(BaseModel):
    """Payment session state machine record tracking payment authorization and settlement."""
    payment_session_id: str
    order_id: str
    payment_request_id: str
    amount: float
    currency: str = "USD"
    network: str = "base-sepolia"
    asset: str = "USDC"
    recipient: str
    status: PaymentStatus = PaymentStatus.REQUIRED

    challenge_payload: Optional[Dict[str, Any]] = None  # HTTP 402 challenge parameters
    external_payment_id: Optional[str] = None          # Transaction hash / facilitator receipt

    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: str
    authorized_at: Optional[str] = None
    settled_at: Optional[str] = None


# ============================================================================
# 6. POLICIES & LIMITS
# ============================================================================

class OrderPolicy(BaseModel):
    """Team-level or project-level spending, risk, and approval rules."""
    policy_id: str = "policy:default"
    team_id: str = "team:default"
    require_approval: bool = True
    maximum_order_value: float = 15000.0     # Maximum per-order total in INR
    daily_limit: float = 50000.0             # Daily spend ceiling in INR
    monthly_limit: float = 200000.0          # Monthly spend ceiling in INR
    allowed_currencies: List[str] = Field(default_factory=lambda: ["INR", "USD", "EUR"])
    allowed_vendors: List[str] = Field(default_factory=lambda: ["DigiKey", "Mouser", "Robu", "Robocraze"])
    allowed_categories: List[str] = Field(default_factory=list)
    require_price_revalidation: bool = True
    price_change_threshold: float = 0.05     # 5% price change invalidates previous approval
    require_receipt: bool = True
    allow_partial_orders: bool = False


# ============================================================================
# 7. RECEIPTS & MANUAL CHECKOUT
# ============================================================================

class Receipt(BaseModel):
    """Official purchase receipt or invoice record."""
    receipt_id: str
    order_id: str
    vendor: str
    external_order_id: Optional[str] = None
    subtotal: float
    shipping: float
    tax: float = 0.0
    fees: float = 0.0
    total: float
    currency: str = "INR"
    receipt_url: Optional[str] = None
    invoice_url: Optional[str] = None
    issued_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: str = "Vendor Procurement API"
    verification_status: ReceiptVerificationStatus = ReceiptVerificationStatus.UNVERIFIED
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ManualCheckoutPackage(BaseModel):
    """Exported procurement kit for manual vendor checkout when automated order API is unavailable."""
    package_id: str
    order_id: str
    vendor: str
    items: List[OrderItem]
    subtotal: float
    shipping: float
    total: float
    currency: str = "INR"
    checkout_url: str
    instructions: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ============================================================================
# 8. AUDIT EVENT LOG
# ============================================================================

class OrderAuditEvent(BaseModel):
    """Append-only audit trail event for order, payment, and execution lifecycle."""
    event_id: str
    order_id: str
    project_id: str
    user_id: str
    team_id: Optional[str] = "team:default"
    event_type: AuditEventType
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    actor_type: str = "USER"                 # USER, AGENT, SYSTEM, PAYMENT_FACILITATOR
    actor_id: str = "user:engineer"
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
