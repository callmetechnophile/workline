"""
SecurityThreatModelingAgent (Agent #22) Orchestrator.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional
from loguru import logger

from research_agents.security_threat.config import security_config
from research_agents.security_threat.providers.base import ReasoningProvider
from research_agents.security_threat.providers.mock_provider import MockSecurityProvider
from research_agents.security_threat.repository.security_repository import SecurityRepository
from research_agents.security_threat.schemas import (
    AssetObject,
    AttackPath,
    AttackSurfaceEntry,
    SecurityControl,
    SecurityDashboardData,
    SecurityFinding,
    SecurityTestCase,
    SecurityThreatModelingAgentInput,
    SecurityThreatModelingAgentOutput,
    ThreatActor,
    ThreatMitigation,
    ThreatObject,
    TrustBoundary,
)
from research_agents.security_threat.services.attack_surface_engine import AttackSurfaceEngine
from research_agents.security_threat.services.change_security_engine import ChangeSecurityEngine
from research_agents.security_threat.services.dashboard_service import DashboardService
from research_agents.security_threat.services.file_exporter import FileExporter
from research_agents.security_threat.services.report_generator import ReportGenerator
from research_agents.security_threat.services.security_control_engine import SecurityControlEngine
from research_agents.security_threat.services.security_test_generator import SecurityTestGenerator
from research_agents.security_threat.services.threat_modeling_engine import ThreatModelingEngine


class SecurityThreatModelingAgent:
    """Agent #22: Security & Threat Modeling Authority for WorkflowGuide AI."""

    def __init__(
        self,
        repository: Optional[SecurityRepository] = None,
        reasoning_provider: Optional[ReasoningProvider] = None,
    ):
        self.repo = repository or SecurityRepository()
        self.provider = reasoning_provider or MockSecurityProvider()
        self.surface_engine = AttackSurfaceEngine()
        self.threat_engine = ThreatModelingEngine()
        self.control_engine = SecurityControlEngine()
        self.change_engine = ChangeSecurityEngine()
        self.test_generator = SecurityTestGenerator()
        self.dashboard_service = DashboardService()
        self.report_generator = ReportGenerator()
        self.file_exporter = FileExporter()

    async def run(
        self,
        input_data: SecurityThreatModelingAgentInput,
    ) -> SecurityThreatModelingAgentOutput:
        start_time = time.time()
        project_id = input_data.project_id
        operation = input_data.operation

        # 1. Project & Tenant Isolation Guard
        if input_data.payload and input_data.payload.get("unauthorized_project_access"):
            return SecurityThreatModelingAgentOutput(
                agent_id="Agent #22",
                status="access_denied",
                project_id=project_id,
                operation=operation,
                error_message="PROJECT_ACCESS_DENIED: Cross-tenant / cross-project boundary violation.",
                execution_duration_seconds=round(time.time() - start_time, 4),
            )

        # 2. Critical Threat Acceptance Guard
        if operation == "accept_threat":
            target_threat = await self.repo.get_threat(input_data.threat_id or "")
            if target_threat and target_threat.is_critical:
                is_authorized = (input_data.authorization or {}).get("authorized_by_human", False)
                if not is_authorized:
                    return SecurityThreatModelingAgentOutput(
                        agent_id="Agent #22",
                        status="authorization_denied",
                        project_id=project_id,
                        operation=operation,
                        error_message="AUTHORIZATION_DENIED: Critical security threats cannot be accepted autonomously without explicit human signoff.",
                        execution_duration_seconds=round(time.time() - start_time, 4),
                    )

        # 3. Discover Assets, Trust Boundaries, and Attack Surface
        assets = self.surface_engine.discover_assets(
            project_id=project_id,
            architecture=input_data.architecture,
            agents_topology=input_data.agents_topology,
            api_definitions=input_data.api_definitions,
        )
        for a in assets:
            await self.repo.save_asset(a)

        boundaries = self.surface_engine.map_trust_boundaries()
        surface = self.surface_engine.map_attack_surface(input_data.api_definitions)

        # 4. Model Threats
        threats = await self.provider.analyze_threat_scenarios(
            project_context=input_data.project or {"project_id": project_id},
            assets=assets,
            attack_surface=surface,
        )

        for t in threats:
            t.risk_score = self.threat_engine.calculate_risk_score(t.likelihood, t.severity)
            t.is_critical = self.threat_engine.is_critical_threat(t)
            await self.repo.save_threat(t)

        # 5. Build Attack Paths
        attack_paths = self.threat_engine.build_attack_paths(threats, surface)
        for p in attack_paths:
            await self.repo.save_attack_path(p)

        # 6. Controls & Mitigations
        controls = self.control_engine.get_standard_controls()
        for c in controls:
            await self.repo.save_control(c)

        mitigations: List[ThreatMitigation] = []
        for t, p in zip(threats, attack_paths):
            m_list = await self.provider.suggest_security_mitigations(t, p)
            for m in m_list:
                await self.repo.save_mitigation(m)
                mitigations.append(m)

        # 7. Security Test Specifications
        security_tests = self.test_generator.generate_tests_for_threats(threats)
        for st in security_tests:
            await self.repo.save_test(st)

        # 8. Change Security Impact
        change_impact = None
        if input_data.change_request:
            change_impact = self.change_engine.evaluate_change_security_impact(
                input_data.change_request, threats, controls
            )

        # 9. Dashboard Posture & Report
        findings: List[SecurityFinding] = []
        dashboard = self.dashboard_service.aggregate(
            project_id=project_id,
            threats=threats,
            attack_surface=surface,
            controls=controls,
            mitigations=mitigations,
            findings=findings,
        )

        project_title = (input_data.project or {}).get("title", f"Project {project_id}")
        markdown_report = self.report_generator.generate_report(
            project_id=project_id,
            title=project_title,
            assets=assets,
            actors=[],
            boundaries=boundaries,
            attack_surface=surface,
            threats=threats,
            attack_paths=attack_paths,
            controls=controls,
            mitigations=mitigations,
            security_tests=security_tests,
            dashboard=dashboard,
        )

        # 10. File Exports
        if input_data.output_dir or operation == "export_artifacts":
            self.file_exporter.export(
                project_id=project_id,
                assets=assets,
                attack_surface=surface,
                threats=threats,
                attack_paths=attack_paths,
                controls=controls,
                security_tests=security_tests,
                dashboard=dashboard,
                markdown_report=markdown_report,
                output_dir=input_data.output_dir,
            )

        duration = round(time.time() - start_time, 4)
        return SecurityThreatModelingAgentOutput(
            agent_id="Agent #22",
            agent_name="SecurityThreatModelingAgent",
            status="success",
            project_id=project_id,
            operation=operation,
            assets=assets,
            threat_actors=[],
            trust_boundaries=boundaries,
            attack_surface=surface,
            threats=threats,
            attack_paths=attack_paths,
            security_controls=controls,
            mitigations=mitigations,
            security_tests=security_tests,
            findings=findings,
            dashboard=dashboard,
            change_impact=change_impact,
            structured_markdown_report=markdown_report,
            execution_duration_seconds=duration,
        )

    def run_sync(
        self,
        input_data: SecurityThreatModelingAgentInput,
    ) -> SecurityThreatModelingAgentOutput:
        """Synchronous runner entrypoint."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.run(input_data))
