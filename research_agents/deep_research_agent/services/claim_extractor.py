"""
Claim classification and verification service for DeepResearchAgent.
Enforces strict separation between explicit source claims, derived claims, model inference, and recommendations.
"""

from typing import List
from research_agents.deep_research_agent.schemas import (
    ClaimTypeLiteral,
    EvidenceItem,
    SynthesizedClaim,
)


class ClaimExtractor:
    """Classifies and validates claims against backing evidence IDs."""

    RECOMMENDATION_KEYWORDS = ["recommend", "should use", "select", "deploy", "choose", "adopt", "opt for"]
    INFERENCE_KEYWORDS = ["may be", "likely", "suggests", "indicates", "implies", "feasible", "suitable for"]

    def classify_claim_type(
        self,
        claim_text: str,
        source_evidence_ids: List[str],
    ) -> ClaimTypeLiteral:
        """
        Determines the formal claim type based on linguistic cues and evidence provenance.
        """
        text_lower = claim_text.lower()

        # 1. Recommendation
        if any(kw in text_lower for kw in self.RECOMMENDATION_KEYWORDS):
            return "engineering_recommendation"

        # 2. Model Inference / Hypothesis
        if any(kw in text_lower for kw in self.INFERENCE_KEYWORDS):
            return "model_inference"

        # 3. Derived Claim (combines multiple evidence sources)
        if len(source_evidence_ids) > 1:
            return "derived_claim"

        # 4. Explicit Source Claim (single backing evidence)
        if len(source_evidence_ids) == 1:
            return "explicit_source_claim"

        return "unknown"

    def validate_claims(
        self,
        claims: List[SynthesizedClaim],
        valid_evidence: List[EvidenceItem],
    ) -> List[SynthesizedClaim]:
        """
        Validates claim evidence references against available evidence items.
        """
        valid_ev_ids = {e.evidence_id for e in valid_evidence}
        validated: List[SynthesizedClaim] = []

        for c in claims:
            # Filter to only existing evidence IDs
            existing_ids = [eid for eid in c.source_evidence_ids if eid in valid_ev_ids]

            # Re-verify claim type
            verified_type = c.claim_type
            if verified_type == "explicit_source_claim" and not existing_ids:
                verified_type = "model_inference"  # Cannot be explicit source claim without valid evidence

            validated.append(
                SynthesizedClaim(
                    claim=c.claim,
                    claim_type=verified_type,
                    source_evidence_ids=existing_ids,
                    confidence=c.confidence,
                    rationale=c.rationale,
                )
            )

        return validated
