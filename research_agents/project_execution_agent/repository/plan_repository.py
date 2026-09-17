"""
SurrealDB graph repository for Implementation Plans, Work Packages, and Tasks (Agent #10).
"""

from typing import Any, Dict, List, Optional
from loguru import logger
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.project_execution_agent.schemas import ImplementationPlan, PlanningTask, WorkPackage


class PlanRepository:
    """SurrealDB repository for saving and retrieving implementation plans."""

    def __init__(self, db_client: Optional[SurrealDBClient] = None):
        self.db = db_client or SurrealDBClient()
        self._memory_plans: Dict[str, ImplementationPlan] = {}

    async def save_plan(self, plan: ImplementationPlan) -> ImplementationPlan:
        """Save implementation plan and relate to project node."""
        try:
            await self.db.create_node("implementation_plan", plan.plan_id, plan.model_dump())
            await self.db.relate_nodes(
                f"project:{plan.project_id}",
                "has_implementation_plan",
                f"implementation_plan:{plan.plan_id}",
            )
            for wp in plan.work_packages:
                await self.db.create_node("work_package", wp.work_package_id, wp.model_dump())
                await self.db.relate_nodes(
                    f"implementation_plan:{plan.plan_id}",
                    "contains_work_package",
                    f"work_package:{wp.work_package_id}",
                )
                for task in wp.tasks:
                    await self.db.create_node("execution_task", task.task_id, task.model_dump())
                    await self.db.relate_nodes(
                        f"work_package:{wp.work_package_id}",
                        "contains_task",
                        f"execution_task:{task.task_id}",
                    )
        except Exception as e:
            logger.warning(f"SurrealDB save_plan fallback to in-memory store: {e}")
        
        self._memory_plans[plan.plan_id] = plan
        return plan

    async def get_plan(self, plan_id: str) -> Optional[ImplementationPlan]:
        """Retrieve implementation plan by ID."""
        return self._memory_plans.get(plan_id)

    async def list_plans_for_project(self, project_id: str) -> List[ImplementationPlan]:
        """List all plans for a project."""
        return [p for p in self._memory_plans.values() if p.project_id == project_id]
