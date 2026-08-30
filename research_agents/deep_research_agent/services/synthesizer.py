"""
Core reasoning and synthesis orchestrator for DeepResearchAgent.
Prompts Amazon Bedrock to reason across gathered evidence and generates a typed synthesis structure.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from research_agents.deep_research_agent.providers.base import ReasoningProvider
from research_agents.deep_research_agent.schemas import (
    ComponentTradeStudy,
    ContradictionReport,
    CrossSourceComparison,
    DeepResearchAgentInput,
    EngineeringImplication,
    EngineeringRecommendation,
    EvidenceItem,
    ProjectMeta,
    SynthesizedClaim,
)


class SynthesisSchema(BaseModel):
    """Internal Pydantic schema requested from Bedrock."""

    executive_summary: str
    architecture_analysis: str
    component_trade_studies: List[ComponentTradeStudy] = Field(default_factory=list)
    extracted_claims: List[SynthesizedClaim] = Field(default_factory=list)
    cross_source_comparisons: List[CrossSourceComparison] = Field(default_factory=list)
    contradictions: List[ContradictionReport] = Field(default_factory=list)
    engineering_implications: List[EngineeringImplication] = Field(default_factory=list)
    recommendations: List[EngineeringRecommendation] = Field(default_factory=list)
    research_gaps: List[str] = Field(default_factory=list)


class DeepResearchSynthesizer:
    """Orchestrates evidence reasoning prompts and parses structured Bedrock output."""

    SYSTEM_PROMPT = (
        "You are an expert Principal Systems & Hardware Engineer in the WorkflowGuide AI platform. "
        "Your task is to analyze all provided research evidence (academic papers, datasheets, web evidence) "
        "and produce an objective, structured engineering synthesis for the project.\n\n"
        "STRICT OPERATIONAL RULES:\n"
        "1. Strictly separate EXPLICIT SOURCE FACTS from MODEL INFERENCE and RECOMMENDATIONS.\n"
        "2. Never fabricate specifications or cite non-existent evidence IDs.\n"
        "3. Explicit source claims MUST cite their exact backing evidence ID (e.g. ['ev_001']).\n"
        "4. Highlight trade-offs, power limits, thermal constraints, and contradictions.\n"
        "5. Output valid structured JSON conforming to the requested schema."
    )

    def __init__(self, provider: ReasoningProvider):
        self.provider = provider

    def build_prompt(
        self,
        project: ProjectMeta,
        evidence: List[EvidenceItem],
    ) -> str:
        """Constructs rich evidence tables for the reasoning prompt."""
        ev_summary_lines: List[str] = []
        for e in evidence[:40]:  # Limit context budget
            loc_str = f" [p.{e.page}]" if e.page else ""
            ev_summary_lines.append(
                f"- ID: {e.evidence_id} | Type: {e.source_type} | Source: {e.title or e.source_id}{loc_str}\n"
                f"  Content: {e.text[:280]}"
            )

        prompt = (
            f"PROJECT CONTEXT:\n"
            f"- Title: {project.title}\n"
            f"- Domain: {project.engineering_domain or 'General Engineering'}\n"
            f"- Description: {project.description or 'N/A'}\n"
            f"- Objectives: {', '.join(project.objectives) if project.objectives else 'N/A'}\n"
            f"- Components: {', '.join(project.components) if project.components else 'N/A'}\n"
            f"- Technologies: {', '.join(project.technologies) if project.technologies else 'N/A'}\n"
            f"- Constraints: {', '.join(project.constraints) if project.constraints else 'N/A'}\n\n"
            f"STRUCTURED RESEARCH EVIDENCE ({len(evidence)} items):\n"
            f"{''.join(ev_summary_lines)}\n\n"
            f"INSTRUCTIONS:\n"
            f"1. Synthesize an Executive Summary and Architecture Analysis.\n"
            f"2. Formulate Component Trade Studies comparing evaluated hardware/software options.\n"
            f"3. Extract and partition claims into explicit_source_claim (backed by evidence IDs), model_inference, and engineering_recommendation.\n"
            f"4. Identify Cross-Source Comparisons and any Contradiction Reports.\n"
            f"5. Document Engineering Implications (power, compute, latency, thermal, cost).\n"
            f"6. Provide prioritized Actionable Recommendations and note Research Gaps."
        )
        return prompt

    async def synthesize(
        self,
        project: ProjectMeta,
        evidence: List[EvidenceItem],
    ) -> SynthesisSchema:
        """Executes structured reasoning with Bedrock."""
        prompt = self.build_prompt(project, evidence)
        return await self.provider.generate_structured(
            prompt=prompt,
            schema=SynthesisSchema,
            system_prompt=self.SYSTEM_PROMPT,
        )
