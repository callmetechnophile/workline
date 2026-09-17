"""
Deterministic Mock reasoning provider for ProjectExecutionAgent (Agent #10).
"""

from typing import Any, Dict, List
from research_agents.project_execution_agent.providers.base import ReasoningProvider
from research_agents.project_execution_agent.schemas import PlanningTask, WorkPackage


class MockProjectExecutionProvider(ReasoningProvider):
    """Deterministic Mock Provider for unit testing and offline benchmarking."""

    async def generate_work_breakdown(
        self,
        project_context: Dict[str, Any],
        architecture: Dict[str, Any],
        bom: Dict[str, Any],
        validation: Dict[str, Any],
    ) -> List[WorkPackage]:
        title = project_context.get("title", "Autonomous Engineering System")
        
        # WP-01: System Core & Setup
        wp1_tasks = [
            PlanningTask(
                task_id="TASK-001",
                work_package_id="WP-001",
                title="Initialize Repository Structure and Manifest",
                description=f"Create folder layout and base configurations for {title}.",
                task_type="code",
                priority="high",
                estimated_hours=2.0,
                dependencies=[],
                allowed_paths=["config/**", "src/**"],
                allowed_tools=["filesystem"],
                allowed_operations=["read", "create"],
                target_file="config/manifest.json",
                file_content='{"project": "' + title + '", "status": "initialized"}\n',
                expected_outputs=["config/manifest.json"],
                validation_criteria=["JSON manifest exists and is valid."],
            ),
            PlanningTask(
                task_id="TASK-002",
                work_package_id="WP-001",
                title="Configure Environment and Dependency Declarations",
                description="Generate requirements.txt and environment variable templates.",
                task_type="configuration",
                priority="high",
                estimated_hours=1.5,
                dependencies=["TASK-001"],
                allowed_paths=["config/**", "requirements.txt"],
                allowed_tools=["filesystem"],
                allowed_operations=["create", "modify"],
                target_file="requirements.txt",
                file_content="pydantic>=2.0.0\nloguru>=0.7.0\n",
                expected_outputs=["requirements.txt"],
                validation_criteria=["Dependencies match engineering requirements."],
            ),
        ]
        wp1 = WorkPackage(
            work_package_id="WP-001",
            title="System Core & Environment Setup",
            description="Foundation layout, environment configurations, and base manifests.",
            phase="DESIGN",
            estimated_hours=3.5,
            deliverables=["config/manifest.json", "requirements.txt"],
            tasks=wp1_tasks,
        )

        # WP-02: Firmware & Sensor Drivers
        wp2_tasks = [
            PlanningTask(
                task_id="TASK-003",
                work_package_id="WP-002",
                title="Implement Sensor & Hardware Interface Drivers",
                description="Develop low-level interface drivers for BOM components.",
                task_type="firmware",
                priority="high",
                estimated_hours=5.0,
                dependencies=["TASK-001"],
                allowed_paths=["firmware/**", "src/drivers/**"],
                allowed_tools=["filesystem", "compiler"],
                allowed_operations=["read", "create", "modify"],
                target_file="firmware/sensors/driver.py",
                file_content="# Low-level sensor hardware driver\nclass SensorDriver:\n    def read(self): return {}\n",
                expected_outputs=["firmware/sensors/driver.py"],
                validation_criteria=["Driver initializes hardware without errors."],
            ),
        ]
        wp2 = WorkPackage(
            work_package_id="WP-002",
            title="Firmware & Hardware Interfaces",
            description="Low-level device drivers and hardware interface abstraction.",
            phase="IMPLEMENTATION",
            estimated_hours=5.0,
            deliverables=["firmware/sensors/driver.py"],
            tasks=wp2_tasks,
        )

        # WP-03: Control Algorithms & Business Logic
        wp3_tasks = [
            PlanningTask(
                task_id="TASK-004",
                work_package_id="WP-003",
                title="Implement Autonomous Controller & State Machine",
                description="Core control loop and system decision logic.",
                task_type="code",
                priority="critical",
                estimated_hours=6.0,
                dependencies=["TASK-002", "TASK-003"],
                allowed_paths=["src/control/**", "src/logic/**"],
                allowed_tools=["filesystem"],
                allowed_operations=["create", "modify"],
                target_file="src/control/controller.py",
                file_content="# Core controller\nclass Controller:\n    def step(self): return True\n",
                expected_outputs=["src/control/controller.py"],
                validation_criteria=["Control loop completes cycle under budget."],
            ),
        ]
        wp3 = WorkPackage(
            work_package_id="WP-003",
            title="Control Logic & Algorithmic Processing",
            description="Autonomous control loop and engineering business logic.",
            phase="IMPLEMENTATION",
            estimated_hours=6.0,
            deliverables=["src/control/controller.py"],
            tasks=wp3_tasks,
        )

        # WP-04: Verification & Quality Gates
        wp4_tasks = [
            PlanningTask(
                task_id="TASK-005",
                work_package_id="WP-004",
                title="Construct Automated Unit & Integration Tests",
                description="Test harness validating controller against design rules.",
                task_type="testing",
                priority="high",
                estimated_hours=4.0,
                dependencies=["TASK-004"],
                allowed_paths=["tests/**"],
                allowed_tools=["filesystem", "test_runner"],
                allowed_operations=["read", "create", "test"],
                target_file="tests/test_system.py",
                file_content="def test_core():\n    assert True\n",
                expected_outputs=["tests/test_system.py"],
                validation_criteria=["100% test pass rate on pytest runner."],
            ),
        ]
        wp4 = WorkPackage(
            work_package_id="WP-004",
            title="Verification & Quality Assurance",
            description="Automated tests and validation harnesses.",
            phase="VERIFICATION",
            estimated_hours=4.0,
            deliverables=["tests/test_system.py"],
            tasks=wp4_tasks,
        )

        return [wp1, wp2, wp3, wp4]
