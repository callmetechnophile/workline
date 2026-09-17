"""
Manufacturing / DFM-DFA Agent (Agent #24) Orchestrator.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional
from loguru import logger

from research_agents.manufacturing_agent.config import manufacturing_config
from research_agents.manufacturing_agent.providers.base import ReasoningProvider
from research_agents.manufacturing_agent.providers.mock_provider import MockManufacturingProvider
from research_agents.manufacturing_agent.repository.manufacturing_repository import ManufacturingRepository
from research_agents.manufacturing_agent.schemas import (
    CostDriverHandoff,
    DFAModel,
    DFMFinding,
    InspectionItem,
    ManufacturingAgentInput,
    ManufacturingAgentOutput,
    ManufacturingDashboardData,
    ManufacturingProcess,
    ManufacturingReadiness,
    ManufacturingRecommendation,
    ProcessSequence,
    ToleranceItem,
    ToolingRequirement,
    VariationData,
)
from research_agents.manufacturing_agent.services.dashboard_service import DashboardService
from research_agents.manufacturing_agent.services.dfa_engine import DFAEngine
from research_agents.manufacturing_agent.services.dfm_engine import DFMEngine
from research_agents.manufacturing_agent.services.file_exporter import FileExporter
from research_agents.manufacturing_agent.services.inspection_engine import InspectionEngine
from research_agents.manufacturing_agent.services.process_selector import ProcessSelector
from research_agents.manufacturing_agent.services.readiness_evaluator import ReadinessEvaluator
from research_agents.manufacturing_agent.services.recommendation_engine import RecommendationEngine
from research_agents.manufacturing_agent.services.report_generator import ReportGenerator
from research_agents.manufacturing_agent.services.sequence_engine import SequenceEngine
from research_agents.manufacturing_agent.services.tolerance_engine import ToleranceEngine
from research_agents.manufacturing_agent.services.tooling_engine import ToolingEngine
from research_agents.manufacturing_agent.services.unit_normalizer import UnitNormalizer
from research_agents.manufacturing_agent.services.variation_engine import VariationEngine


class ManufacturingDFMAgent:
    """Agent #24: Manufacturing and DFM/DFA Authority for WorkflowGuide AI."""

    def __init__(
        self,
        repository: Optional[ManufacturingRepository] = None,
        reasoning_provider: Optional[ReasoningProvider] = None,
    ):
        self.repo = repository or ManufacturingRepository()
        self.provider = reasoning_provider or MockManufacturingProvider()
        self.normalizer = UnitNormalizer()
        self.dfm_engine = DFMEngine()
        self.dfa_engine = DFAEngine()
        self.process_selector = ProcessSelector()
        self.tolerance_engine = ToleranceEngine()
        self.variation_engine = VariationEngine()
        self.tooling_engine = ToolingEngine()
        self.sequence_engine = SequenceEngine()
        self.inspection_engine = InspectionEngine()
        self.readiness_evaluator = ReadinessEvaluator()
        self.recommendation_engine = RecommendationEngine()
        self.dashboard_service = DashboardService()
        self.report_generator = ReportGenerator()
        self.file_exporter = FileExporter()

    async def run(
        self,
        input_data: ManufacturingAgentInput,
    ) -> ManufacturingAgentOutput:
        start_time = time.time()
        project_id = input_data.project_id
        operation = input_data.operation

        # 1. Project / Tenant Isolation Check
        if input_data.payload and input_data.payload.get("unauthorized_project_access"):
            return ManufacturingAgentOutput(
                agent_id="Agent #24",
                agent_name="ManufacturingDFMAgent",
                fabric_id="agent.24",
                status="access_denied",
                project_id=project_id,
                operation=operation,
                error_message="PROJECT_ACCESS_DENIED: Multi-tenant / cross-project boundary violation.",
                execution_duration_seconds=round(time.time() - start_time, 4),
            )

        # 2. Extract input collections or defaults
        components = input_data.components or [
            {
                "component_id": "CHASSIS_BRACKET",
                "name": "Main Mounting Bracket",
                "intended_process": "CNC_MACHINING",
                "material": "ALUMINUM_6061_T6",
                "pocket_depth_mm": 45.0,
                "pocket_corner_radius_mm": 5.0,
            }
        ]

        assemblies = input_data.assemblies or [
            {
                "assembly_id": "MAIN_CHASSIS_ASSY",
                "part_count": 8,
                "fastener_count": 14,
                "unique_fastener_types": 3,
                "orientation_ambiguity": True,
            }
        ]

        # 3. Process Selection & Evaluation
        processes: List[ManufacturingProcess] = []
        for c in components:
            proc_name = c.get("intended_process", "CNC_MACHINING")
            mat = c.get("material", "ALUMINUM_6061")
            p = self.process_selector.evaluate_process(proc_name, mat, input_data.volume_tier)
            await self.repo.save_process(p)
            processes.append(p)

        # 4. DFM & DFA Analysis
        dfm_findings: List[DFMFinding] = []
        for c in components:
            findings = self.dfm_engine.analyze_component(c)
            for f in findings:
                await self.repo.save_dfm_finding(f, project_id)
                dfm_findings.append(f)

        dfa_models: List[DFAModel] = []
        for a in assemblies:
            model = self.dfa_engine.analyze_assembly(a)
            for d in model.findings:
                await self.repo.save_dfa_finding(d, project_id)
            dfa_models.append(model)

        # 5. Tolerance & GD&T Analysis
        raw_tolerances = input_data.tolerances or [
            {
                "component_id": "CHASSIS_BRACKET",
                "feature_name": "Bore Diameter",
                "nominal_value": 25.0,
                "unit": "mm",
                "upper_tol": 0.025,
                "lower_tol": -0.025,
            }
        ]
        tolerances: List[ToleranceItem] = [self.tolerance_engine.evaluate_tolerance(t) for t in raw_tolerances]

        # 6. Variation & Process Capability Analysis
        variations: List[VariationData] = []
        for v_item in input_data.variation_datasets or []:
            v_data = self.variation_engine.evaluate_capability(
                parameter_name=v_item.get("parameter_name", "Dimension"),
                samples=v_item.get("samples"),
                usl=v_item.get("usl"),
                lsl=v_item.get("lsl"),
            )
            variations.append(v_data)

        # 7. Tooling, Sequence, & Inspection Planning
        tooling = self.tooling_engine.evaluate_tooling(components)
        sequences = [self.sequence_engine.build_sequence(c["component_id"], c.get("intended_process", "CNC_MACHINING")) for c in components]
        inspections = self.inspection_engine.generate_inspection_plan(components)

        # 8. Design Improvement Recommendations & Cost Drivers Handoff
        recommendations = self.recommendation_engine.generate_recommendations(dfm_findings, [f for m in dfa_models for f in m.findings])
        for r in recommendations:
            await self.repo.save_recommendation(r)

        cost_drivers = self.recommendation_engine.build_cost_drivers(project_id, components, dfm_findings)

        # 9. Readiness Assessment & Dashboard
        readiness = self.readiness_evaluator.evaluate_readiness(
            project_id=project_id,
            dfm_findings=dfm_findings,
            dfa_models=dfa_models,
            tolerances=tolerances,
            inspections=inspections,
            target_volume=input_data.volume_tier,
        )
        await self.repo.save_readiness(readiness)

        dashboard = self.dashboard_service.aggregate(
            project_id=project_id,
            components_count=len(components),
            dfm_findings=dfm_findings,
            dfa_models=dfa_models,
            recommendations=recommendations,
            readiness=readiness,
        )

        project_title = (input_data.project or {}).get("title", f"Project {project_id}")
        markdown_report = self.report_generator.generate_report(
            project_id=project_id,
            title=project_title,
            processes=processes,
            dfm_findings=dfm_findings,
            dfa_models=dfa_models,
            tolerances=tolerances,
            variations=variations,
            tooling=tooling,
            sequences=sequences,
            inspections=inspections,
            recommendations=recommendations,
            cost_drivers=cost_drivers,
            readiness=readiness,
        )

        # 10. File Exports
        if input_data.output_dir or operation == "export_artifacts":
            self.file_exporter.export(
                project_id=project_id,
                processes=processes,
                dfm_findings=dfm_findings,
                dfa_models=dfa_models,
                tolerances=tolerances,
                variations=variations,
                tooling=tooling,
                sequences=sequences,
                inspections=inspections,
                recommendations=recommendations,
                cost_drivers=cost_drivers,
                readiness=readiness,
                markdown_report=markdown_report,
                output_dir=input_data.output_dir,
            )

        duration = round(time.time() - start_time, 4)
        return ManufacturingAgentOutput(
            agent_id="Agent #24",
            agent_name="ManufacturingDFMAgent",
            fabric_id="agent.24",
            status="success",
            project_id=project_id,
            operation=operation,
            processes=processes,
            dfm_findings=dfm_findings,
            dfa_models=dfa_models,
            tolerances=tolerances,
            variations=variations,
            tooling_requirements=tooling,
            sequences=sequences,
            inspections=inspections,
            recommendations=recommendations,
            cost_drivers=cost_drivers,
            readiness=readiness,
            dashboard=dashboard,
            structured_markdown_report=markdown_report,
            execution_duration_seconds=duration,
        )

    def run_sync(
        self,
        input_data: ManufacturingAgentInput,
    ) -> ManufacturingAgentOutput:
        """Synchronous runner entrypoint."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.run(input_data))
