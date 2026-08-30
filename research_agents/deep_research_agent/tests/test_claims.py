"""
Unit tests for claim separation, classification, and provenance validation.
"""

from research_agents.deep_research_agent.schemas import (
    EvidenceItem,
    SynthesizedClaim,
)
from research_agents.deep_research_agent.services.claim_extractor import ClaimExtractor


def test_claim_classification_types():
    extractor = ClaimExtractor()

    # Recommendation
    rec_type = extractor.classify_claim_type(
        "We recommend deploying Jetson Orin Nano for edge computing.",
        source_evidence_ids=["ev_001"],
    )
    assert rec_type == "engineering_recommendation"

    # Model Inference
    inf_type = extractor.classify_claim_type(
        "This architecture is likely suitable for low-power edge flight.",
        source_evidence_ids=["ev_001"],
    )
    assert inf_type == "model_inference"

    # Derived Claim (multiple sources)
    der_type = extractor.classify_claim_type(
        "The system achieves real-time inference within the 15 W power envelope.",
        source_evidence_ids=["ev_001", "ev_002"],
    )
    assert der_type == "derived_claim"

    # Explicit Source Claim (single source)
    exp_type = extractor.classify_claim_type(
        "Jetson Orin Nano delivers 40 TOPS AI compute.",
        source_evidence_ids=["ev_001"],
    )
    assert exp_type == "explicit_source_claim"


def test_claim_validation_reclassifies_unsupported_explicit_claim():
    extractor = ClaimExtractor()
    valid_ev = [EvidenceItem(evidence_id="ev_valid_01", source_id="src_1", text="Valid evidence text")]

    claims = [
        SynthesizedClaim(
            claim="Claim citing non-existent evidence",
            claim_type="explicit_source_claim",
            source_evidence_ids=["ev_ghost_999"],
        )
    ]

    validated = extractor.validate_claims(claims, valid_ev)
    assert len(validated) == 1
    assert validated[0].claim_type == "model_inference"
    assert validated[0].source_evidence_ids == []
