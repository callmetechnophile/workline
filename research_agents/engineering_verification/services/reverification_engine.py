"""
Change-driven re-verification and regression scoping engine (Sections 53–57).
"""

from typing import Dict, List, Tuple
from research_agents.engineering_verification.schemas import EvidenceObject, TestObject


class ReverificationEngine:
    """Calculates invalidation impacts and scopes required regression tests."""

    def process_change_impact(
        self,
        target_artifact: str,
        tests: List[TestObject],
        evidence_list: List[EvidenceObject],
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Returns:
            (invalidated_tests, invalidated_evidence, required_regression_tests)
        """
        invalidated_tests: List[str] = []
        invalidated_evidence: List[str] = []
        required_regression: List[str] = []

        for ev in evidence_list:
            if target_artifact.lower() in ev.artifact.lower() or target_artifact.lower() in ev.source.lower():
                invalidated_evidence.append(ev.evidence_id)

        for t in tests:
            has_matching_name = target_artifact.lower() in t.name.lower() or target_artifact.lower() in t.objective.lower()
            has_invalidated_ev = any(ev.source == f"test:{t.test_id}" and ev.evidence_id in invalidated_evidence for ev in evidence_list)
            if has_matching_name or has_invalidated_ev:
                invalidated_tests.append(t.test_id)
                required_regression.append(t.test_id)

        return list(set(invalidated_tests)), list(set(invalidated_evidence)), list(set(required_regression))
