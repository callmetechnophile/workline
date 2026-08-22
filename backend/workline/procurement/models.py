"""Data models and enums for the BOM and Procurement Intelligence Engine."""

from datetime import datetime, timezone
from enum import Enum
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# PHASE 10H ENUMS & MODELS
# ============================================================================

class BomStatus(str, Enum):
    DRAFT = "DRAFT"
    GENERATED = "GENERATED"
    VALIDATED = "VALIDATED"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    READY_FOR_PROCUREMENT = "READY_FOR_PROCUREMENT"
    PARTIALLY_RESOLVED = "PARTIALLY_RESOLVED"
    BLOCKED = "BLOCKED"
    SUPERSEDED = "SUPERSEDED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPORTED = "EXPORTED"


# Alias for legacy compatibility
BOMStatus = BomStatus


class ProcurementStatus(str, Enum):
    UNRESOLVED = "UNRESOLVED"
    RESOLVED = "RESOLVED"
    AVAILABLE = "AVAILABLE"
    PARTIAL = "PARTIAL"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    AMBIGUOUS = "AMBIGUOUS"
    BLOCKED = "BLOCKED"


class CheckStatus(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class FreshnessStatus(str, Enum):
    FRESH = "FRESH"
    STALE = "STALE"
    EXPIRED = "EXPIRED"


class DatasheetStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    FAILED = "FAILED"


class QuantityBreak(BaseModel):
    quantity: int
    unit_price: float


class SupplierOffer(BaseModel):
    supplier_id: str
    supplier_item_id: str
    manufacturer: str
    part_number: str
    ordering_code: str
    description: str
    package: str
    unit_price: float
    currency: str = "INR"
    quantity_breaks: List[QuantityBreak] = Field(default_factory=list)
    stock: int = 0
    lead_time_days: Optional[int] = None
    moq: int = 1
    url_reference: Optional[str] = None
    retrieved_at: float = Field(default_factory=time.time)
    source: str = "digikey"
    confidence: str = "HIGH"  # HIGH, MEDIUM, LOW


class PartVariant(BaseModel):
    canonical_part: str
    ordering_code: str
    manufacturer: str
    package: str
    packaging: str  # Tape & Reel, Cut Tape, Tube, Tray
    temperature_range: Optional[str] = None
    rohs_compliant: bool = True


class BomItem(BaseModel):
    bom_item_id: str
    bom_id: str = "BOM-001"
    reference_designator: str = ""  # e.g. "U1", "R1, R2, R3"
    description: Optional[str] = None
    component_entity_id: str = ""
    part_number: str = ""
    manufacturer: str = ""
    ordering_code: str = ""
    package: Optional[str] = None
    quantity: int = 1
    unit: str = "pcs"
    required_quantity: int = 1
    selected_supplier: Optional[str] = None
    selected_vendor: str = "DigiKey"
    supplier_item_id: Optional[str] = None
    unit_price: float = 0.0
    extended_price: float = 0.0
    currency: str = "INR"
    stock: Optional[int] = 0
    lead_time_days: Optional[int] = None
    moq: int = 1
    status: ProcurementStatus = ProcurementStatus.UNRESOLVED
    validation_status: Any = CheckStatus.PASS
    confidence: str = "HIGH"
    evidence: List[str] = Field(default_factory=list)
    created_at: Any = Field(default_factory=time.time)
    updated_at: Any = Field(default_factory=time.time)

    # Legacy fields
    component_id: Optional[str] = None
    requirement_id: Optional[str] = None
    mpn: Optional[str] = None
    category: Optional[str] = None
    selected_listing_id: Optional[str] = None
    vendor_product_url: Optional[str] = None
    datasheet_url: Optional[str] = None


# Alias for legacy compatibility
BOMItem = BomItem


class BillOfMaterials(BaseModel):
    bom_id: str
    project_id: str
    team_id: str = "default_team"
    version: int = 1
    status: BomStatus = BomStatus.DRAFT
    source_decisions: List[str] = Field(default_factory=list)
    items: List[BomItem] = Field(default_factory=list)
    currency: str = "INR"
    estimated_total: float = 0.0
    total_component_cost: float = 0.0
    estimated_shipping: float = 0.0
    vendor_breakdown: Dict[str, float] = Field(default_factory=dict)
    approved_by: Optional[str] = None
    created_at: Any = Field(default_factory=time.time)
    updated_at: Any = Field(default_factory=time.time)


# Alias for legacy compatibility
BOM = BillOfMaterials


class ProcurementPackageItem(BaseModel):
    manufacturer: str
    part_number: str
    ordering_code: str
    supplier: str
    supplier_item_id: str
    quantity: int
    unit_price: float
    currency: str
    estimated_total: float
    stock: int
    lead_time_days: Optional[int] = None
    moq: int
    validation_status: str = "VALID"


class SupplierBreakdown(BaseModel):
    supplier_id: str
    item_count: int
    subtotal: float


class ProcurementPackage(BaseModel):
    package_id: str
    project_id: str
    team_id: str = "default_team"
    bom_id: str
    bom_version: int
    items: List[ProcurementPackageItem] = Field(default_factory=list)
    subtotal: float = 0.0
    currency: str = "INR"
    supplier_breakdown: List[SupplierBreakdown] = Field(default_factory=list)
    validation_status: str = "READY"  # READY, REVALIDATION_REQUIRED, BLOCKED
    generated_at: float = Field(default_factory=time.time)


# ============================================================================
# LEGACY PHASE 5 / 6 SPECIFICATIONS & VALIDATION MODELS
# ============================================================================

class ElectricalSpecs(BaseModel):
    nominal_voltage: Optional[float] = None
    voltage_min_v: Optional[float] = None
    voltage_max_v: Optional[float] = None
    voltage_min: Optional[float] = None
    voltage_max: Optional[float] = None
    current_max_a: Optional[float] = None
    current_max: Optional[float] = None
    current: Optional[float] = None
    power_dissipation_max_w: Optional[float] = None
    power: Optional[float] = None
    quiescent_current_ua: Optional[float] = None
    efficiency_percentage: Optional[float] = None


class PhysicalSpecs(BaseModel):
    package_type: Optional[str] = None
    package: Optional[str] = None
    mounting_type: Optional[str] = None
    mounting: Optional[str] = None
    pin_count: Optional[int] = None
    dimensions_mm: Optional[str] = None
    dimensions: Optional[str] = None


class InterfaceSpecs(BaseModel):
    supported_protocols: List[str] = Field(default_factory=list)
    i2c: bool = False
    spi: bool = False
    uart: bool = False
    gpio: bool = False
    can: bool = False
    usb: bool = False
    ethernet: bool = False
    wifi: bool = False
    bluetooth: bool = False
    pwm_channels: int = 0
    adc_channels: int = 0
    gpio_count: Optional[int] = None


class EnvironmentSpecs(BaseModel):
    operating_temp_min_c: Optional[float] = None
    operating_temp_max_c: Optional[float] = None
    temperature_min: Optional[float] = None
    temperature_max: Optional[float] = None
    rohs_status: Optional[str] = None
    rohs_compliant: bool = True


class AvailabilitySpecs(BaseModel):
    in_stock: bool = True
    total_inventory: int = 0
    stock: int = 0
    lead_time: Optional[int] = 0
    lead_time_weeks: Optional[int] = None
    lead_time_days: int = 0
    moq: int = 1


class PricingTier(BaseModel):
    quantity: int
    price_inr: float


class PricingSpecs(BaseModel):
    unit_price_inr: float = 0.0
    unit_price: float = 0.0
    currency: str = "INR"
    tiers: List[PricingTier] = Field(default_factory=list)
    quantity_breaks: Dict[int, float] = Field(default_factory=dict)


class VendorListing(BaseModel):
    listing_id: str
    vendor_id: Optional[str] = None
    component_id: Optional[str] = None
    vendor_name: str = ""
    vendor_part_number: Optional[str] = None
    product_url: Optional[str] = None
    unit_price_inr: float = 0.0
    unit_price: float = 0.0
    original_price: float = 0.0
    original_currency: str = "INR"
    currency: str = "INR"
    moq: int = 1
    stock_quantity: int = 0
    stock: int = 0
    in_stock: bool = True
    lead_time_days: int = 0
    location: Optional[str] = None
    source: Optional[str] = None
    pricing_tiers: List[PricingTier] = Field(default_factory=list)
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    freshness: FreshnessStatus = FreshnessStatus.FRESH


class VendorInfo(BaseModel):
    name: Optional[str] = None
    primary_vendor: Optional[str] = None
    location: Optional[str] = None
    product_url: Optional[str] = None
    preferred_vendors: List[str] = Field(default_factory=list)
    listings: List[VendorListing] = Field(default_factory=list)


class DatasheetMetadata(BaseModel):
    datasheet_id: Optional[str] = None
    url: Optional[str] = None
    source_url: Optional[str] = None
    manufacturer: Optional[str] = None
    mpn: Optional[str] = None
    title: Optional[str] = None
    document_type: str = "Datasheet"
    verification_status: DatasheetStatus = DatasheetStatus.UNVERIFIED
    extracted_text_chunks: List[str] = Field(default_factory=list)
    local_path: Optional[str] = None
    file_hash: Optional[str] = None
    page_count: Optional[int] = None
    extracted_at: Optional[str] = None


class DatasheetInfo(BaseModel):
    datasheet_id: Optional[str] = None
    url: Optional[str] = None
    manufacturer: Optional[str] = None
    mpn: Optional[str] = None
    title: Optional[str] = None
    document_type: str = "Datasheet"
    verification_status: DatasheetStatus = DatasheetStatus.UNVERIFIED
    extracted_text_chunks: List[str] = Field(default_factory=list)
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CandidateMetadata(BaseModel):
    provenance_source: str = "nexar"
    source: Optional[str] = None
    score: float = 1.0
    scoring_breakdown: Dict[str, float] = Field(default_factory=dict)
    recommendation: Optional[str] = None
    reason: Optional[str] = None
    confidence_score: float = 1.0
    is_user_verified: bool = False
    notes: Optional[str] = None


class ComponentCandidate(BaseModel):
    component_id: str
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


class ComponentRequirement(BaseModel):
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
    check_name: str
    status: CheckStatus
    expected: Optional[str] = None
    actual: Optional[str] = None
    explanation: str


class DeterministicValidationReport(BaseModel):
    overall_status: CheckStatus
    is_compatible: bool
    checks: List[ValidationCheck] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    evidence: Dict[str, Any] = Field(default_factory=dict)


class OptimizationOption(BaseModel):
    option_id: str
    name: str
    strategy: str
    vendor_count: int
    selected_vendors: List[str]
    total_component_cost: float
    estimated_shipping: float
    estimated_landed_total: float
    currency: str = "INR"
    max_lead_time_days: int
    items: List[BomItem] = Field(default_factory=list)
    tradeoffs: List[str] = Field(default_factory=list)


class ProcurementPlan(BaseModel):
    plan_id: str
    project_id: str
    recommended_option: OptimizationOption
    alternative_options: List[OptimizationOption] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
