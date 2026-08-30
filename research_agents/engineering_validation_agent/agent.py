"""
Agent #9: EngineeringValidationAgent implementation using Google ADK conventions.
Acts as the definitive engineering quality gate between design and physical execution.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid
from loguru import logger

from research_agents.engineering_validation_agent.config import val_config
from research_agents.engineering_validation_agent.providers.base import ReasoningProvider
from research_agents.engineering_validation_agent.providers.bedrock import BedrockProvider
from research_agents.engineering_validation_agent.schemas import (
    EngineeringValidationAgentInput,
    EngineeringValidationAgentOutput,
    FinalVerdict,
    RequirementValidationItem,
    RequiredCorrection,
    ValidationItem,
    ValidationTraceabilityItem,
)
from research_agents.engineering_validation_agent.services.architecture_validator import ArchitectureValidator
from research_agents.engineering_validation_agent.services.bom_procurement_validator import BOMProcurementValidator
from research_agents.engineering_validation_agent.services.correction_generator import CorrectionGenerator
from research_agents.engineering_validation_agent.services.electrical_validator import ElectricalValidator
from research_agents.engineering_validation_agent.services.file_exporter import ValidationFileExporter
from research_agents.engineering_validation_agent.services.interface_validator import InterfaceValidator
from research_agents.engineering_validation_agent.services.power_validator import PowerValidator
from research_agents.engineering_validation_agent.services.report_generator import ValidationReportGenerator
from research_agents.engineering_validation_agent.services.requirement_validator import RequirementValidator
from research_agents.engineering_validation_agent.services.rule_engine import ValidationEngine
from research_agents.engineering_validation_agent.services.traceability_builder import ValidationTraceabilityBuilder


class EngineeringValidationAgent:
    """
    Google ADK-compliant Engineering Validation & Design Verification Agent.
    Validates the engineering architecture, BOM, procurement plan, and project requirements before execution.
    """

    NAME = "EngineeringValidationAgent"
    DESCRIPTION = "Validates the engineering architecture, BOM, procurement plan, and project requirements before execution."
    CAPABILITIES = [
        "validation.run",
        "validation.requirements",
        "validation.architecture",
        "validation.bom",
        "validation.procurement",
        "validation.report",
        "validation.readiness",
    ]

    def __init__(
        self,
        reasoning_provider: Optional[ReasoningProvider] = None,
        rule_engine: Optional[ValidationEngine] = None,
        requirement_validator: Optional[RequirementValidator] = None,
        architecture_validator: Optional[ArchitectureValidator] = None,
        electrical_validator: Optional[ElectricalValidator] = None,
        power_validator: Optional[PowerValidator] = None,
        interface_validator: Optional[InterfaceValidator] = None,
        bom_procurement_validator: Optional[BOMProcurementValidator] = None,
        correction_generator: Optional[CorrectionGenerator] = None,
        traceability_builder: Optional[ValidationTraceabilityBuilder] = None,
        report_generator: Optional[ValidationReportGenerator] = None,
        file_exporter: Optional[ValidationFileExporter] = None,
    ):
        self.provider = reasoning_provider or BedrockProvider()
        self.rule_engine = rule_engine or ValidationEngine()
        self.requirement_validator = requirement_validator or RequirementValidator()
        self.architecture_validator = architecture_validator or ArchitectureValidator()
        self.electrical_validator = electrical_validator or ElectricalValidator()
        self.power_validator = power_validator or PowerValidator()
        self.interface_validator = interface_validator or InterfaceValidator()
        self.bom_procurement_validator = bom_procurement_validator or BOMProcurementValidator()
        self.correction_generator = correction_generator or CorrectionGenerator()
        self.traceability_builder = traceability_builder or ValidationTraceabilityBuilder()
        self.report_generator = report_generator or ValidationReportGenerator()
        self.file_exporter = file_exporter or ValidationFileExporter()

    async def run(
        self,
        input_data: EngineeringValidationAgentInput,
        execution_id: Optional[str] = None,
    ) -> EngineeringValidationAgentOutput:
        """
        Executes deterministic multi-domain engineering design verification.
        """
        start_time = time.time()
        exec_id = (
            execution_id
            or (input_data.execution_context.execution_id if input_data.execution_context else None)
            or f"exec_{uuid.uuid4().hex[:8]}"
        )

        proj_id = input_data.project.get("project_id") or input_data.project.get("title", "Project")
        proj_title = input_data.project.get("title", "Engineering System Design")

        logger.info(f"[{exec_id}][{self.NAME}] Starting design verification for project='{proj_id}'")

        # 1. Validate Requirements
        req_results = self.requirement_validator.validate_requirements(
            engineering_synthesis=input_data.engineering_synthesis,
            architecture=input_data.architecture,
            bom=input_data.bom,
            optimized_procurement=input_data.optimized_procurement,
        )

        req_passed = sum(1 for r in req_results if r.status == "PASS")
        req_failed = sum(1 for r in req_results if r.status == "FAIL")
        req_unknown = sum(1 for r in req_results if r.status == "UNKNOWN")

        # 2. Build Validation Context
        context: Dict[str, Any] = {
            "project": input_data.project,
            "engineering_synthesis": input_data.engineering_synthesis,
            "architecture": input_data.architecture,
            "subsystems": input_data.subsystems or input_data.architecture.get("subsystems", []),
            "component_roles": input_data.component_roles or input_data.architecture.get("component_roles", []),
            "interfaces": input_data.interfaces or input_data.architecture.get("interfaces", []),
            "power_domains": input_data.power_domains or input_data.architecture.get("power_domains", []),
            "data_flows": input_data.data_flows or input_data.architecture.get("data_flows", []),
            "control_flows": input_data.control_flows or input_data.architecture.get("control_flows", []),
            "dependencies": input_data.dependencies or input_data.architecture.get("dependencies", []),
            "bom": input_data.bom,
            "optimized_procurement": input_data.optimized_procurement,
            "engineering_decisions": input_data.engineering_decisions,
            "risks": input_data.risks,
            "req_passed": req_passed,
            "req_failed": req_failed,
            "req_unknown": req_unknown,
        }

        # 3. Execute Rule Engine
        rule_findings, final_verdict = self.rule_engine.execute_rules(context)

        # 4. Partition Domain Results
        arch_res = [f for f in rule_findings if f.category == "architecture"] or self.architecture_validator.validate_architecture(
            context["subsystems"], context["component_roles"], context["dependencies"]
        )
        elec_res = [f for f in rule_findings if f.category == "electrical"]
        pwr_res = [f for f in rule_findings if f.category == "power"]
        int_res = [f for f in rule_findings if f.category == "interface"]
        res_res = [f for f in rule_findings if f.category == "resource"]
        sw_res = [f for f in rule_findings if f.category == "software"]
        ai_res = [f for f in rule_findings if f.category == "ai_ml"]
        therm_res = [f for f in rule_findings if f.category == "thermal"]
        mech_res = [f for f in rule_findings if f.category == "mechanical"]
        bom_res = [f for f in rule_findings if f.category == "bom"]
        proc_res = [f for f in rule_findings if f.category == "procurement"]

        crit_fails = [f for f in rule_findings if f.status == "FAIL" and f.severity == "CRITICAL"]
        warnings = [f for f in rule_findings if f.status == "WARNING"]
        unknowns = [f for f in rule_findings if f.status == "UNKNOWN"]

        # 5. Generate Required Corrections for Failures (Section 49)
        all_failures = [f for f in rule_findings if f.status == "FAIL"]
        corrections = self.correction_generator.generate_corrections(all_failures)

        # 6. Build Validation Traceability (Section 46)
        traceability = self.traceability_builder.build_traceability(context, rule_findings, final_verdict)

        validation_id = f"VAL-{uuid.uuid4().hex[:6].upper()}"

        # 7. Render 21-Section Markdown Report (Section 47)
        report_markdown = self.report_generator.generate_report(
            project_title=proj_title,
            validation_id=validation_id,
            final_verdict=final_verdict,
            req_results=req_results,
            findings=rule_findings,
            critical_fails=crit_fails,
            warnings=warnings,
            unknowns=unknowns,
            corrections=corrections,
            traceability=traceability,
        )

        output = EngineeringValidationAgentOutput(
            status="success",
            project_id=proj_id,
            validation_id=validation_id,
            verdict=final_verdict.verdict,
            requirement_results=req_results,
            architecture_results=arch_res,
            electrical_results=elec_res,
            power_results=pwr_res,
            interface_results=int_res,
            resource_results=res_res,
            software_results=sw_res,
            ai_ml_results=ai_res,
            thermal_results=therm_res,
            mechanical_results=mech_res,
            bom_results=bom_res,
            procurement_results=proc_res,
            rule_results=rule_findings,
            critical_failures=crit_fails,
            warnings=warnings,
            unknowns=unknowns,
            required_corrections=corrections,
            traceability=traceability,
            final_verdict=final_verdict,
            confidence=0.98,
            structured_report_markdown=report_markdown,
        )

        # 8. File Export if output_dir provided (Section 51)
        if input_data.output_dir:
            self.file_exporter.export_artifacts(output, input_data.output_dir, overwrite=True)

        elapsed = time.time() - start_time
        logger.info(
            f"[{exec_id}][{self.NAME}] Verification complete in {elapsed:.3f}s: "
            f"Verdict={final_verdict.verdict} Critical={final_verdict.critical_failures} "
            f"High={final_verdict.high_failures} Warnings={final_verdict.warnings}"
        )

        return output

    def run_sync(
        self,
        input_data: EngineeringValidationAgentInput,
        execution_id: Optional[str] = None,
    ) -> EngineeringValidationAgentOutput:
        """Synchronous wrapper for Google ADK / CLI execution."""
        return asyncio.run(self.run(input_data=input_data, execution_id=execution_id))

    # =========================================================================
    # Internal Google ADK Capability Methods
    # =========================================================================

    def validate_design(self, input_data: EngineeringValidationAgentInput) -> EngineeringValidationAgentOutput:
        """ADK Capability: Executes complete end-to-end design verification."""
        return self.run_sync(input_data)

    def validate_requirements(self, synth: Dict, arch: Dict, bom: Dict, proc: Dict) -> List[RequirementValidationItem]:
        """ADK Capability: Evaluates requirement coverage across design artifacts."""
        return self.requirement_validator.validate_requirements(synth, arch, bom, proc)

    def validate_architecture(self, subsystems: List, roles: List, deps: List) -> List[ValidationItem]:
        """ADK Capability: Validates subsystem hierarchy and component roles."""
        return self.architecture_validator.validate_architecture(subsystems, roles, deps)

    def validate_components(self, bom: Dict) -> List[ValidationItem]:
        """ADK Capability: Validates component parameters and specifications."""
        return self.bom_procurement_validator.validate_bom({"bom": bom})

    def validate_electrical(self, context: Dict) -> List[ValidationItem]:
        """ADK Capability: Validates logic voltage levels and electrical interfaces."""
        return self.electrical_validator.validate_electrical(context)

    def validate_power(self, context: Dict) -> List[ValidationItem]:
        """ADK Capability: Validates current loads and regulator headroom."""
        return self.power_validator.validate_power(context)

    def validate_interfaces(self, context: Dict) -> List[ValidationItem]:
        """ADK Capability: Validates protocol handshakes and bus assignments."""
        return self.interface_validator.validate_interfaces(context)

    def validate_resources(self, context: Dict) -> List[ValidationItem]:
        """ADK Capability: Validates pin and peripheral channel capacities."""
        return self.interface_validator.validate_resources(context)

    def validate_software(self, context: Dict) -> List[ValidationItem]:
        """ADK Capability: Validates OS, firmware, and toolchain stacks."""
        rule = next((r for r in self.rule_engine.rules if r.rule_id == "RULE-SW-001"), None)
        return rule.check(context) if rule else []

    def validate_thermal(self, context: Dict) -> List[ValidationItem]:
        """ADK Capability: Validates heatsink and thermal dissipation strategies."""
        rule = next((r for r in self.rule_engine.rules if r.rule_id == "RULE-THERM-001"), None)
        return rule.check(context) if rule else []

    def validate_mechanical(self, context: Dict) -> List[ValidationItem]:
        """ADK Capability: Validates physical form factor and mounting limits."""
        rule = next((r for r in self.rule_engine.rules if r.rule_id == "RULE-MECH-001"), None)
        return rule.check(context) if rule else []

    def validate_bom(self, context: Dict) -> List[ValidationItem]:
        """ADK Capability: Validates BOM completeness and passives."""
        return self.bom_procurement_validator.validate_bom(context)

    def validate_procurement(self, context: Dict) -> List[ValidationItem]:
        """ADK Capability: Validates procurement allocations against architecture."""
        return self.bom_procurement_validator.validate_procurement(context)

    def run_design_rules(self, context: Dict) -> Tuple[List[ValidationItem], FinalVerdict]:
        """ADK Capability: Executes all deterministic design rules."""
        return self.rule_engine.execute_rules(context)

    def generate_validation_report(self, output: EngineeringValidationAgentOutput) -> str:
        """ADK Capability: Exports Markdown verification report."""
        return output.structured_report_markdown

    def is_ready_for_execution(self, output: EngineeringValidationAgentOutput) -> Dict[str, Any]:
        """ADK Capability: Returns execution gate readiness status (Section 39)."""
        is_ready = output.verdict in ("READY", "READY_WITH_WARNINGS")
        blocking_ids = [f.validation_id for f in output.critical_failures]
        return {
            "ready": is_ready,
            "verdict": output.verdict,
            "blocking_validation_ids": blocking_ids,
        }
