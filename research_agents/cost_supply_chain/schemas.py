"""
Pydantic schemas and domain models for Agent #25 (CostSupplyChainAgent).
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    INR = "INR"
    CAD = "CAD"
    AUD = "AUD"
    CNY = "CNY"
    CHF = "CHF"
    KRW = "KRW"
    TWD = "TWD"
    SGD = "SGD"
    MXN = "MXN"


class LifecycleStatus(str, Enum):
    ACTIVE = "ACTIVE"
    NRND = "NRND"  # Not Recommended for New Designs
    EOL = "EOL"    # End of Life
    OBSOLETE = "OBSOLETE"
    UNANNOUNCED = "UNANNOUNCED"
    UNKNOWN = "UNKNOWN"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    CLAIMED = "CLAIMED"


class CostCategory(str, Enum):
    RAW_MATERIAL = "RAW_MATERIAL"
    FABRICATION = "FABRICATION"
    ASSEMBLY = "ASSEMBLY"
    TOOLING = "TOOLING"
    TEST_INSPECTION = "TEST_INSPECTION"
    OVERHEAD_LOGISTICS = "OVERHEAD_LOGISTICS"
    PACKAGING = "PACKAGING"
    UNKNOWN = "UNKNOWN"


class RiskSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskType(str, Enum):
    SINGLE_SOURCE = "SINGLE_SOURCE"
    OBSOLESCENCE = "OBSOLESCENCE"
    LONG_LEAD_TIME = "LONG_LEAD_TIME"
    HIGH_MOQ = "HIGH_MOQ"
    GEOPOLITICAL = "GEOPOLITICAL"
    FINANCIAL = "FINANCIAL"


class MakeBuyRecommendation(str, Enum):
    MAKE = "MAKE"
    BUY = "BUY"
    HYBRID = "HYBRID"
    DATA_REQUIRED = "DATA_REQUIRED"


class VolumeTier(BaseModel):
    min_quantity: int
    unit_cost: float


class CostBreakdown(BaseModel):
    raw_material: Optional[float] = None
    fabrication: Optional[float] = None
    assembly: Optional[float] = None
    tooling_nre: Optional[float] = None
    testing_inspection: Optional[float] = None
    overhead_logistics: Optional[float] = None
    packaging: Optional[float] = None


class PartCost(BaseModel):
    part_id: str
    part_name: str
    quantity_per_assembly: float = 1.0
    unit_cost: Optional[float] = None
    price_status: str = "KNOWN"  # "KNOWN" or "PRICE_UNKNOWN"
    currency: str = "USD"
    breakdown: Optional[CostBreakdown] = None
    quotation_source: str = "UNKNOWN"
    moq: Optional[int] = None
    lead_time_weeks: Optional[float] = None
    volume_tiers: List[VolumeTier] = Field(default_factory=list)
    lifecycle_status: LifecycleStatus = LifecycleStatus.ACTIVE
    is_single_source: bool = False
    supplier_country: Optional[str] = None
    primary_supplier: Optional[str] = None
    notes: Optional[str] = None


class CostDriver(BaseModel):
    driver_id: str
    name: str
    category: CostCategory = CostCategory.UNKNOWN
    impact_percentage: float = 0.0
    cost_per_unit: float = 0.0
    currency: str = "USD"
    description: str = ""
    mitigation_options: List[str] = Field(default_factory=list)


class BOMCostRollup(BaseModel):
    bom_id: str
    project_id: str
    target_volume: int = 1000
    currency: str = "USD"
    total_unit_cost: Optional[float] = None
    total_extended_cost: Optional[float] = None
    total_tooling_nre: float = 0.0
    is_cost_complete: bool = True
    unpriced_parts_count: int = 0
    unpriced_part_ids: List[str] = Field(default_factory=list)
    parts_cost_breakdown: List[PartCost] = Field(default_factory=list)
    category_breakdown: Dict[str, float] = Field(default_factory=dict)
    confidence_interval: Dict[str, float] = Field(default_factory=dict)
    top_cost_drivers: List[CostDriver] = Field(default_factory=list)


class SupplierCandidate(BaseModel):
    supplier_id: str
    name: str
    country: str
    certifications: List[str] = Field(default_factory=list)
    lead_time_weeks: Optional[float] = None
    moq: Optional[int] = None
    unit_price: Optional[float] = None
    currency: str = "USD"
    verification_status: VerificationStatus = VerificationStatus.CLAIMED
    reliability_score: float = 0.85
    notes: Optional[str] = None


class SupplierComparison(BaseModel):
    part_id: str
    candidates: List[SupplierCandidate] = Field(default_factory=list)
    recommended_supplier_id: Optional[str] = None
    recommendation_rationale: str = ""


class SupplyRisk(BaseModel):
    risk_id: str
    part_id: str
    part_name: str
    risk_type: RiskType
    severity: RiskSeverity
    description: str
    lead_time_weeks: Optional[float] = None
    moq: Optional[int] = None
    lifecycle_status: Optional[LifecycleStatus] = None
    supplier_country: Optional[str] = None
    mitigation_strategy: str = ""


class MakeVsBuyAnalysis(BaseModel):
    analysis_id: str
    part_id: str
    part_name: str
    make_unit_cost: float
    make_tooling_nre: float
    buy_unit_cost: float
    buy_tooling_nre: float = 0.0
    breakeven_volume: Optional[float] = None
    target_volume: int = 1000
    recommendation: MakeBuyRecommendation = MakeBuyRecommendation.DATA_REQUIRED
    rationale: str = ""


class VolumeCostPoint(BaseModel):
    quantity: int
    unit_cost: float
    extended_cost: float


class VolumeCostCurve(BaseModel):
    part_or_bom_id: str
    currency: str = "USD"
    curve_points: List[VolumeCostPoint] = Field(default_factory=list)


class ChangeCostImpact(BaseModel):
    change_id: str
    project_id: str
    title: str
    recurring_unit_delta: float = 0.0
    tooling_nre_delta: float = 0.0
    scrap_or_rework_cost: float = 0.0
    annualized_volume: int = 1000
    annual_cost_impact: float = 0.0
    recommendation: str = "APPROVE"
    rationale: str = ""


class CostDashboardData(BaseModel):
    project_id: str
    total_bom_cost: Optional[float] = None
    currency: str = "USD"
    target_volume: int = 1000
    unpriced_parts_count: int = 0
    total_risks_count: int = 0
    single_source_count: int = 0
    obsolete_or_nrnd_count: int = 0
    top_drivers: List[CostDriver] = Field(default_factory=list)
    high_risks: List[SupplyRisk] = Field(default_factory=list)
class CostSupplyChainInput(BaseModel):
    project_id: str
    operation: str = "full_analysis"  # "rollup", "drivers", "suppliers", "risks", "make_buy", "change_impact", "dashboard", "full_analysis"
    team_id: Optional[str] = None
    user_id: Optional[str] = None
    target_volume: int = 1000
    currency: str = "USD"
    parts: List[PartCost] = Field(default_factory=list)
    dfm_findings: List[Dict[str, Any]] = Field(default_factory=list)
    dfa_metrics: Dict[str, Any] = Field(default_factory=dict)
    supplier_candidates: Dict[str, List[SupplierCandidate]] = Field(default_factory=dict)
    make_buy_params: Optional[Dict[str, Any]] = None
    change_params: Optional[Dict[str, Any]] = None
    payload: Optional[Dict[str, Any]] = None


class CostSupplyChainOutput(BaseModel):
    agent_id: str = "Agent #25"
    agent_name: str = "CostSupplyChainAgent"
    fabric_id: str = "agent.25"
    status: str = "success"  # "success", "error", "access_denied"
    project_id: str
    operation: str
    rollup: Optional[BOMCostRollup] = None
    drivers: List[CostDriver] = Field(default_factory=list)
    supplier_comparisons: List[SupplierComparison] = Field(default_factory=list)
    risks: List[SupplyRisk] = Field(default_factory=list)
    make_buy: Optional[MakeVsBuyAnalysis] = None
    volume_curve: Optional[VolumeCostCurve] = None
    change_impact: Optional[ChangeCostImpact] = None
    dashboard: Optional[CostDashboardData] = None
    report_markdown: Optional[str] = None
    execution_duration_seconds: float = 0.0
    error_message: Optional[str] = None
