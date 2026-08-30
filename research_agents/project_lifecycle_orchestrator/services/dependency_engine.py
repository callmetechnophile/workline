"""
Dependency evaluation engine for ProjectLifecycleOrchestrator (Sections 16 & 39).
Determines completed, pending, and parallelizable engineering actions from the knowledge graph.
"""

from typing import Any, Dict, List, Set


class DependencyEngine:
    """Evaluates task prerequisite graphs and identifies parallel execution paths."""

    def evaluate_dependencies(
        self,
        tasks: List[Dict[str, Any]],
        completed_task_ids: Set[str],
    ) -> Dict[str, Any]:
        ready_tasks: List[Dict[str, Any]] = []
        blocked_tasks: List[Dict[str, Any]] = []

        for task in tasks:
            t_id = task.get("task_id", "")
            if t_id in completed_task_ids:
                continue

            deps = task.get("dependencies", [])
            unmet = [d for d in deps if d not in completed_task_ids]

            if not unmet:
                ready_tasks.append(task)
            else:
                blocked_tasks.append({
                    "task": task,
                    "unmet_dependencies": unmet,
                })

        # Check parallelizability
        is_parallel = len(ready_tasks) > 1

        return {
            "ready_tasks": ready_tasks,
            "blocked_tasks": blocked_tasks,
            "can_parallelize": is_parallel,
            "parallel_count": len(ready_tasks),
        }
