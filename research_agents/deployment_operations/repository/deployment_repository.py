"""
SurrealDB graph repository for Agent #26 (DeploymentOpsAgent).
Persists deployment plans, commissioning plans, operational baselines, incidents, and maintenance tasks.
"""

from typing import Any, Dict, List, Optional
from loguru import logger
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.deployment_operations.schemas import (
    CommissioningPlan,
    DeploymentPlan,
    IncidentRecord,
    MaintenanceTask,
    OperationalBaseline,
)


class DeploymentRepository:
    """SurrealDB graph access repository with memory fallback."""

    def __init__(self, db_client: Optional[SurrealDBClient] = None):
        self.db = db_client or SurrealDBClient()
        self._memory_plans: Dict[str, DeploymentPlan] = {}
        self._memory_commissioning: Dict[str, CommissioningPlan] = {}
        self._memory_baselines: Dict[str, OperationalBaseline] = {}
        self._memory_incidents: Dict[str, IncidentRecord] = {}
        self._memory_maintenance: Dict[str, List[MaintenanceTask]] = {}

    async def save_deployment_plan(
        self, plan: DeploymentPlan, team_id: Optional[str] = None, user_id: Optional[str] = None
    ) -> DeploymentPlan:
        self._memory_plans[plan.plan_id] = plan
        try:
            payload = plan.model_dump()
            if team_id:
                payload["team_id"] = team_id
            if user_id:
                payload["user_id"] = user_id
            await self.db.create_node("deployment_plan", plan.plan_id, payload)
            await self.db.relate_nodes(
                f"project:{plan.project_id}", "has_deployment_plan", f"deployment_plan:{plan.plan_id}"
            )
        except Exception as e:
            logger.warning(f"SurrealDB save_deployment_plan fallback: {e}")
        return plan

    async def get_deployment_plan(self, plan_id: str) -> Optional[DeploymentPlan]:
        return self._memory_plans.get(plan_id)

    async def save_commissioning_plan(self, plan: CommissioningPlan) -> CommissioningPlan:
        self._memory_commissioning[plan.plan_id] = plan
        try:
            await self.db.create_node("commissioning_plan", plan.plan_id, plan.model_dump())
        except Exception as e:
            logger.warning(f"SurrealDB save_commissioning_plan fallback: {e}")
        return plan

    async def get_commissioning_plan(self, plan_id: str) -> Optional[CommissioningPlan]:
        return self._memory_commissioning.get(plan_id)

    async def save_operational_baseline(self, baseline: OperationalBaseline) -> OperationalBaseline:
        self._memory_baselines[baseline.baseline_id] = baseline
        try:
            await self.db.create_node("operational_baseline", baseline.baseline_id, baseline.model_dump())
        except Exception as e:
            logger.warning(f"SurrealDB save_operational_baseline fallback: {e}")
        return baseline

    async def get_operational_baseline(self, baseline_id: str) -> Optional[OperationalBaseline]:
        return self._memory_baselines.get(baseline_id)

    async def save_incident(self, incident: IncidentRecord) -> IncidentRecord:
        self._memory_incidents[incident.incident_id] = incident
        try:
            await self.db.create_node("incident", incident.incident_id, incident.model_dump())
            await self.db.relate_nodes(
                f"system:{incident.system_id}", "has_incident", f"incident:{incident.incident_id}"
            )
        except Exception as e:
            logger.warning(f"SurrealDB save_incident fallback: {e}")
        return incident

    async def get_incident(self, incident_id: str) -> Optional[IncidentRecord]:
        return self._memory_incidents.get(incident_id)

    async def save_maintenance_tasks(
        self, system_id: str, tasks: List[MaintenanceTask]
    ) -> List[MaintenanceTask]:
        self._memory_maintenance[system_id] = tasks
        try:
            for t in tasks:
                await self.db.create_node("maintenance_task", t.task_id, t.model_dump())
                await self.db.relate_nodes(
                    f"system:{system_id}", "has_maintenance_task", f"maintenance_task:{t.task_id}"
                )
        except Exception as e:
            logger.warning(f"SurrealDB save_maintenance_tasks fallback: {e}")
        return tasks

    async def get_maintenance_tasks(self, system_id: str) -> List[MaintenanceTask]:
        return self._memory_maintenance.get(system_id, [])
