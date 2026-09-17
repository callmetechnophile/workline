"""ProjectExecutionAgent (Agent #10) Orchestrator."""
import time
from typing import Any, Dict, Optional
from loguru import logger

from research_agents.project_execution_agent.config import planning_config
from research_agents.project_execution_agent.providers.base import ReasoningProvider
from research_agents.project_execution_agent.providers.mock_provider import MockProjectExecutionProvider
from research_agents.project_execution_agent.repository.plan_repository import PlanRepository
from research_agents.project_execution_agent.schemas import (
    ImplementationPlan,
    ProjectExecutionAgentInput,
    ProjectExecutionAgentOutput,
)
from research_agents.project_execution_agent.services.dag_engine import DAGEngine
from research_agents.project_execution_agent.services.file_exporter import FileExporter
from research_agents.project_execution_agent.services.report_generator import ReportGenerator
from research_agents.project_execution_agent.services.scope_assigner import ScopeAssigner
from research_agents.project_execution_agent.services.wbs_engine import WBSEngine

class ProjectExecutionAgent:
    """Agent #10: Project Execution & Implementation Planning Agent."""

    NAME = "ProjectExecutionAgent"
    DESCRIPTION = "Work Breakdown Structure (WBS) & Implementation Planning Engine"
    CAPABILITIES = ["planning.work_packages", "planning.tasks", "planning.dependencies", "planning.scopes"]

    def __init__(
        self,
        reasoning_provider: Optional[ReasoningProvider] = None,
        repository: Optional[PlanRepository] = None,
    ):
        self.provider = reasoning_provider or MockProjectExecutionProvider()
        self.repo = repository or PlanRepository()
        self.wbs_engine = WBSEngine()
        self.dag_engine = DAGEngine()
        self.scope_assigner = ScopeAssigner()
        self.report_generator = ReportGenerator()
        self.file_exporter = FileExporter()

    async def run(self, input_data: ProjectExecutionAgentInput) -> ProjectExecutionAgentOutput:
        t0 = time.perf_counter()
        
        project_dict = input_data.project or {}
        project_id = input_data.project_id or project_dict.get("project_id", "proj_default_001")
        title = input_data.title or project_dict.get("title", "Engineering Project")
        domain = input_data.engineering_domain or project_dict.get("engineering_domain", "Robotics / Hardware")

        logger.info(f"[{self.NAME}] Generating Implementation Plan for project '{project_id}' ({title}).")

        work_packages = await self.provider.generate_work_breakdown(
            project_context={"project_id": project_id, "title": title, "engineering_domain": domain},
            architecture=input_data.architecture or {},
            bom=input_data.bom or {},
            validation=input_data.validation or {},
        )

        if not work_packages:
            work_packages = self.wbs_engine.partition_architecture(
                input_data.architecture, input_data.bom, input_data.validation
            )

        all_tasks = []
        for wp in work_packages:
            all_tasks.extend(wp.tasks)

        all_tasks = self.scope_assigner.assign_scopes(all_tasks)

        task_lookup = {t.task_id: t for t in all_tasks}
        for wp in work_packages:
            wp.tasks = [task_lookup[t.task_id] for t in wp.tasks if t.task_id in task_lookup]
            wp.estimated_hours = sum(t.estimated_hours for t in wp.tasks)

        dag = self.dag_engine.build_dag(all_tasks)

        total_hours = sum(t.estimated_hours for t in all_tasks)
        execution_readiness = not dag.has_cycle

        blocking_reasons = []
        if dag.has_cycle:
            blocking_reasons.append(f"Circular dependency detected among tasks: {dag.cycle_nodes}")

        plan = ImplementationPlan(
            project_id=project_id,
            title=title,
            engineering_domain=domain,
            work_packages=work_packages,
            all_tasks=all_tasks,
            dag=dag,
            total_estimated_hours=round(total_hours, 2),
            execution_readiness=execution_readiness,
            blocking_reasons=blocking_reasons,
        )

        await self.repo.save_plan(plan)

        report_md = self.report_generator.generate_report(plan)
        if input_data.output_dir:
            self.file_exporter.export(plan, report_md, input_data.output_dir)

        duration = time.perf_counter() - t0
        logger.info(f"[{self.NAME}] Implementation Plan {plan.plan_id} generated in {duration:.3f}s ({len(all_tasks)} tasks, Readiness={execution_readiness}).")

        return ProjectExecutionAgentOutput(
            project_id=project_id,
            plan_id=plan.plan_id,
            implementation_plan=plan,
            work_package_count=len(work_packages),
            task_count=len(all_tasks),
            critical_path_length=len(dag.critical_path),
            structured_markdown_report=report_md,
            execution_readiness=execution_readiness,
            execution_duration_seconds=round(duration, 4),
        )

    def run_sync(self, input_data: ProjectExecutionAgentInput) -> ProjectExecutionAgentOutput:
        """Synchronous wrapper for ProjectExecutionAgent."""
        import asyncio
        return asyncio.run(self.run(input_data))
