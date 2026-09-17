"""Tests for supplier evaluation and scoring engine."""
from research_agents.cost_supply_chain.schemas import SupplierCandidate, VerificationStatus
from research_agents.cost_supply_chain.services.supplier_engine import SupplierEngine


def test_evaluate_suppliers_ranking():
    engine = SupplierEngine()
    cands = [
        SupplierCandidate(
            supplier_id="SUP-A",
            name="Fast Supplier",
            country="US",
            unit_price=12.0,
            lead_time_weeks=4.0,
            moq=100,
            verification_status=VerificationStatus.VERIFIED,
            certifications=["ISO 9001"],
        ),
        SupplierCandidate(
            supplier_id="SUP-B",
            name="Slow Cheap Supplier",
            country="CN",
            unit_price=8.0,
            lead_time_weeks=20.0,
            moq=5000,
            verification_status=VerificationStatus.CLAIMED,
        ),
    ]
    comp = engine.evaluate_suppliers("PART-1", cands, target_volume=1000)
    assert comp.recommended_supplier_id == "SUP-A"
    assert "Recommended supplier Fast Supplier" in comp.recommendation_rationale


def test_evaluate_suppliers_empty():
    engine = SupplierEngine()
    comp = engine.evaluate_suppliers("PART-1", [])
    assert comp.recommended_supplier_id is None
