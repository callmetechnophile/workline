"""
Agent #5: EngineeringSynthesisAgent implementation using Google ADK conventions.
Transforms research evidence and deep research findings into structured, evidence-backed engineering design decisions,
trade-offs, risk assessments, validation plans, and complete traceability.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional
import uuid
from loguru import logger

from research_agents.engineering_synthesis_agent.providers.base import (
    ProviderError,
    ReasoningProvider,
)
from research_agents.engineering_synthesis_agent.providers.bedrock import BedrockProvider
from research_agents.engineering_synthesis_agent.schemas import (
    AssumptionItem,
    DecisionTraceability,
    EngineeringDecision,
    EngineeringRisk,
    EngineeringSynthesisAgentInput,
    EngineeringSynthesisAgentOutput,
    EngineeringTradeoff,
    ExperimentPlan,
    ProjectMeta,
    RecommendationItem,
    RequirementAnalysis,
    StructuredError,
    TechnicalFinding,
    UnknownItem,
    ValidationRequirement,
)
from research_agents.engineering_synthesis_agent.services.decision_engine import DecisionEngine
from research_agents.engineering_synthesis_agent.services.file_exporter import EngineeringFileExporter
from research_agents.engineering_synthesis_agent.services.finding_extractor import FindingExtractor
from research_agents.engineering_synthesis_agent.services.report_generator import EngineeringReportGenerator
from research_agents.engineering_synthesis_agent.services.requirement_mapper import RequirementMapper
from research_agents.engineering_synthesis_agent.services.risk_analyzer import RiskAnalyzer
from research_agents.engineering_synthesis_agent.services.traceability_builder import TraceabilityBuilder
from research_agents.engineering_synthesis_agent.services.tradeoff_analyzer import TradeoffAnalyzer
from research_agents.engineering_synthesis_agent.services.validation_planner import ValidationPlanner


class EngineeringSynthesisAgent:
    """
    Google ADK-compliant Engineering Synthesis & Decision Agent.
    Transforms research evidence into traceable engineering decisions, recommendations,
    risk assessments, and validation requirements.
    """

    NAME = "EngineeringSynthesisAgent"
    DESCRIPTION = (
        "Transforms research evidence into traceable engineering decisions, recommendations, "
        "risk assessments, and validation requirements."
    )
    CAPABILITIES = [
        "engineering.analyze",
        "engineering.compare",
        "engineering.decide",
        "engineering.recommend",
        "engineering.validate",
    ]

    def __init__(
        self,
        reasoning_provider: Optional[ReasoningProvider] = None,
        requirement_mapper: Optional[RequirementMapper] = None,
        finding_extractor: Optional[FindingExtractor] = None,
        tradeoff_analyzer: Optional[TradeoffAnalyzer] = None,
        decision_engine: Optional[DecisionEngine] = None,
        risk_analyzer: Optional[RiskAnalyzer] = None,
        validation_planner: Optional[ValidationPlanner] = None,
        traceability_builder: Optional[TraceabilityBuilder] = None,
        report_generator: Optional[EngineeringReportGenerator] = None,
        file_exporter: Optional[EngineeringFileExporter] = None,
    ):
        self.provider = reasoning_provider or BedrockProvider()
        self.requirement_mapper = requirement_mapper or RequirementMapper()
        self.finding_extractor = finding_extractor or FindingExtractor()
        self.tradeoff_analyzer = tradeoff_analyzer or TradeoffAnalyzer()
        self.decision_engine = decision_engine or DecisionEngine()
        self.risk_analyzer = risk_analyzer or RiskAnalyzer()
        self.validation_planner = validation_planner or ValidationPlanner()
        self.traceability_builder = traceability_builder or TraceabilityBuilder()
        self.report_generator = report_generator or EngineeringReportGenerator()
        self.file_exporter = file_exporter or EngineeringFileExporter()

    async def run(
        self,
        input_data: EngineeringSynthesisAgentInput,
        execution_id: Optional[str] = None,
    ) -> EngineeringSynthesisAgentOutput:
        """
        Executes staged engineering synthesis and decision generation.
        """
        start_time = time.time()
        exec_id = (
            execution_id
            or (input_data.execution_context.execution_id if input_data.execution_context else None)
            or f"exec_{uuid.uuid4().hex[:8]}"
        )

        logger.info(
            f"[{exec_id}][{self.NAME}] Starting engineering synthesis for project='{input_data.project.title}'"
        )

        # 1. Combine upstream evidence items
        all_evidence: List[Dict[str, Any]] = (
            input_data.research_papers
            + input_data.web_sources
            + input_data.documents
            + input_data.chunks
            + input_data.facts
        )

        # 2. Extract Technical Findings (Section 5)
        findings = self.finding_extractor.extract_findings(
            deep_research_data=input_data.deep_research,
            raw_facts=input_data.facts,
            evidence_items=all_evidence,
        )

        # 3. Map Requirements to Evidence (Section 4 & 16)
        requirement_analysis = self.requirement_mapper.map_requirements(
            project=input_data.project,
            evidence_items=all_evidence,
            technical_finding_ids=[f.finding_id for f in findings],
        )

        # 4. Analyze Engineering Trade-offs (Section 7)
        tradeoffs = self.tradeoff_analyzer.analyze_tradeoffs(
            project=input_data.project,
            deep_research_data=input_data.deep_research,
            evidence_items=all_evidence,
        )

        # 5. Generate Decisions, Recommendations, Assumptions & Unknowns (Sections 8, 9, 11, 12)
        decisions, recommendations, assumptions, unknowns = (
            self.decision_engine.generate_decisions_and_recommendations(
                project=input_data.project,
                requirements=requirement_analysis,
                findings=findings,
                tradeoffs=tradeoffs,
            )
        )

        # 6. Qualitative Risk Analysis (Section 13)
        risks = self.risk_analyzer.analyze_risks(
            project=input_data.project,
            decisions=decisions,
        )

        # 7. Validation Planning & Experiment Design (Sections 14 & 15)
        validations, experiments = self.validation_planner.plan_validation(
            project=input_data.project,
            decisions=decisions,
        )

        # 8. Build Decision Traceability Lineage (Section 17)
        traceability = self.traceability_builder.build_traceability(
            requirements=requirement_analysis,
            findings=findings,
            tradeoffs=tradeoffs,
            decisions=decisions,
            validations=validations,
        )

        # Calculate overall confidence
        confidence_scores = [d.confidence for d in decisions] + [r.confidence for r in requirement_analysis]
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.85

        # 9. Generate 18-Section Structured Engineering Markdown Report (Section 24)
        report_markdown = self.report_generator.generate_report(
            project=input_data.project,
            requirements=requirement_analysis,
            findings=findings,
            tradeoffs=tradeoffs,
            decisions=decisions,
            recommendations=recommendations,
            assumptions=assumptions,
            unknowns=unknowns,
            risks=risks,
            validations=validations,
            experiments=experiments,
            traceability=traceability,
            overall_confidence=overall_confidence,
        )

        output = EngineeringSynthesisAgentOutput(
            status="success",
            project=input_data.project,
            requirement_analysis=requirement_analysis,
            technical_findings=findings,
            tradeoffs=tradeoffs,
            decisions=decisions,
            recommendations=recommendations,
            assumptions=assumptions,
            unknowns=unknowns,
            risks=risks,
            validation_requirements=validations,
            experiments=experiments,
            traceability=traceability,
            overall_confidence=overall_confidence,
            structured_report_markdown=report_markdown,
        )

        # 10. File Export if output_dir provided (Section 36)
        if input_data.output_dir:
            self.file_exporter.export_artifacts(output, input_data.output_dir, overwrite=True)

        elapsed = time.time() - start_time
        logger.info(
            f"[{exec_id}][{self.NAME}] Synthesis finished in {elapsed:.3f}s: "
            f"Requirements={len(requirement_analysis)} Findings={len(findings)} "
            f"Decisions={len(decisions)} Risks={len(risks)} Validations={len(validations)}"
        )

        return output

    def run_sync(
        self,
        input_data: EngineeringSynthesisAgentInput,
        execution_id: Optional[str] = None,
    ) -> EngineeringSynthesisAgentOutput:
        """Synchronous runner for Google ADK / CLI execution."""
        return asyncio.run(self.run(input_data=input_data, execution_id=execution_id))

    # =========================================================================
    # Internal Google ADK Capability Methods
    # =========================================================================

    def synthesize_engineering(self, input_data: EngineeringSynthesisAgentInput) -> EngineeringSynthesisAgentOutput:
        """ADK Capability: Executes complete engineering synthesis synchronously."""
        return self.run_sync(input_data)

    def map_requirements(
        self, project: ProjectMeta, evidence: List[Dict[str, Any]], findings: List[str]
    ) -> List[RequirementAnalysis]:
        """ADK Capability: Maps project requirements against evidence."""
        return self.requirement_mapper.map_requirements(project, evidence, findings)

    def evaluate_tradeoffs(
        self, project: ProjectMeta, deep_research: Dict[str, Any], evidence: List[Dict[str, Any]]
    ) -> List[EngineeringTradeoff]:
        """ADK Capability: Evaluates multi-option hardware and software trade-offs."""
        return self.tradeoff_analyzer.analyze_tradeoffs(project, deep_research, evidence)

    def make_decisions(
        self,
        project: ProjectMeta,
        reqs: List[RequirementAnalysis],
        findings: List[TechnicalFinding],
        tradeoffs: List[EngineeringTradeoff],
    ) -> List[EngineeringDecision]:
        """ADK Capability: Generates engineering decisions."""
        decisions, _, _, _ = self.decision_engine.generate_decisions_and_recommendations(
            project, reqs, findings, tradeoffs
        )
        return decisions

    def assess_risks(self, project: ProjectMeta, decisions: List[EngineeringDecision]) -> List[EngineeringRisk]:
        """ADK Capability: Performs qualitative risk analysis."""
        return self.risk_analyzer.analyze_risks(project, decisions)

    def plan_validation(
        self, project: ProjectMeta, decisions: List[EngineeringDecision]
    ) -> List[ValidationRequirement]:
        """ADK Capability: Formulates verification and validation procedures."""
        validations, _ = self.validation_planner.plan_validation(project, decisions)
        return validations

    def build_traceability(
        self,
        reqs: List[RequirementAnalysis],
        findings: List[TechnicalFinding],
        tradeoffs: List[EngineeringTradeoff],
        decisions: List[EngineeringDecision],
        validations: List[ValidationRequirement],
    ) -> List[DecisionTraceability]:
        """ADK Capability: Builds complete decision traceability chains."""
        return self.traceability_builder.build_traceability(reqs, findings, tradeoffs, decisions, validations)
