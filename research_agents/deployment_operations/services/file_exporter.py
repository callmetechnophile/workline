"""
JSON and CSV exporter for deployment and operations artifacts.
"""

import csv
import io
import json
from research_agents.deployment_operations.schemas import DeploymentOpsOutput


class FileExporter:
    """Exports operational plans and data to JSON and CSV."""

    def to_json(self, output: DeploymentOpsOutput) -> str:
        return json.dumps(output.model_dump(), indent=2)

    def to_csv_deployment_plan(self, output: DeploymentOpsOutput) -> str:
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(["Step Number", "Title", "Action", "Responsible Role", "Expected Result", "Rollback Action", "Requires Auth"])
        if output.deployment_plan:
            for s in output.deployment_plan.steps:
                writer.writerow([
                    s.step_number,
                    s.title,
                    s.action,
                    s.responsible_role,
                    s.expected_result,
                    s.rollback_action or "None",
                    s.requires_authorization,
                ])
        return out.getvalue()
