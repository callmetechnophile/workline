"""
Agent #17: EngineeringComplianceAgent implementation using Google ADK conventions.
Gatekeeper for deterministic engineering compliance, design-rule checking, and safety constraint verification.
"""

import asyncio
from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional
import uuid
from loguru import logger

from research_agents.engineering_compliance.config import compliance_config
from research_agents.engineering_compliance.providers.base import ReasoningProvider
from research_agents.engineering_compliance.providers.bedrock import BedrockComplianceProvider
from research_agents.engineering_compliance.repository.compliance_repository import ComplianceRepository
from research_agents.engineering_compliance.schemas import (
    ComplianceDomainLiteral,
    ComplianceGateLiteral,
    ComplianceInput,
    ComplianceMatrixItem,
    ComplianceOutput,
    ComplianceResult,
    ComplianceRule,
    ComplianceStatusLiteral,
    ComplianceWaiver,
    ProjectComplianceSummary,
)
from research_agents.engineering_compliance.services.file_exporter import ComplianceFileExporter
from research_agents.engineering_compliance.services.gate_service import ComplianceGateService
from research_agents.engineering_compliance.services.matrix_generator import MatrixGenerator
from research_agents.engineering_compliance.services.report_generator import ComplianceReportGenerator
from research_agents.engineering_compliance.services.rule_engine import DesignRuleEngine
from research_agents.engineering_compliance.services.waiver_manager import WaiverManager
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.engineering_knowledge_graph_agent.services.graph_query import KnowledgeGraphService


