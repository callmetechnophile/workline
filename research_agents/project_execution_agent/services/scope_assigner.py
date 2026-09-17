"""ArmorIQ Scope and Tool Permission Assigner for Execution Tasks (Agent #10)."""
from typing import List
from research_agents.project_execution_agent.schemas import PlanningTask

class ScopeAssigner:
    """Assigns least-privilege tools, allowed operations, and filesystem scopes to tasks."""

    def assign_scopes(self, tasks: List[PlanningTask]) -> List[PlanningTask]:
        for task in tasks:
            if not task.allowed_tools:
                if task.task_type in ("code", "firmware", "hardware", "pcb", "configuration", "documentation"):
                    task.allowed_tools = ["filesystem"]
                elif task.task_type in ("testing", "simulation"):
                    task.allowed_tools = ["filesystem", "test_runner"]
                elif task.task_type in ("build", "integration"):
                    task.allowed_tools = ["filesystem", "shell", "compiler"]
                else:
                    task.allowed_tools = ["filesystem"]

            if not task.allowed_operations:
                if task.task_type == "testing":
                    task.allowed_operations = ["read", "create", "test"]
                elif task.task_type in ("build", "integration"):
                    task.allowed_operations = ["read", "create", "modify", "execute"]
                else:
                    task.allowed_operations = ["read", "create", "modify"]

            if not task.allowed_paths and task.target_file:
                dir_path = "/".join(task.target_file.split("/")[:-1])
                task.allowed_paths = [f"{dir_path}/**" if dir_path else "**"]

        return tasks
