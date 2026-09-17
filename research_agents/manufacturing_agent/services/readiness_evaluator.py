"""
Deterministic Manufacturing Readiness Gate Evaluator (Section 41).
"""

from typing import List, Optional
from research_agents.manufacturing_agent.schemas import (
    DFAFinding,
    DFAModel,
    DFMFinding,
    InspectionItem,
    ManufacturingReadiness,
    ReadinessVerdictLiteral,
    ToleranceItem,
)


class ReadinessEvaluator:
    """Evaluates multi-stage manufacturing readiness gates without arbitrary LLM overrides."""

    def evaluate_readiness(
        self,
        project_id: str,
        dfm_findings: List[DFMFinding],
        dfa_models: List[DFAModel],
        tolerances: List[ToleranceItem],
        inspections: List[InspectionItem],
        target_volume: str = "PROTOTYPE",
    ) -> ManufacturingReadiness:
        blockers: List[str] = []
        unresolved_tols: List[str] = []
        unverified_insps: List[str] = []

        # 1. DFM Blockers
        for f in dfm_findings:
            if f.severity == "BLOCKER":
                blockers.append(f"DFM BLOCKER ({f.component_id}): {f.description}")

        # 2. DFA Blockers
        for m in dfa_models:
            for f in m.findings:
                if f.severity == "BLOCKER":
                    blockers.append(f"DFA BLOCKER ({m.assembly_id}): {f.description}")

        # 3. Tolerance Concerns
        for t in tolerances:
            if t.classification == "UNRESOLVED":
                unresolved_tols.append(f"{t.component_id} / {t.feature_name}: Ambiguous or unresolved tolerance")

        # 4. Inspection Criteria
        for i in inspections:
            if i.verification_status != "VERIFIED":
                unverified_insps.append(f"{i.component_id}: {i.feature_or_characteristic} ({i.verification_status})")

        # Deterministic scoring
        dfm_penalties = sum(25.0 if f.severity == "BLOCKER" else 15.0 if f.severity == "CRITICAL" else 5.0 if f.severity == "MAJOR" else 1.0 for f in dfm_findings)
        dfm_score = max(0.0, 100.0 - dfm_penalties)

        dfa_penalties = 0.0
        for m in dfa_models:
            dfa_penalties += sum(25.0 if f.severity == "BLOCKER" else 15.0 if f.severity == "CRITICAL" else 5.0 if f.severity == "MAJOR" else 1.0 for f in m.findings)
        dfa_score = max(0.0, 100.0 - dfa_penalties)

        composite = round((dfm_score + dfa_score) / 2.0, 1)

        # Verdict calculation
        verdict: ReadinessVerdictLiteral = "PROTOTYPE_READY"
        if any("DFM BLOCKER" in b for b in blockers):
            verdict = "DFM_BLOCKED"
        elif any("DFA BLOCKER" in b for b in blockers):
            verdict = "DFA_BLOCKED"
        elif unresolved_tols:
            verdict = "REQUIRES_VALIDATION"
        elif composite < 60.0:
            verdict = "CONDITIONAL"
        elif target_volume in ("HIGH_VOLUME", "MASS_PRODUCTION"):
            if composite >= 85.0 and not blockers and not unresolved_tols:
                verdict = "PRODUCTION_READY"
            else:
                verdict = "PILOT_READY"
        else:
            verdict = "PROTOTYPE_READY"

        summary = (
            f"Manufacturing Readiness Verdict: {verdict}. DFM Score: {dfm_score:.1f}, "
            f"DFA Score: {dfa_score:.1f}. Active Blockers: {len(blockers)}."
        )

        return ManufacturingReadiness(
            project_id=project_id,
            verdict=verdict,
            dfm_score=round(dfm_score, 1),
            dfa_score=round(dfa_score, 1),
            composite_manufacturability_score=composite,
            active_blockers=blockers,
            unresolved_tolerances=unresolved_tols,
            unverified_inspection_criteria=unverified_insps,
            confidence=0.90,
            summary=summary,
        )
