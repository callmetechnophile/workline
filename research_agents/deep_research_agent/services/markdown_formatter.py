"""
Structured Markdown report formatter for DeepResearchAgent.
Produces an executive engineering research synthesis report with tables, trade studies, and provenance footnotes.
"""

from typing import List
from research_agents.deep_research_agent.schemas import (
    ComponentTradeStudy,
    ContradictionReport,
    CrossSourceComparison,
    EngineeringImplication,
    EngineeringRecommendation,
    EvidenceItem,
    ProjectMeta,
    SynthesizedClaim,
)


class MarkdownReportFormatter:
    """Formats structured research output into an authoritative engineering synthesis report."""

    def format_report(
        self,
        project: ProjectMeta,
        executive_summary: str,
        architecture_analysis: str,
        trade_studies: List[ComponentTradeStudy],
        claims: List[SynthesizedClaim],
        comparisons: List[CrossSourceComparison],
        contradictions: List[ContradictionReport],
        implications: List[EngineeringImplication],
        recommendations: List[EngineeringRecommendation],
        research_gaps: List[str],
        evidence_used: List[EvidenceItem],
    ) -> str:
        """Assembles Markdown document sections."""
        lines: List[str] = []

        # 1. Title & Metadata
        lines.append(f"# Engineering Research Synthesis: {project.title}\n")
        if project.engineering_domain:
            lines.append(f"**Domain:** {project.engineering_domain}  ")
        if project.objectives:
            lines.append(f"**Objectives:** {', '.join(project.objectives)}  ")
        if project.constraints:
            lines.append(f"**Key Constraints:** {', '.join(project.constraints)}  ")
        lines.append("")

        # 2. Executive Summary
        lines.append("## 1. Executive Summary\n")
        lines.append(f"{executive_summary.strip()}\n")

        # 3. Architecture Analysis
        lines.append("## 2. Architecture & Subsystem Analysis\n")
        lines.append(f"{architecture_analysis.strip()}\n")

        # 4. Component Trade Studies
        if trade_studies:
            lines.append("## 3. Component Trade Studies\n")
            for study in trade_studies:
                lines.append(f"### Trade Study: {study.component_type}\n")
                lines.append(f"**Recommended Choice:** `{study.recommended_option}`  ")
                lines.append(f"**Rationale:** {study.recommendation_reason}\n")

                if study.tradeoff_matrix:
                    first_val = next(iter(study.tradeoff_matrix.values()))
                    headers = ["Candidate"] + list(first_val.keys())
                    lines.append("| " + " | ".join(headers) + " |")
                    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                    for cand, metrics in study.tradeoff_matrix.items():
                        row = [cand] + [str(v) for v in metrics.values()]
                        lines.append("| " + " | ".join(row) + " |")
                    lines.append("")

        # 5. Verified Claims & Evidence Separation
        if claims:
            lines.append("## 4. Synthesized Claims & Evidence Verification\n")
            lines.append("> [!NOTE]")
            lines.append("> Claims are strictly partitioned into verified Source Facts, Model Inferences, and Engineering Recommendations.\n")

            fact_claims = [c for c in claims if c.claim_type == "explicit_source_claim"]
            inf_claims = [c for c in claims if c.claim_type in ("model_inference", "derived_claim")]
            rec_claims = [c for c in claims if c.claim_type == "engineering_recommendation"]

            if fact_claims:
                lines.append("### 4.1 Explicit Source Facts")
                for c in fact_claims:
                    sources_str = f" `[{', '.join(c.source_evidence_ids)}]`" if c.source_evidence_ids else ""
                    lines.append(f"- **Fact:** {c.claim}{sources_str}")
                lines.append("")

            if inf_claims:
                lines.append("### 4.2 Model Inferences & Analytical Deductions")
                for c in inf_claims:
                    rat = f" *(Rationale: {c.rationale})*" if c.rationale else ""
                    lines.append(f"- **Inference:** {c.claim}{rat}")
                lines.append("")

            if rec_claims:
                lines.append("### 4.3 Engineering Recommendations")
                for c in rec_claims:
                    lines.append(f"- **Recommendation:** {c.claim}")
                lines.append("")

        # 6. Cross-Source Comparisons & Contradictions
        if comparisons or contradictions:
            lines.append("## 5. Cross-Source Comparisons & Contradiction Analysis\n")
            for comp in comparisons:
                status = "[Agreed]" if comp.sources_agree else "[Divergent]"
                lines.append(f"- **{status} {comp.topic}:** {comp.summary}")
            lines.append("")

            if contradictions:
                lines.append("### Contradiction Resolutions\n")
                lines.append("| Topic | Claim A | Claim B | Resolution |")
                lines.append("|---|---|---|---|")
                for cont in contradictions:
                    lines.append(f"| {cont.topic} | {cont.source_a_claim} | {cont.source_b_claim} | {cont.resolution} |")
                lines.append("")

        # 7. Engineering Implications
        if implications:
            lines.append("## 6. Engineering Implications\n")
            for imp in implications:
                lines.append(f"- **{imp.category.upper()}:** {imp.finding} — *Impact:* {imp.impact_on_project}")
            lines.append("")

        # 8. Actionable Recommendations
        if recommendations:
            lines.append("## 7. Actionable Design Guidance\n")
            for idx, rec in enumerate(recommendations, 1):
                prio_tag = f"[{rec.priority.upper()} PRIORITY]"
                lines.append(f"{idx}. **{prio_tag} {rec.recommendation}** (`{rec.category}`)")
                lines.append(f"   - *Justification:* {rec.justification}")
            lines.append("")

        # 9. Research Gaps
        if research_gaps:
            lines.append("## 8. Identified Research Gaps\n")
            for gap in research_gaps:
                lines.append(f"- {gap}")
            lines.append("")

        # 10. Evidence Index
        if evidence_used:
            lines.append("## 9. Evidence & Provenance Index\n")
            lines.append("| Evidence ID | Type | Title / Source | Page/Sec | URL |")
            lines.append("|---|---|---|---|---|")
            for ev in evidence_used[:15]:
                title = (ev.title or ev.source_id)[:30]
                loc = f"p.{ev.page}" if ev.page else (ev.section or "-")
                url_str = f"[Link]({ev.source_url})" if ev.source_url else "-"
                lines.append(f"| `{ev.evidence_id}` | {ev.source_type} | {title} | {loc} | {url_str} |")
            lines.append("")

        return "\n".join(lines).strip()
