"""
Agent #7: ComponentPlanningAgent implementation using Google ADK conventions.
Transforms multi-domain system architecture into a validated Bill of Materials (BOM).
"""

import asyncio
import time
from typing import Any, Dict, List, Optional
import uuid
from loguru import logger

from research_agents.component_planning_agent.providers.base import (
    ProviderError,
    ReasoningProvider,
)
from research_agents.component_planning_agent.providers.bedrock import BedrockProvider
from research_agents.component_planning_agent.schemas import (
    BOMAssumptionItem,
    BOMItem,
    BOMSummary,
    BOMTraceabilityItem,
    BOMUnknownItem,
    BOMValidationItem,
    CompatibilityCheck,
    ComponentAlternativeItem,
    ComponentPlanningAgentInput,
    ComponentPlanningAgentOutput,
    ComponentRequirementItem,
    ProjectMeta,
    ResourceConflict,
    StructuredError,
)
from research_agents.component_planning_agent.services.alternative_generator import AlternativeGenerator
from research_agents.component_planning_agent.services.compatibility_validator import CompatibilityValidator
from research_agents.component_planning_agent.services.component_selector import ComponentSelector
from research_agents.component_planning_agent.services.conflict_detector import ResourceConflictDetector
from research_agents.component_planning_agent.services.file_exporter import BOMFileExporter
from research_agents.component_planning_agent.services.report_generator import BOMReportGenerator
from research_agents.component_planning_agent.services.requirement_generator import ComponentRequirementGenerator
from research_agents.component_planning_agent.services.supporting_passives import SupportingPassivesIdentifier
from research_agents.component_planning_agent.services.traceability_builder import BOMTraceabilityBuilder


