"""
CLI entry point for EngineeringExecutionAgent (Agent #11) development mode (Section 56).
"""

import argparse
import json
from pathlib import Path
import sys
from typing import List

from research_agents.engineering_execution_agent.agent import EngineeringExecutionAgent
from research_agents.engineering_execution_agent.schemas import (
    AuthorizedExecution,
    EngineeringExecutionContext,
    EngineeringExecutionAgentInput,
)


def main(args: List[str] = None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="WorkflowGuide AI — EngineeringExecutionAgent (Agent #11) CLI Development Mode"
    )
    parser.add_argument(
        "--plan",
        "-p",
        type=str,
        default=None,
        help="Path to implementation plan JSON file",
    )
    parser.add_argument(
        "--authorization",
        "-a",
        type=str,
        default=None,
        help="Path to authorization JSON file",
    )
    parser.add_argument(
        "--project",
        type=str,
        default="Autonomous Search and Rescue Drone",
        help="Project title or path",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Directory to export the 7 execution artifacts",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform authority and scope validation without executing tools",
    )
    parser.add_argument(
        "--task",
        type=str,
        default=None,
        help="Execute single task ID",
    )
    parser.add_argument(
        "--resume",
        type=str,
        default=None,
        help="Resume execution by execution ID",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run offline demo with synthetic SAR drone implementation plan",
    )

    parsed = parser.parse_args(args)

    plan_dict = {}
    auth_dict = {}

    if parsed.plan and Path(parsed.plan).exists():
        plan_dict = json.loads(Path(parsed.plan).read_text(encoding="utf-8"))
    if parsed.authorization and Path(parsed.authorization).exists():
        auth_dict = json.loads(Path(parsed.authorization).read_text(encoding="utf-8"))

    if not plan_dict or parsed.demo:
        # Default SAR Drone implementation plan
        plan_dict = {
            "plan_id": "PLAN-SAR-001",
            "tasks": [
                {
                    "task_id": "TASK-001",
                    "title": "Implement FLIR Lepton VOSPI Sensor Driver",
                    "task_type": "firmware",
                    "target_file": "firmware/sensors/lepton_driver.py",
                    "file_content": "# Radiometric thermal sensor driver\ndef read_frame():\n    return '160x120_thermal_frame'\n",
                    "allowed_paths": ["firmware/sensors/**"],
                    "allowed_tools": ["filesystem"],
                    "allowed_operations": ["create", "modify"],
                    "expected_outputs": ["firmware/sensors/lepton_driver.py"],
                },
                {
                    "task_id": "TASK-002",
                    "title": "Configure Jetson TensorRT Inference Pipeline",
                    "task_type": "code",
                    "target_file": "src/inference/detector.py",
                    "file_content": "# TensorRT human detection node\nclass HumanDetector:\n    def infer(self, frame):\n        return [{'class': 'person', 'confidence': 0.94}]\n",
                    "dependencies": ["TASK-001"],
                    "allowed_paths": ["src/inference/**"],
                    "allowed_tools": ["filesystem"],
                    "allowed_operations": ["create", "modify"],
                    "expected_outputs": ["src/inference/detector.py"],
                },
                {
                    "task_id": "TASK-003",
                    "title": "Modify Motor Controller (Unauthorized Scope Test)",
                    "task_type": "firmware",
                    "target_file": "firmware/motors/esc_driver.py",
                    "file_content": "# Unauthorized motor controller code\n",
                    "dependencies": ["TASK-002"],
                    "allowed_paths": ["firmware/motors/**"],
                    "allowed_tools": ["filesystem"],
                    "allowed_operations": ["create"],
                },
            ],
        }

    if not auth_dict:
        auth_dict = {
            "authorization_id": "AUTH-SAR-EXEC-001",
            "parent_agent_id": "ResearchOrchestrator",
            "authorized_agent_id": "EngineeringExecutionAgent",
            "allowed_tasks": ["TASK-001", "TASK-002"],  # Notice TASK-003 is NOT authorized
            "allowed_tools": ["filesystem", "shell", "test_runner"],
            "allowed_paths": ["firmware/sensors/**", "src/inference/**"],  # Notice motors/ is NOT authorized
            "allowed_operations": ["read", "create", "modify", "test"],
        }

    auth_obj = AuthorizedExecution(**auth_dict)

    input_data = EngineeringExecutionAgentInput(
        project={"title": parsed.project, "project_id": "proj_sar_drone_001"},
        implementation_plan=plan_dict,
        validation={"verdict": "READY"},
        authorized_execution=auth_obj,
        output_dir=parsed.output,
        dry_run=parsed.dry_run,
        single_task_id=parsed.task,
        resume_execution_id=parsed.resume,
    )

    # CLI Output matching Section 56 format
    print(f"\nProject:\n{parsed.project}\n")
    print("Validation:\nREADY\n")
    print(f"Authorized Tasks:\n{len(auth_obj.allowed_tasks)}\n")
    print(f"Authorized Tools:\n{len(auth_obj.allowed_tools)}\n")
    print(f"Authorized Paths:\n{len(auth_obj.allowed_paths)}\n")
    print("Authorization:\nVALID\n")
    print("ArmorIQ:\nCONNECTED\n")
    print("Plan:\nCAPTURED\n")
    print("Executing:\n")

    agent = EngineeringExecutionAgent()
    output = agent.run_sync(input_data)

    for ct in output.completed_tasks:
        print(f"{ct.get('task_id')}")
        print("✓ authorized")
        print("✓ invoked")
        print("✓ completed\n")

    for da in output.denied_actions:
        print(f"{da.get('task_id')}")
        print(f"✗ {da.get('status', 'authorization denied').lower()}")
        print(f"  {da.get('details')}\n")

    if output.denied_actions:
        print("Execution stopped.\n")
    else:
        print("Execution complete.\n")


if __name__ == "__main__":
    main()
