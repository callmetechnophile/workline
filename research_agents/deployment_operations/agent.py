"""
Deployment & Operations Agent (Agent #26 / agent.26) Orchestrator.
Unified Agent Control Fabric authority for operational readiness, deployment planning,
commissioning, observability, incident management, maintenance, recovery, and retirement.
"""

import time
from typing import Any, Dict, List, Optional
from loguru import logger

from research_agents.deployment_operations.config import config
from research_agents.deployment_operations.providers.base import BaseReasoningProvider
from research_agents.deployment_operations.providers.mock_provider import MockReasoningProvider
from research_agents.deployment_operations.repository.deployment_repository import DeploymentRepository
from research_agents.deployment_operations.schemas import (
    CommissioningPlan,
    DeploymentOpsInput,
    DeploymentOpsOutput,
    DeploymentPlan,
    ReadinessStatus,
    SystemType,
)
from research_agents.deployment_operations.services.commissioning_engine import CommissioningEngine
from research_agents.deployment_operations.services.configuration_engine import ConfigurationEngine
from research_agents.deployment_operations.services.dashboard_service import DashboardService
from research_agents.deployment_operations.services.decommission_engine import DecommissionEngine
from research_agents.deployment_operations.services.dependency_engine import DependencyEngine
from research_agents.deployment_operations.services.deployment_planner import DeploymentPlanner
from research_agents.deployment_operations.services.environment_validator import EnvironmentValidator
from research_agents.deployment_operations.services.file_exporter import FileExporter
from research_agents.deployment_operations.services.health_observability_engine import HealthObservabilityEngine
from research_agents.deployment_operations.services.incident_engine import IncidentEngine
from research_agents.deployment_operations.services.maintenance_serviceability_engine import MaintenanceServiceabilityEngine
from research_agents.deployment_operations.services.operational_mode_engine import OperationalModeEngine
from research_agents.deployment_operations.services.readiness_engine import ReadinessEngine
from research_agents.deployment_operations.services.recovery_rollback_engine import RecoveryRollbackEngine
from research_agents.deployment_operations.services.report_generator import ReportGenerator
from research_agents.deployment_operations.services.spare_parts_planner import SparePartsPlanner
from research_agents.deployment_operations.services.troubleshooting_engine import TroubleshootingEngine
from research_agents.deployment_operations.services.unit_normalizer import OperationalUnitNormalizer


