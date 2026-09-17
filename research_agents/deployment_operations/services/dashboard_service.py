"""
Operational posture summary dashboard compiler.
"""

from typing import Any, Dict
from research_agents.deployment_operations.schemas import DeploymentOpsOutput


class DashboardService:
    """Generates aggregated metrics and operational summary dictionaries."""

    def compile_posture(self, output: DeploymentOpsOutput) -> Dict[str, Any]:
        return {
            "project_id": output.project_id,
            "system_id": output.system_id,
            "readiness_status": output.readiness_status.value,
            "total_readiness_criteria": len(output.readiness_criteria),
            "blocking_criteria_count": len([c for c in output.readiness_criteria if c.is_blocking]),
            "deployment_steps_count": len(output.deployment_plan.steps) if output.deployment_plan else 0,
            "commissioning_tests_count": len(output.commissioning_plan.tests) if output.commissioning_plan else 0,
            "health_metrics_count": len(output.health_metrics),
            "alert_rules_count": len(output.alert_rules),
            "maintenance_tasks_count": len(output.maintenance_tasks),
            "critical_spares_count": len([s for s in output.spare_parts if s.is_critical]),
        }