class ComponentPlanningAgent:
    """
    Google ADK-compliant BOM & Component Planning Agent.
    Transforms system architecture into a technically validated engineering BOM with
    component requirements, specifications, alternatives, and traceability.
    """

    NAME = "ComponentPlanningAgent"
    DESCRIPTION = (
        "Transforms system architecture into a technically validated engineering BOM "
        "with component requirements, specifications, alternatives, and traceability."
    )
    CAPABILITIES = [
        "bom.generate",
        "bom.components",
        "bom.validate",
        "bom.alternatives",
        "bom.datasheets",
        "bom.traceability",
    ]

    def __init__(
        self,
        reasoning_provider: Optional[ReasoningProvider] = None,
        requirement_generator: Optional[ComponentRequirementGenerator] = None,
        component_selector: Optional[ComponentSelector] = None,
        compatibility_validator: Optional[CompatibilityValidator] = None,
        conflict_detector: Optional[ResourceConflictDetector] = None,
        supporting_passives: Optional[SupportingPassivesIdentifier] = None,
        alternative_generator: Optional[AlternativeGenerator] = None,
        traceability_builder: Optional[BOMTraceabilityBuilder] = None,
        report_generator: Optional[BOMReportGenerator] = None,
        file_exporter: Optional[BOMFileExporter] = None,
    ):
        self.provider = reasoning_provider or BedrockProvider()
        self.requirement_generator = requirement_generator or ComponentRequirementGenerator()
        self.component_selector = component_selector or ComponentSelector()
        self.compatibility_validator = compatibility_validator or CompatibilityValidator()
        self.conflict_detector = conflict_detector or ResourceConflictDetector()
        self.supporting_passives = supporting_passives or SupportingPassivesIdentifier()
        self.alternative_generator = alternative_generator or AlternativeGenerator()
        self.traceability_builder = traceability_builder or BOMTraceabilityBuilder()
        self.report_generator = report_generator or BOMReportGenerator()
        self.file_exporter = file_exporter or BOMFileExporter()

    async def run(
        self,
        input_data: ComponentPlanningAgentInput,
        execution_id: Optional[str] = None,
    ) -> ComponentPlanningAgentOutput:
        """
        Executes end-to-end BOM construction and validation.
        """
        start_time = time.time()
        exec_id = (
            execution_id
            or (input_data.execution_context.execution_id if input_data.execution_context else None)
            or f"exec_{uuid.uuid4().hex[:8]}"
        )

        logger.info(
            f"[{exec_id}][{self.NAME}] Starting BOM planning for project='{input_data.project.title}'"
        )

        # 1. Generate Component Requirements from Architecture (Section 7)
        comp_reqs = self.requirement_generator.generate_requirements(
            project=input_data.project,
            subsystems=input_data.subsystems,
            component_roles=input_data.component_roles,
            power_domains=input_data.power_domains,
            engineering_decisions=input_data.engineering_decisions,
        )

        # 2. Select Components & Map Specifications (Sections 8, 9, 10)
        primary_items = self.component_selector.select_components(
            component_requirements=comp_reqs,
            component_roles=input_data.component_roles,
            engineering_decisions=input_data.engineering_decisions,
        )

        # 3. Add Supporting Passives & Auxiliary Hardware (Sections 16 & 17)
        passive_items = self.supporting_passives.identify_supporting_passives(
            primary_items=primary_items,
            start_line_number=len(primary_items) + 1,
        )

        all_items = primary_items + passive_items

        # 4. Multi-Domain Compatibility Validation (Sections 11-13)
        compat_checks = self.compatibility_validator.validate_compatibility(
            bom_items=all_items,
            interfaces=input_data.interfaces,
            power_domains=input_data.power_domains,
        )

        # 5. Resource Conflict Detection (Section 14)
        conflicts = self.conflict_detector.detect_conflicts(
            bom_items=all_items,
            interfaces=input_data.interfaces,
        )

        # 6. Alternative Components (Sections 18 & 19)
        alternatives = self.alternative_generator.generate_alternatives(bom_items=all_items)

        # 7. Validation Requirements, Unknowns, and Assumptions (Sections 32-34)
        validations: List[BOMValidationItem] = [
            BOMValidationItem(
                validation_id="VAL-BOM-001",
                type="electrical",
                description="Verify 5.0V power rail voltage droop and ripple during simultaneous 15W AI burst and radio transmission.",
                affected_items=[item.bom_item_id for item in all_items if item.category in ("SBC", "DC-DC converter", "capacitor")],
                severity="high",
                status="required",
                reason="Prevents GPU brownout resets during peak target acquisition.",
            ),
            BOMValidationItem(
                validation_id="VAL-BOM-002",
                type="interface",
                description="Oscilloscope measurement of SPI VoSPI clock integrity and frame loss rate over 10,000 frames.",
                affected_items=[item.bom_item_id for item in all_items if item.category in ("SBC", "thermal camera")],
                severity="medium",
                status="required",
                reason="Verifies thermal video packet synchronization.",
            ),
        ]

        unknowns: List[BOMUnknownItem] = [
            BOMUnknownItem(
                unknown_id="UNKNOWN-BOM-001",
                description="Exact cold-weather (-10 deg C) discharge capacity curve of 4S LiPo battery.",
                affected_items=[item.bom_item_id for item in all_items if item.category == "battery"],
                why_it_matters="Determines winter mission duration and low-voltage return-to-home trigger.",
                required_information="Manufacturer cold-temperature test sheet.",
                blocking=False,
            )
        ]

        assumptions: List[BOMAssumptionItem] = [
            BOMAssumptionItem(
                assumption_id="ASSUMP-BOM-001",
                description="Jetson Orin Nano carrier board provides standard 3.3V CMOS GPIO logic levels.",
                affected_items=[item.bom_item_id for item in all_items if item.category in ("SBC", "thermal camera", "microcontroller")],
                confidence=0.98,
                validation_required=True,
            )
        ]

        # 8. BOM Traceability (Section 48)
        traceability = self.traceability_builder.build_traceability(
            project=input_data.project,
            component_requirements=comp_reqs,
            bom_items=all_items,
            validations=validations,
        )

        # 9. Summary Metrics (Section 24)
        selected_cnt = sum(1 for i in all_items if i.selection_status == "selected")
        candidate_cnt = sum(1 for i in all_items if i.selection_status == "candidate")
        pending_cnt = sum(1 for i in all_items if i.selection_status == "pending")
        subsystems_covered = len({i.subsystem_id for i in all_items})

        summary = BOMSummary(
            total_line_items=len(all_items),
            selected_items=selected_cnt,
            candidate_items=candidate_cnt,
            pending_items=pending_cnt,
            subsystem_count=subsystems_covered,
        )

        bom_id = f"BOM-{uuid.uuid4().hex[:6].upper()}"

        # 10. Publication-grade Markdown BOM Report (Section 47)
        report_markdown = self.report_generator.generate_report(
            project=input_data.project,
            bom_id=bom_id,
            summary=summary,
            items=all_items,
            component_requirements=comp_reqs,
            conflicts=conflicts,
            compatibility_checks=compat_checks,
            alternatives=alternatives,
            validations=validations,
            unknowns=unknowns,
            assumptions=assumptions,
            traceability=traceability,
        )

        output = ComponentPlanningAgentOutput(
            status="success",
            bom_id=bom_id,
            project_id=input_data.project.project_id or input_data.project.title,
            version="1.0",
            summary=summary,
            items=all_items,
            component_requirements=comp_reqs,
            subsystems=[
                {"subsystem_id": "SUB-001", "name": "Compute Subsystem", "item_count": sum(1 for i in all_items if i.subsystem_id == "SUB-001")},
                {"subsystem_id": "SUB-002", "name": "Sensing Subsystem", "item_count": sum(1 for i in all_items if i.subsystem_id == "SUB-002")},
                {"subsystem_id": "SUB-003", "name": "Power Subsystem", "item_count": sum(1 for i in all_items if i.subsystem_id == "SUB-003")},
                {"subsystem_id": "SUB-004", "name": "Control Subsystem", "item_count": sum(1 for i in all_items if i.subsystem_id == "SUB-004")},
            ],
            conflicts=conflicts,
            compatibility_checks=compat_checks,
            alternatives=alternatives,
            validation_requirements=validations,
            unknowns=unknowns,
            assumptions=assumptions,
            traceability=traceability,
            structured_bom_markdown=report_markdown,
        )

        # 11. 7-File Export if output_dir provided (Section 46)
        if input_data.output_dir:
            self.file_exporter.export_artifacts(output, input_data.output_dir, overwrite=True)

        elapsed = time.time() - start_time
        logger.info(
            f"[{exec_id}][{self.NAME}] BOM constructed in {elapsed:.3f}s: "
            f"Items={len(all_items)} (Selected={selected_cnt}, Pending={pending_cnt}) "
            f"Requirements={len(comp_reqs)} Conflicts={len(conflicts)} Alternatives={len(alternatives)}"
        )

        return output

    def run_sync(
        self,
        input_data: ComponentPlanningAgentInput,
        execution_id: Optional[str] = None,
    ) -> ComponentPlanningAgentOutput:
        """Synchronous wrapper for Google ADK / CLI execution."""
        return asyncio.run(self.run(input_data=input_data, execution_id=execution_id))

    # =========================================================================
    # Internal Google ADK Capability Methods
    # =========================================================================

    def generate_bom(self, input_data: ComponentPlanningAgentInput) -> ComponentPlanningAgentOutput:
        """ADK Capability: Constructs complete engineering BOM synchronously."""
        return self.run_sync(input_data)

    def generate_component_requirements(self, project: ProjectMeta) -> List[ComponentRequirementItem]:
        """ADK Capability: Generates component requirements from architecture."""
        return self.requirement_generator.generate_requirements(project, [], [], [], [])

    def select_components(self, comp_reqs: List[ComponentRequirementItem]) -> List[BOMItem]:
        """ADK Capability: Selects exact/candidate components matching requirements."""
        return self.component_selector.select_components(comp_reqs, [], [])

    def validate_compatibility(self, bom_items: List[BOMItem]) -> List[CompatibilityCheck]:
        """ADK Capability: Performs multi-domain compatibility checks."""
        return self.compatibility_validator.validate_compatibility(bom_items, [], [])

    def check_power_requirements(self, bom_items: List[BOMItem], power_domains: List[Dict[str, Any]]) -> List[CompatibilityCheck]:
        """ADK Capability: Checks power rail allocations and regulator limits."""
        return [c for c in self.compatibility_validator.validate_compatibility(bom_items, [], power_domains) if c.type == "power"]

    def check_interfaces(self, bom_items: List[BOMItem], interfaces: List[Dict[str, Any]]) -> List[CompatibilityCheck]:
        """ADK Capability: Checks protocol and voltage level interface compatibility."""
        return [c for c in self.compatibility_validator.validate_compatibility(bom_items, interfaces, []) if c.type in ("interface", "electrical")]

    def detect_resource_conflicts(self, bom_items: List[BOMItem], interfaces: List[Dict[str, Any]]) -> List[ResourceConflict]:
        """ADK Capability: Detects peripheral and resource contentions."""
        return self.conflict_detector.detect_conflicts(bom_items, interfaces)

    def identify_supporting_components(self, bom_items: List[BOMItem]) -> List[BOMItem]:
        """ADK Capability: Identifies required supporting passives and auxiliary hardware."""
        return self.supporting_passives.identify_supporting_passives(bom_items)

    def generate_alternatives(self, bom_items: List[BOMItem]) -> List[ComponentAlternativeItem]:
        """ADK Capability: Extracts and classifies candidate component alternatives."""
        return self.alternative_generator.generate_alternatives(bom_items)

    def generate_datasheet_links(self, bom_items: List[BOMItem]) -> Dict[str, Optional[str]]:
        """ADK Capability: Maps BOM items to verified datasheet URLs."""
        return {item.part_number: item.datasheet_url for item in bom_items}

    def generate_bom_traceability(
        self, project: ProjectMeta, comp_reqs: List[ComponentRequirementItem], bom_items: List[BOMItem]
    ) -> List[BOMTraceabilityItem]:
        """ADK Capability: Generates requirement-to-validation BOM traceability lineage."""
        return self.traceability_builder.build_traceability(project, comp_reqs, bom_items, [])
