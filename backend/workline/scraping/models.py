"""Data models for vendor scraping, component normalization, and datasheet metadata."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FreshnessStatus(str, Enum):
    FRESH = "FRESH"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


class DatasheetStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    RETRIEVED = "RETRIEVED"
    PARSED = "PARSED"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class ElectricalSpecs(BaseModel):
    voltage_min: Optional[float] = None
    voltage_max: Optional[float] = None
    nominal_voltage: Optional[float] = None
    current_min: Optional[float] = None
    current_max: Optional[float] = None
    power_mw: Optional[float] = None
    raw_specs: Dict[str, Any] = Field(default_factory=dict)


class PhysicalSpecs(BaseModel):
    package: Optional[str] = None
    dimensions: Optional[str] = None
    mounting_type: Optional[str] = None  # SMD, Through-Hole, Module


class InterfaceSpecs(BaseModel):
    i2c: bool = False
    spi: bool = False
    uart: bool = False
    gpio_count: Optional[int] = None
    can: bool = False
    usb: bool = False
    ethernet: bool = False
    adc_channels: Optional[int] = None
    pwm_channels: Optional[int] = None
    other_interfaces: List[str] = Field(default_factory=list)


class EnvironmentSpecs(BaseModel):
    temperature_min_c: Optional[float] = None
    temperature_max_c: Optional[float] = None
    operating_temp_range: Optional[str] = None


class QuantityBreak(BaseModel):
    quantity: int
    unit_price: float
    currency: str = "INR"


class VendorListing(BaseModel):
    listing_id: str
    vendor_name: str
    product_url: str
    sku: Optional[str] = None
    unit_price: Optional[float] = None
    currency: str = "INR"
    quantity_breaks: List[QuantityBreak] = Field(default_factory=list)
    stock: Optional[int] = None
    in_stock: bool = False
    lead_time_days: Optional[int] = None
    location: Optional[str] = None
    freshness: FreshnessStatus = FreshnessStatus.FRESH
    retrieved_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)


class DatasheetMetadata(BaseModel):
    datasheet_id: str
    component_id: Optional[str] = None
    url: str
    manufacturer: Optional[str] = None
    mpn: Optional[str] = None
    title: Optional[str] = None
    document_type: str = "Datasheet"  # Datasheet, User Manual, Errata, AppNote
    file_size_bytes: Optional[int] = None
    verification_status: DatasheetStatus = DatasheetStatus.UNVERIFIED
    page_count: Optional[int] = None
    extracted_text_chunks: List[str] = Field(default_factory=list)
    retrieved_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ShippingEstimate(BaseModel):
    origin: str
    destination: str = "India"
    carrier: str
    service: str
    distance_km: Optional[float] = None
    estimated_cost: float
    currency: str = "INR"
    confidence: str = "ESTIMATED"  # EXACT, ESTIMATED, UNKNOWN
    source: str = "Standard Freight Baseline"
    retrieved_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class RawVendorResult(BaseModel):
    vendor: str
    source_url: str
    product_url: str
    product_name: str
    manufacturer: Optional[str] = None
    mpn: Optional[str] = None
    sku: Optional[str] = None
    price_raw: Optional[str] = None
    currency: Optional[str] = None
    stock_raw: Optional[str] = None
    lead_time_raw: Optional[str] = None
    datasheet_url: Optional[str] = None
    description: Optional[str] = None
    spec_table: Dict[str, str] = Field(default_factory=dict)
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)
    retrieved_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ComponentCandidate(BaseModel):
    component_id: str
    manufacturer: str
    manufacturer_part_number: str
    product_name: str
    category: str
    description: Optional[str] = None
    electrical: ElectricalSpecs = Field(default_factory=ElectricalSpecs)
    physical: PhysicalSpecs = Field(default_factory=PhysicalSpecs)
    interfaces: InterfaceSpecs = Field(default_factory=InterfaceSpecs)
    environment: EnvironmentSpecs = Field(default_factory=EnvironmentSpecs)
    listings: List[VendorListing] = Field(default_factory=list)
    datasheet: Optional[DatasheetMetadata] = None
    alternatives: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
