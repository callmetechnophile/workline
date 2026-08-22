"""Workline Procurement & Component Intelligence Subsystem (Nexar Primary + Scrapling Fallback)."""

from backend.workline.procurement.cache import ProcurementCache, nexar_cache, scrapling_cache
from backend.workline.procurement.engine import ProcurementEngine, procurement_engine
from backend.workline.procurement.models import (
    BOM,
    BOMItem,
    BOMStatus,
    CheckStatus,
    ComponentCandidate,
    ComponentRequirement,
    DatasheetInfo,
    DatasheetMetadata,
    DatasheetStatus,
    DeterministicValidationReport,
    ElectricalSpecs,
    EnvironmentSpecs,
    FreshnessStatus,
    InterfaceSpecs,
    OptimizationOption,
    PhysicalSpecs,
    PricingSpecs,
    ProcurementPlan,
    ValidationCheck,
    VendorInfo,
    VendorListing,
)
from backend.workline.procurement.normalize import (
    ComponentNormalizer,
    PricingNormalizer,
    generate_component_id,
    normalize_manufacturer,
    normalize_mpn,
)
from backend.workline.procurement.optimize import ProcurementOptimizer
from backend.workline.procurement.search import ComponentSearchEngine
from backend.workline.procurement.shipping import ShippingCalculator, ShippingEstimate
from backend.workline.procurement.validate import TechnicalValidator

__all__ = [
    "ProcurementEngine",
    "procurement_engine",
    "ComponentSearchEngine",
    "TechnicalValidator",
    "ProcurementOptimizer",
    "ShippingCalculator",
    "ShippingEstimate",
    "ComponentNormalizer",
    "PricingNormalizer",
    "normalize_mpn",
    "normalize_manufacturer",
    "generate_component_id",
    "ProcurementCache",
    "nexar_cache",
    "scrapling_cache",
    "ComponentCandidate",
    "VendorListing",
    "DatasheetMetadata",
    "DatasheetInfo",
    "DatasheetStatus",
    "ElectricalSpecs",
    "PhysicalSpecs",
    "InterfaceSpecs",
    "EnvironmentSpecs",
    "PricingSpecs",
    "VendorInfo",
    "FreshnessStatus",
    "CheckStatus",
    "ComponentRequirement",
    "BOMItem",
    "BOM",
    "BOMStatus",
    "ValidationCheck",
    "DeterministicValidationReport",
    "OptimizationOption",
    "ProcurementPlan",
]
