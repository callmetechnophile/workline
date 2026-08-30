"""
Data contracts and Pydantic schemas for BOMOptimizationAgent (Agent #8).
Defines supplier offers, Blue Dart shipping options, orders, landed cost structures,
procurement strategies, traceability, and 7-file export contracts.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


StockStatusLiteral = Literal["in_stock", "limited", "out_of_stock", "unknown"]
ShippingModeLiteral = Literal["express", "priority", "air", "surface", "economy", "standard", "local"]


class RequestContext(BaseModel):
    """Execution and governance context for ArmorIQ / A2A integration (Section 40)."""

    user_id: Optional[str] = None
    project_id: Optional[str] = None
    agent_id: str = "BOMOptimizationAgent"
    parent_agent_id: Optional[str] = None
    authorization_context: Optional[Dict[str, Any]] = None
    execution_id: Optional[str] = None
    tool_scope: List[str] = Field(default_factory=list)


class Location(BaseModel):
    """Geographic location definition for supplier origins and project destinations (Section 15 & 16)."""

    city: str = "Bengaluru"
    state: str = "Karnataka"
    country: str = "India"
    postal_code: Optional[str] = "560001"


class ProjectConstraints(BaseModel):
    """Procurement constraints for budget and delivery timeframe."""

    maximum_budget: Optional[float] = None
    maximum_delivery_days: Optional[int] = None


class ProjectMeta(BaseModel):
    """Engineering project metadata for procurement optimization."""

    project_id: Optional[str] = None
    title: str = Field(..., description="Project title or concept name.")
    destination: Location = Field(default_factory=Location)
    constraints: ProjectConstraints = Field(default_factory=ProjectConstraints)


class SupplierOffer(BaseModel):
    """Normalized component pricing and availability from a distributor (Section 5)."""

    supplier_id: str
    supplier_name: str
    location: Location = Field(default_factory=Location)
    bom_item_id: str
    part_number: str
    manufacturer: str
    unit_price: Optional[float] = None
    currency: str = "INR"
    available_quantity: Optional[int] = None
    minimum_order_quantity: Optional[int] = 1
    price_breaks: Dict[int, float] = Field(default_factory=dict)
    lead_time_days: Optional[int] = None
    stock_status: StockStatusLiteral = "in_stock"
    source_url: Optional[str] = None
    data_timestamp: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ShippingOption(BaseModel):
    """Carrier logistics and transit cost quote (Section 18)."""

    shipping_id: str
    supplier_id: str
    origin: str
    destination: str
    distance_km: Optional[float] = None
    carrier: str = "Blue Dart"
    service: str = "Express"
    shipping_mode: ShippingModeLiteral = "express"
    shipping_cost: Optional[float] = None
    currency: str = "INR"
    estimated_delivery_days: Optional[int] = None
    source: str = "configured_estimate"  # "configured_estimate" | "live_quote" | "user_supplied"
    data_timestamp: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class OrderItem(BaseModel):
    """Individual line item allocation within a supplier order bundle (Section 20)."""

    bom_item_id: str
    part_number: str
    component_name: str
    required_quantity: int
    purchased_quantity: int
    surplus_quantity: int = 0
    unit_price: float
    product_cost: float
    shipping_cost_allocated: Optional[float] = None
    known_landed_cost: float
    moq_reason: Optional[str] = None


class SupplierOrder(BaseModel):
    """Consolidated purchase order bundle assigned to a single distributor (Section 20)."""

    order_id: str
    supplier_id: str
    supplier_name: str
    supplier_location: Location = Field(default_factory=Location)
    items: List[OrderItem] = Field(default_factory=list)
    product_subtotal: float = 0.0
    shipping_cost: float = 0.0
    additional_cost: float = 0.0
    known_landed_cost: float = 0.0
    unknown_costs: List[str] = Field(default_factory=list)
    delivery_estimate_days: Optional[int] = None
    shipping_mode: str = "surface"
    carrier: str = "Blue Dart"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class OptimizedBOMItem(BaseModel):
    """Procurement-optimized BOM component record (Section 25)."""

    bom_item_id: str
    selected_supplier: str
    selected_part_number: str
    manufacturer: str
    category: str
    subsystem_id: str
    required_quantity: int
    purchased_quantity: int
    unit_price: Optional[float] = None
    product_cost: Optional[float] = None
    shipping_cost_allocated: Optional[float] = None
    known_landed_cost: Optional[float] = None
    stock_status: StockStatusLiteral = "in_stock"
    lead_time_days: Optional[int] = None
    alternative_options: List[Dict[str, Any]] = Field(default_factory=list)
    selection_reason: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ProcurementStrategy(BaseModel):
    """Comprehensive procurement configuration option (Sections 23 & 24)."""

    strategy_id: str = "STRAT-001"
    name: str = "Lowest Landed Cost"
    objective: str = "minimize_landed_cost"
    orders: List[SupplierOrder] = Field(default_factory=list)
    total_product_cost: float = 0.0
    total_shipping_cost: float = 0.0
    total_known_landed_cost: float = 0.0
    unknown_costs: List[str] = Field(default_factory=list)
    supplier_count: int = 0
    estimated_delivery_days: Optional[int] = None
    constraints_satisfied: bool = True
    warnings: List[str] = Field(default_factory=list)


class CostSummary(BaseModel):
    """Aggregate financial and logistics metrics across the procurement plan (Section 43)."""

    total_product_cost: float = 0.0
    total_shipping_cost: float = 0.0
    total_additional_cost: float = 0.0
    total_known_landed_cost: float = 0.0
    unknown_costs: List[str] = Field(default_factory=list)
    supplier_count: int = 0
    order_count: int = 0
    estimated_delivery_days: Optional[int] = None


class ProcurementTraceabilityItem(BaseModel):
    """Full traceability chain from original BOM item to supplier offer and landed cost (Section 44)."""

    traceability_id: str
    bom_item_id: str
    component_requirement_ids: List[str] = Field(default_factory=list)
    candidate_part_numbers: List[str] = Field(default_factory=list)
    supplier_offer_ids: List[str] = Field(default_factory=list)
    shipping_ids: List[str] = Field(default_factory=list)
    selected_offer_id: Optional[str] = None
    decision_reason: str


class StructuredError(BaseModel):
    """Machine-readable error model."""

    code: str
    message: str
    retryable: bool = False
    details: Optional[Dict[str, Any]] = None


class BOMOptimizationAgentInput(BaseModel):
    """Structured input contract for BOMOptimizationAgent (Section 3)."""

    project: ProjectMeta
    bom: Dict[str, Any] = Field(
        default_factory=dict,
        description="Engineering BOM from Agent #7 (ComponentPlanningAgent).",
    )
    component_alternatives: List[Dict[str, Any]] = Field(default_factory=list)
    supplier_data: List[Dict[str, Any]] = Field(default_factory=list)
    shipping_data: List[Dict[str, Any]] = Field(default_factory=list)
    output_dir: Optional[str] = Field(
        default=None,
        description="Optional directory to export the 7 procurement artifacts.",
    )
    execution_context: Optional[RequestContext] = None


class BOMOptimizationAgentOutput(BaseModel):
    """Structured output contract for BOMOptimizationAgent (Section 42)."""

    status: Literal["success", "error"] = "success"
    project_id: str = ""
    bom_id: str = ""
    optimization_id: str = "OPT-001"
    destination: Location = Field(default_factory=Location)
    selected_strategy: ProcurementStrategy = Field(default_factory=ProcurementStrategy)
    strategies: List[ProcurementStrategy] = Field(default_factory=list)
    optimized_items: List[OptimizedBOMItem] = Field(default_factory=list)
    orders: List[SupplierOrder] = Field(default_factory=list)
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)
    compatibility_warnings: List[str] = Field(default_factory=list)
    procurement_warnings: List[str] = Field(default_factory=list)
    cost_summary: CostSummary = Field(default_factory=CostSummary)
    supplier_summary: List[Dict[str, Any]] = Field(default_factory=list)
    delivery_summary: Dict[str, Any] = Field(default_factory=dict)
    traceability: List[ProcurementTraceabilityItem] = Field(default_factory=list)
    assumptions: List[Dict[str, Any]] = Field(default_factory=list)
    unknowns: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(default=0.95, ge=0.0, le=1.0)
    structured_report_markdown: str = ""
    warnings: List[str] = Field(default_factory=list)
    errors: List[StructuredError] = Field(default_factory=list)
