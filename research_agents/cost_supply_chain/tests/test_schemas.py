"""Tests for Agent #25 Pydantic schemas."""
import pytest
from research_agents.cost_supply_chain.schemas import (
    BOMCostRollup,
    CostCategory,
    CostDriver,
    LifecycleStatus,
    MakeBuyRecommendation,
    MakeVsBuyAnalysis,
    PartCost,
    RiskSeverity,
    RiskType,
    SupplierCandidate,
    SupplyRisk,
    VerificationStatus,
    VolumeTier,
)


def test_part_cost_defaults():
    p = PartCost(part_id="P1", part_name="Test Part")
    assert p.part_id == "P1"
    assert p.quantity_per_assembly == 1.0
    assert p.price_status == "KNOWN"
    assert p.lifecycle_status == LifecycleStatus.ACTIVE
    assert p.is_single_source is False


def test_supplier_candidate():
    s = SupplierCandidate(
        supplier_id="SUP-1",
        name="Apex Precision",
        country="US",
        unit_price=12.50,
        verification_status=VerificationStatus.VERIFIED,
    )
    assert s.supplier_id == "SUP-1"
    assert s.unit_price == 12.50
    assert s.verification_status == VerificationStatus.VERIFIED


def test_make_vs_buy_analysis():
    mba = MakeVsBuyAnalysis(
        analysis_id="MB-1",
        part_id="P1",
        part_name="Bracket",
        make_unit_cost=10.0,
        make_tooling_nre=5000.0,
        buy_unit_cost=15.0,
        breakeven_volume=1000.0,
        recommendation=MakeBuyRecommendation.MAKE,
    )
    assert mba.breakeven_volume == 1000.0
    assert mba.recommendation == MakeBuyRecommendation.MAKE
