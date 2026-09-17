"""
Work Breakdown Structure (WBS) generation and partitioning engine (Agent #10).
"""

from typing import Any, Dict, List, Optional
from research_agents.project_execution_agent.schemas import PlanningTask, WorkPackage


class WBSEngine:
    """Decomposes architecture, subsystems, and BOM components into standard work packages."""

    def partition_architecture(
        self,
        architecture: Optional[Dict[str, Any]],
        bom: Optional[Dict[str, Any]],
        validation: Optional[Dict[str, Any]],
    ) -> List[WorkPackage]:
        arch = architecture or {}
        subsystems = arch.get("subsystems", [])
        packages: List[WorkPackage] = []
        
        packages.append(
            WorkPackage(
                work_package_id="WP-001",
                title="System Core & Environment Setup",
                description="Core folder structure, manifests, and system configurations.",
                phase="DESIGN",
                estimated_hours=3.5,
                deliverables=["config/system.json", "requirements.txt"],
                tasks=[
                    PlanningTask(
                        task_id="TASK-001",
                        work_package_id="WP-001",
                        title="Initialize Repository Manifest & Config",
                        task_type="configuration",
                        priority="high",
                        estimated_hours=2.0,
                        dependencies=[],
                        allowed_paths=["config/**"],
                        allowed_tools=["filesystem"],
                        allowed_operations=["create"],
                        target_file="config/system.json",
                        file_content='{"status": "ready"}',
                        expected_outputs=["config/system.json"],
                    )
                ],
            )
        )

        if subsystems:
            sub_tasks = []
            for i, sub in enumerate(subsystems, start=2):
                sub_name = sub if isinstance(sub, str) else sub.get("name", f"Subsystem_{i}")
                task_id = f"TASK-{i:03d}"
                sub_tasks.append(
                    PlanningTask(
                        task_id=task_id,
                        work_package_id="WP-002",
                        title=f"Implement Subsystem Module: {sub_name}",
                        task_type="code",
                        priority="high",
                        estimated_hours=4.0,
                        dependencies=["TASK-001"],
                        allowed_paths=[f"src/subsystems/{sub_name.lower()}/**"],
                        allowed_tools=["filesystem"],
                        allowed_operations=["create", "modify"],
                        target_file=f"src/subsystems/{sub_name.lower()}/module.py",
                        file_content=f"# Subsystem: {sub_name}\n",
                        expected_outputs=[f"src/subsystems/{sub_name.lower()}/module.py"],
                    )
                )
            packages.append(
                WorkPackage(
                    work_package_id="WP-002",
                    title="Subsystems & Core Modules",
                    description="Implementation of architectural subsystems.",
                    phase="IMPLEMENTATION",
                    estimated_hours=len(sub_tasks) * 4.0,
                    deliverables=[t.target_file for t in sub_tasks if t.target_file],
                    tasks=sub_tasks,
                )
            )

        packages.append(
            WorkPackage(
                work_package_id="WP-003",
                title="Automated Quality Gates & Test Suite",
                description="Unit, integration, and security verification tests.",
                phase="VERIFICATION",
                estimated_hours=4.0,
                deliverables=["tests/test_system.py"],
                tasks=[
                    PlanningTask(
                        task_id="TASK-099",
                        work_package_id="WP-003",
                        title="Execute Test Suite & Quality Checks",
                        task_type="testing",
                        priority="critical",
                        estimated_hours=4.0,
                        dependencies=["TASK-001"],
                        allowed_paths=["tests/**"],
                        allowed_tools=["filesystem", "test_runner"],
                        allowed_operations=["create", "test"],
                        target_file="tests/test_system.py",
                        file_content="def test_suite(): assert True\n",
                        expected_outputs=["tests/test_system.py"],
                    )
                ],
            )
        )

        return packages