class EngineeringComplianceAgent:
    """
    Google ADK-compliant Engineering Compliance Agent (Agent #17).
    Deterministic gatekeeper for design rules, safety limits, interface compatibility, and standards.
    """

    NAME = "EngineeringComplianceAgent"
    DESCRIPTION = (
        "Evaluate engineering artifacts against explicit project requirements, "
        "engineering constraints, design rules, validation criteria, and applicable "
        "standards, while producing traceable compliance results."
    )
    CAPABILITIES = [
        "compliance.evaluate",
        "compliance.rules",
        "compliance.gate",
        "compliance.matrix",
        "compliance.waiver",
        "graph.read",
        "graph.insert",
        "graph.update",
    ]

    def __init__(
        self,
        db_client: Optional[SurrealDBClient] = None,
        reasoning_provider: Optional[ReasoningProvider] = None,
    ):
        self.db = db_client or SurrealDBClient()
        self.provider = reasoning_provider or BedrockComplianceProvider()
        self.repo = ComplianceRepository(self.db)
        self.graph_service = KnowledgeGraphService(self.db)
        self.rule_engine = DesignRuleEngine()
        self.gate_service = ComplianceGateService()
        self.waiver_mgr = WaiverManager()
        self.matrix_gen = MatrixGenerator()
        self.report_gen = ComplianceReportGenerator()
        self.exporter = ComplianceFileExporter()

    async def evaluate_compliance(
        self,
        input_data: ComplianceInput,
        custom_artifact_data: Optional[Dict[str, Any]] = None,
    ) -> ComplianceOutput:
        """
        Executes full deterministic compliance evaluation cycle:
        LOAD RULES -> EVALUATE ARTIFACTS -> CHECK WAIVERS -> EVALUATE GATE -> BUILD MATRIX -> EXPORT
        """
        start_time = time.time()
        proj_id = input_data.project_id
        user_id = input_data.user_id

        # 1. Multi-User Project Isolation (Section 98)
        if not await self.graph_service.verify_project_access(proj_id, user_id):
            raise PermissionError(f"ACCESS_DENIED: User '{user_id}' lacks permission for project '{proj_id}'.")

        logger.info(f"[{self.NAME}] Initiating compliance check for project '{proj_id}'")

        # 2. Establish Default Authoritative Rules if not present
        existing_rules = await self.repo.get_rules(proj_id)
        if not existing_rules:
            rules_to_create = [
                ComplianceRule(
                    rule_id="RULE-ELEC-01",
                    project_id=proj_id,
                    name="Voltage Supply Rating Limit",
                    description="Supply voltage must not exceed component maximum rating.",
                    domain="ELECTRICAL",
                    severity="CRITICAL",
                    expression="supply_voltage <= max_rated_voltage",
                    source="VALIDATED_COMPONENT_DATASHEET",
                ),
                ComplianceRule(
                    rule_id="RULE-INTF-01",
                    project_id=proj_id,
                    name="SPI VoSPI Bus Clock Rating",
                    description="VoSPI bus clock frequency must not exceed peripheral limit.",
                    domain="INTERFACE",
                    severity="HIGH",
                    expression="clock_freq_mhz <= max_bus_freq_mhz",
                    source="PROJECT_REQUIREMENT",
                ),
                ComplianceRule(
                    rule_id="RULE-THERM-01",
                    project_id=proj_id,
                    name="Thermal Operating Envelope",
                    description="Operating temperature must satisfy environmental specification.",
                    domain="THERMAL",
                    severity="HIGH",
                    expression="max_operating_temp >= required_operating_temp",
                    source="PROJECT_REQUIREMENT",
                ),
            ]
            for r in rules_to_create:
                await self.repo.create_rule(r)
            existing_rules = rules_to_create

        # Filter domain if specified
        if input_data.domain_filter:
            existing_rules = [r for r in existing_rules if r.domain == input_data.domain_filter]

        # 3. Default Artifact Telemetry (FLIR Lepton 3.5 Sensor + Subsystem)
        artifact_data = custom_artifact_data or {
            "artifact_id": input_data.target_artifact or "component:500-0771-01",
            "artifact_type": "component",
            "requirement_id": "REQ-SAR-001",
            "supply_voltage": 3.3,
            "max_rated_voltage": 3.3,
            "clock_freq_mhz": 15.0,
            "max_bus_freq_mhz": 20.0,
            "max_operating_temp": 80.0,
        }

        # 4. Evaluate Rules Deterministically
        results: List[ComplianceResult] = []
        for rule in existing_rules:
            res = self.rule_engine.evaluate_rule(rule, artifact_data, proj_id)
            await self.repo.create_result(res)
            results.append(res)

        # 5. Fetch Active Waivers
        waivers = await self.repo.get_waivers(proj_id)

        # 6. Evaluate Gate Summary
        summary = self.gate_service.evaluate_gate(proj_id, results, waivers)

        # 7. Build Traceability Matrix
        matrix = self.matrix_gen.build_matrix(results)

        # 8. Render 25-Section Markdown Report
        report_md = self.report_gen.generate_report(summary, results, matrix, waivers)

        # 9. Assemble Output & Export
        output = ComplianceOutput(
            summary=summary,
            results=results,
            matrix=matrix,
            waivers=waivers,
            report_markdown=report_md,
        )

        if input_data.output_dir:
            exported = self.exporter.export_artifacts(
                output_dir=input_data.output_dir,
                summary=summary,
                results=results,
                matrix=matrix,
                waivers=waivers,
                report_markdown=report_md,
            )
            output.exported_files = exported

        elapsed = time.time() - start_time
        logger.info(f"[{self.NAME}] Compliance check completed in {elapsed:.3f}s (Gate={summary.gate}, Status={summary.status})")

        return output

    def evaluate_compliance_sync(
        self,
        input_data: ComplianceInput,
        custom_artifact_data: Optional[Dict[str, Any]] = None,
    ) -> ComplianceOutput:
        """Synchronous wrapper for ADK and CLI."""
        return asyncio.run(self.evaluate_compliance(input_data, custom_artifact_data))

    # =========================================================================
    # Google ADK Capability Methods (Section 77)
    # =========================================================================

    def evaluate_project(self, project_id: str, user_id: str = "user_001") -> ComplianceOutput:
        """ADK Capability: Evaluates overall project compliance."""
        return self.evaluate_compliance_sync(ComplianceInput(project_id=project_id, user_id=user_id))

    def evaluate_artifact(
        self,
        artifact_id: str,
        project_id: str,
        artifact_data: Dict[str, Any],
        user_id: str = "user_001",
    ) -> ComplianceOutput:
        """ADK Capability: Evaluates a single design artifact."""
        return self.evaluate_compliance_sync(
            ComplianceInput(project_id=project_id, target_artifact=artifact_id, user_id=user_id),
            custom_artifact_data=artifact_data,
        )

    def get_compliance_gate(self, project_id: str, user_id: str = "user_001") -> ComplianceGateLiteral:
        """ADK Capability: Returns gate outcome for Agent #14 workflow gating."""
        out = self.evaluate_project(project_id, user_id)
        return out.summary.gate

    def create_waiver_request(
        self,
        project_id: str,
        rule_id: str,
        artifact_id: str,
        reason: str,
        risk: str,
        approved_by: str,
        duration_days: int = 30,
    ) -> ComplianceWaiver:
        """ADK Capability: Creates a scoped, expiring compliance waiver."""
        waiver = self.waiver_mgr.create_waiver(
            project_id=project_id,
            rule_id=rule_id,
            artifact_id=artifact_id,
            reason=reason,
            risk=risk,
            approved_by=approved_by,
            duration_days=duration_days,
        )
        asyncio.run(self.repo.create_waiver(waiver))
        return waiver