class DeploymentOpsAgent:
    """Agent #26: Deployment & Operations Authority for WorkflowGuide AI."""

    def __init__(
        self,
        repository: Optional[DeploymentRepository] = None,
        reasoning_provider: Optional[BaseReasoningProvider] = None,
    ):
        self.repo = repository or DeploymentRepository()
        self.provider = reasoning_provider or MockReasoningProvider()
        self.unit_normalizer = OperationalUnitNormalizer()
        self.readiness_engine = ReadinessEngine()
        self.deployment_planner = DeploymentPlanner()
        self.commissioning_engine = CommissioningEngine()
        self.config_engine = ConfigurationEngine()
        self.env_validator = EnvironmentValidator()
        self.dependency_engine = DependencyEngine()
        self.observability_engine = HealthObservabilityEngine()
        self.incident_engine = IncidentEngine()
        self.troubleshooting_engine = TroubleshootingEngine()
        self.recovery_engine = RecoveryRollbackEngine()
        self.maintenance_engine = MaintenanceServiceabilityEngine()
        self.spare_parts_planner = SparePartsPlanner()
        self.operational_mode_engine = OperationalModeEngine()
        self.decommission_engine = DecommissionEngine()
        self.dashboard_service = DashboardService()
        self.report_generator = ReportGenerator()
        self.file_exporter = FileExporter()

    async def run(self, input_data: DeploymentOpsInput) -> DeploymentOpsOutput:
        start_time = time.time()
        project_id = input_data.project_id
        system_id = input_data.system_id
        system_type = input_data.system_type
        operation = input_data.operation

        # 1. Multi-tenant / Project boundary check
        if input_data.payload and input_data.payload.get("unauthorized_project_access"):
            return DeploymentOpsOutput(
                agent_id="Agent #26",
                agent_name="DeploymentOpsAgent",
                fabric_id="agent.26",
                status="access_denied",
                project_id=project_id,
                system_id=system_id,
                system_type=system_type,
                operation=operation,
                error_message="PROJECT_ACCESS_DENIED: Multi-tenant boundary violation.",
                execution_duration_seconds=round(time.time() - start_time, 4),
            )

        try:
            # 2. Evaluate Deployment Readiness
            readiness_status, criteria = self.readiness_engine.evaluate_readiness(
                project_id=project_id,
                system_type=system_type,
                components=input_data.components,
                known_risks=input_data.known_risks,
                dfm_handoff=input_data.dfm_handoff,
                supply_chain_handoff=input_data.supply_chain_handoff,
            )

            # 3. Environment & Installation Validation
            install_reqs, env_reqs = self.env_validator.inspect_requirements(system_type)

            # 4. Sequenced Deployment Plan
            is_blocked = readiness_status == ReadinessStatus.BLOCKED
            deployment_plan = self.deployment_planner.create_deployment_plan(
                project_id=project_id,
                system_id=system_id,
                system_type=system_type,
                target_environment=input_data.environment,
                is_blocked=is_blocked,
            )
            await self.repo.save_deployment_plan(
                deployment_plan, team_id=input_data.team_id, user_id=input_data.user_id
            )

            # 5. Commissioning Plan
            comm_plan = self.commissioning_engine.create_commissioning_plan(
                project_id=project_id,
                system_id=system_id,
                system_type=system_type,
            )
            await self.repo.save_commissioning_plan(comm_plan)

            # 6. Operational Baseline & Configuration
            baseline = self.config_engine.create_operational_baseline(
                project_id=project_id,
                system_id=system_id,
                configurations=input_data.configurations or None,
            )
            await self.repo.save_operational_baseline(baseline)

            # 7. Operational Dependencies & SPOF Analysis
            deps = self.dependency_engine.analyze_dependencies(
                system_id=system_id,
                system_type=system_type,
                custom_deps=input_data.dependencies or None,
            )

            # 8. Health Metrics & Alert Rules
            metrics, alerts = self.observability_engine.configure_observability(
                system_id=system_id,
                system_type=system_type,
            )

            # 9. Troubleshooting & Incident
            troubleshooting = self.troubleshooting_engine.build_troubleshooting_tree(
                system_id=system_id,
                reliability_findings=input_data.reliability_handoff,
            )

            # 10. Recovery & Rollback
            recovery_plans = self.recovery_engine.build_recovery_plans(system_id)
            rollback_plan = self.recovery_engine.build_rollback_plan(system_id)
            backup_plan = self.recovery_engine.build_backup_restore_plan(system_id)

            # 11. Maintenance & Serviceability
            maint_tasks = self.maintenance_engine.create_maintenance_tasks(system_id, system_type)
            await self.repo.save_maintenance_tasks(system_id, maint_tasks)
            serv_evals = self.maintenance_engine.evaluate_serviceability(system_id, system_type)

            # 12. Spare Parts Planning
            spares = self.spare_parts_planner.plan_spares(input_data.supply_chain_handoff)

            # 13. Decommissioning Plan
            decomm_plan = self.decommission_engine.create_decommissioning_plan(project_id, system_id)

            # Construct Output
            output = DeploymentOpsOutput(
                agent_id="Agent #26",
                agent_name="DeploymentOpsAgent",
                fabric_id="agent.26",
                status="success",
                project_id=project_id,
                system_id=system_id,
                system_type=system_type,
                operation=operation,
                readiness_status=readiness_status,
                readiness_criteria=criteria,
                deployment_plan=deployment_plan,
                installation_requirements=install_reqs,
                commissioning_plan=comm_plan,
                operational_baseline=baseline,
                dependencies=deps,
                health_metrics=metrics,
                alert_rules=alerts,
                incidents=[],
                troubleshooting_tree=troubleshooting,
                recovery_plans=recovery_plans,
                rollback_plan=rollback_plan,
                backup_restore_plan=backup_plan,
                maintenance_tasks=maint_tasks,
                serviceability_evaluations=serv_evals,
                spare_parts=spares,
                decommissioning_plan=decomm_plan,
                execution_duration_seconds=round(time.time() - start_time, 4),
            )

            # Render full Markdown report
            output.report_markdown = self.report_generator.generate_full_report(output)
            return output

        except Exception as e:
            logger.error(f"DeploymentOpsAgent execution failed: {e}")
            return DeploymentOpsOutput(
                agent_id="Agent #26",
                agent_name="DeploymentOpsAgent",
                fabric_id="agent.26",
                status="error",
                project_id=project_id,
                system_id=system_id,
                system_type=system_type,
                operation=operation,
                error_message=str(e),
                execution_duration_seconds=round(time.time() - start_time, 4),
            )
