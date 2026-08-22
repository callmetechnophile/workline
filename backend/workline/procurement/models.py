"""Canonical Pydantic models for Workline Procurement, Component Intelligence, and BOM Lifecycles."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# 1. ENUMS
# ============================================================================

class FreshnessStatus(str, Enum):
    """Vendor pricing and inventory data freshness."""
    FRESH = "FRESH"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


class DatasheetStatus(str, Enum):
    """Datasheet verification lifecycle status."""
    UNVERIFIED = "UNVERIFIED"
    RETRIEVED = "RETRIEVED"
    PARSED = "PARSED"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class CheckStatus(str, Enum):
    """Deterministic validation status for electrical/interface constraints."""
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class BOMStatus(str, Enum):
    """Engineering Bill of Materials lifecycle status."""
    DRAFT = "DRAFT"
    ANALYZING = "ANALYZING"
    VALIDATING = "VALIDATING"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


# ============================================================================
# 2. CANONICAL HARDWARE SPECIFICATIONS (All support None / UNKNOWN)
# ============================================================================

class ElectricalSpecs(BaseModel):
    """Canonical electrical operating characteristics."""
    voltage_min: Optional[float] = None
    voltage_max: Optional[float] = None
    nominal_voltage: Optional[float] = None
    current: Optional[float] = None          # Nominal/max current in Amperes
    current_max: Optional[float] = None      # Explicit max current in Amperes
    power: Optional[float] = None            # Max power in Watts
    raw_specs: Dict[str, Any] = Field(default_factory=dict)


class PhysicalSpecs(BaseModel):
    """Canonical physical packaging and mounting."""
    package: Optional[str] = None            # e.g., 'QFN-16', 'TO-220', 'Module'
    dimensions: Optional[str] = None         # e.g., '3.0 x 3.0 mm'
    mounting: Optional[str] = None           # 'Surface Mount', 'Through Hole', 'Chassis'
    mounting_type: Optional[str] = None      # Alias for mounting
    pin_count: Optional[int] = None


class InterfaceSpecs(BaseModel):
    """Canonical digital and analog interfaces."""
    i2c: Optional[bool] = None
    spi: Optional[bool] = None
    uart: Optional[bool] = None
    gpio: Optional[bool] = None
    can: Optional[bool] = None
    usb: Optional[bool] = None
    ethernet: Optional[bool] = None
    pwm_channels: Optional[int] = None
    adc_channels: Optional[int] = None
    other: List[str] = Field(default_factory=list)


class EnvironmentSpecs(BaseModel):
    """Canonical operating environment boundaries."""
    temperature_min: Optional[float] = None  # Celsius
    temperature_max: Optional[float] = None  # Celsius
    rohs_compliant: Optional[bool] = None


class AvailabilitySpecs(BaseModel):
    """Canonical availability and inventory metrics."""
    stock: Optional[int] = None
    in_stock: Optional[bool] = None
    lead_time: Optional[int] = None          # In days
    lead_time_days: Optional[int] = None     # Alias in days


class PricingSpecs(BaseModel):
    """Canonical pricing structure."""
    unit_price: Optional[float] = None       # Normalized to INR
    currency: str = "INR"
    quantity_breaks: Dict[int, float] = Field(default_factory=dict)  # Qty -> Unit Price


class VendorInfo(BaseModel):
    """Canonical vendor/supplier descriptor."""
    name: str = "Unknown Vendor"
    vendor_id: Optional[str] = None
    product_url: Optional[str] = None
    location: Optional[str] = "Global"


class DatasheetInfo(BaseModel):
    """Canonical datasheet and document descriptor."""
    datasheet_id: str
    url: str
    title: Optional[str] = None
    document_type: str = "Datasheet"         # Datasheet, AppNote, Guidelines, Reference Manual
    verification_status: DatasheetStatus = DatasheetStatus.UNVERIFIED
    extracted_text_chunks: List[str] = Field(default_factory=list)


class CandidateMetadata(BaseModel):
    """Source origin, retrieval timestamp, and explainable scoring."""
    source: str = "Nexar"                    # Nexar, Scrapling, Manual
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    score: float = 1.0
    scoring_breakdown: Dict[str, float] = Field(default_factory=dict)
    recommendation: str = "RECOMMENDED"      # RECOMMENDED, ALTERNATIVE, CAUTION
    reason: Optional[str] = None


# ============================================================================
# 3. VENDOR LISTING & DATASHEET MODELS
# ============================================================================

class VendorListing(BaseModel):
    """A distinct commercial offer from a distributor or vendor."""
    listing_id: str
    component_id: str
    vendor_id: Optional[str] = None
    vendor_name: str
    product_url: str
    unit_price: Optional[float] = None       # Normalized to INR
    original_price: Optional[float] = None
    original_currency: Optional[str] = "USD"
    currency: str = "INR"
    quantity_breaks: Dict[int, float] = Field(default_factory=dict)
    stock: Optional[int] = None
    in_stock: bool = True
    lead_time: Optional[int] = None
    lead_time_days: Optional[int] = None
    moq: int = 1
    location: Optional[str] = "Global"
    freshness: FreshnessStatus = FreshnessStatus.FRESH
    source: str = "Nexar"
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DatasheetMetadata(BaseModel):
    """Comprehensive technical document metadata."""
    datasheet_id: str
    component_id: Optional[str] = None
    url: str
    source: str = "Nexar"
    manufacturer: Optional[str] = None
    mpn: Optional[str] = None
    title: Optional[str] = None
    document_type: str = "Datasheet"
    verification_status: DatasheetStatus = DatasheetStatus.UNVERIFIED
    extracted_text_chunks: List[str] = Field(default_factory=list)
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ============================================================================
# 4. CANONICAL COMPONENT CANDIDATE
# ============================================================================

class ComponentCandidate(BaseModel):
    """
    Authoritative canonical component model unifying Nexar, Scrapling,
    and manual entries into a single normalized identity.
    """
    component_id: str                        # component:<mfr>_<mpn>
    manufacturer: str
    manufacturer_part_number: str
    product_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None

    electrical: ElectricalSpecs = Field(default_factory=ElectricalSpecs)
    physical: PhysicalSpecs = Field(default_factory=PhysicalSpecs)
    interfaces: InterfaceSpecs = Field(default_factory=InterfaceSpecs)
    environment: EnvironmentSpecs = Field(default_factory=EnvironmentSpecs)
    availability: AvailabilitySpecs = Field(default_factory=AvailabilitySpecs)
    pricing: PricingSpecs = Field(default_factory=PricingSpecs)
    vendor: VendorInfo = Field(default_factory=VendorInfo)
    datasheet: Optional[DatasheetInfo] = None

    listings: List[VendorListing] = Field(default_factory=list)
    metadata: CandidateMetadata = Field(default_factory=CandidateMetadata)


# ============================================================================
# 5. PROCUREMENT, BOM & VALIDATION MODELS
# ============================================================================

class ComponentRequirement(BaseModel):
    """Engineering requirement definition for component selection."""
    requirement_id: str
    category: str
    description: Optional[str] = None
    quantity: int = 1
    nominal_voltage: Optional[float] = None
    voltage_min: Optional[float] = None
    voltage_max: Optional[float] = None
    required_current_min_a: Optional[float] = None
    required_power_w: Optional[float] = None
    required_interfaces: List[str] = Field(default_factory=list)
    package_preference: Optional[str] = None
    target_unit_budget_inr: Optional[float] = None


class ValidationCheck(BaseModel):
    """An individual deterministic parameter check."""
    check_name: str
    status: CheckStatus                      # PASS, WARN, FAIL, UNKNOWN
    expected: Optional[str] = None
    actual: Optional[str] = None
    explanation: str


class DeterministicValidationReport(BaseModel):
    """Complete deterministic compatibility report."""
    overall_status: CheckStatus              # PASS, WARN, FAIL, UNKNOWN
    is_compatible: bool
    checks: List[ValidationCheck] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    evidence: Dict[str, Any] = Field(default_factory=dict)


class BOMItem(BaseModel):
    """Individual line item in an engineering Bill of Materials."""
    bom_item_id: str
    component_id: str
    requirement_id: Optional[str] = None
    manufacturer: str
    mpn: str
    category: Optional[str] = None
    description: Optional[str] = None
    quantity: int = 1
    selected_vendor: str = "DigiKey"
    selected_listing_id: Optional[str] = None
    vendor_product_url: Optional[str] = None
    unit_price: float                        # INR
    extended_price: float                    # INR (unit_price * quantity)
    currency: str = "INR"
    stock: Optional[int] = None
    lead_time_days: Optional[int] = None
    datasheet_url: Optional[str] = None
    validation_status: CheckStatus = CheckStatus.PASS


class BOM(BaseModel):
    """Authoritative Bill of Materials with landed cost and lifecycle tracking."""
    bom_id: str
    project_id: str
    version: int = 1
    status: BOMStatus = BOMStatus.DRAFT
    total_component_cost: float = 0.0        # INR
    estimated_shipping: float = 0.0          # INR
    estimated_total: float = 0.0             # INR
    currency: str = "INR"
    items: List[BOMItem] = Field(default_factory=list)
    vendor_breakdown: Dict[str, float] = Field(default_factory=dict)
    approved_by: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class OptimizationOption(BaseModel):
    """Procurement sourcing trade-off scenario."""
    option_id: str
    name: str                                # e.g., 'Consolidated Domestic Sourcing'
    strategy: str                            # lowest_cost, consolidated, fastest_delivery
    vendor_count: int
    selected_vendors: List[str]
    total_component_cost: float              # INR
    estimated_shipping: float                # INR
    estimated_landed_total: float            # INR
    currency: str = "INR"
    max_lead_time_days: int
    items: List[BOMItem] = Field(default_factory=list)
    tradeoffs: List[str] = Field(default_factory=list)


class ProcurementPlan(BaseModel):
    """Comprehensive procurement recommendation report."""
    plan_id: str
    project_id: str
    recommended_option: OptimizationOption
    alternative_options: List[OptimizationOption] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
