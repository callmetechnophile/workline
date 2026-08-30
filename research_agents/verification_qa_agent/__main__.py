"""
CLI entry point for VerificationQAAgent (Agent #12) (Section 58).
Supports --plan, --execution, --project, --output, --dry-run, --tests-only, --requirements-only, --security-only, and --demo.
"""

import argparse
import json
from pathlib import Path
import sys
from typing import List, Optional

from research_agents.verification_qa_agent.agent import VerificationQAAgent
from research_agents.verification_qa_agent.providers.mock_provider import MockQAProvider
from research_agents.verification_qa_agent.schemas import VerificationQAAgentInput


def main(args: List[str] = None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="WorkflowGuide AI — VerificationQAAgent (Agent #12) CLI Development Mode"
    )
    parser.add_argument("--plan", type=str, help="Path to implementation_plan.json")
    parser.add_argument("--execution", type=str, help="Path to execution_result.json")
    parser.add_argument("--project", type=str, help="Project name or directory")
    parser.add_argument("--output", type=str, help="Directory to export QA artifacts")
    parser.add_argument("--dry-run", action="store_true", help="Perform inspection without executing tests")
    parser.add_argument("--tests-only", action="store_true", help="Run only authorized verification tests")
    parser.add_argument("--requirements-only", action="store_true", help="Verify only requirement coverage")
    parser.add_argument("--security-only", action="store_true", help="Run only security scanning")
    parser.add_argument("--demo", action="store_true", help="Run end-to-end SAR drone QA verification demo")

    parsed = parser.parse_args(args)

    if parsed.demo or not (parsed.plan and parsed.execution):
        # Built-in SAR Drone Demo
        input_data = VerificationQAAgentInput(
            project={
                "title": parsed.project or "Autonomous Search and Rescue Drone",
                "project_id": "proj_sar_drone_001",
            },
            requirements=[
                {
                    "requirement_id": "REQ-SAR-001",
                    "description": "FLIR Lepton 3.5 thermal camera integration over SPI / VoSPI.",
                },
                {
                    "requirement_id": "REQ-SAR-002",
                    "description": "Real-time edge neural human detection at >= 15 FPS.",
                },
            ],
            architecture={
                "subsystems": ["ThermalImagingSubsystem", "EdgeInferenceSubsystem"],
            },
            bom={
                "items": [
                    {"component_id": "CMP-001", "mpn": "500-0771-01", "name": "FLIR Lepton 3.5"},
                    {"component_id": "CMP-002", "mpn": "945-13766-0000-000", "name": "Jetson Orin Nano"},
                ]
            },
            validation={"verdict": "READY"},
            implementation_plan={
                "tasks": [
                    {
                        "task_id": "TASK-001",
                        "title": "Implement FLIR Lepton VOSPI Sensor Driver",
                        "target_file": "research_agents/engineering_execution_agent/tools/filesystem_tool.py",
                        "acceptance_criteria": ["Driver communicates over SPI at 20MHz", "VoSPI packet sync verified"],
                    },
                    {
                        "task_id": "TASK-002",
                        "title": "Configure Jetson TensorRT Inference Pipeline",
                        "target_file": "research_agents/engineering_execution_agent/tools/test_runner_tool.py",
                        "acceptance_criteria": ["FP16 TensorRT engine loaded", "Latency <= 30ms"],
                    },
                ]
            },
            execution_result={
                "status": "success",
                "authorization_id": "AUTH-SAR-EXEC-001",
                "completed_tasks": [
                    {"task_id": "TASK-001", "title": "Implement FLIR Lepton VOSPI Sensor Driver"},
                    {"task_id": "TASK-002", "title": "Configure Jetson TensorRT Inference Pipeline"},
                ],
                "failed_tasks": [],
                "denied_actions": [],
                "changed_files": [
                    "research_agents/engineering_execution_agent/tools/filesystem_tool.py",
                    "research_agents/engineering_execution_agent/tools/test_runner_tool.py",
                ],
                "tool_calls": [
                    {
                        "tool_call_id": "CALL-001",
                        "task_id": "TASK-001",
                        "tool": "filesystem",
                        "operation": "create",
                        "resource": "research_agents/engineering_execution_agent/tools/filesystem_tool.py",
                        "armoriq_receipt_id": "RCPT-001",
                    }
                ],
                "armoriq_receipts": [
                    {"receipt_id": "RCPT-001", "agent_name": "EngineeringExecutionAgent", "signature": "valid_sig"}
                ],
                "authorized_execution": {
                    "allowed_paths": ["research_agents/engineering_execution_agent/**"],
                },
            },
            dry_run=parsed.dry_run,
            tests_only=parsed.tests_only,
            requirements_only=parsed.requirements_only,
            security_only=parsed.security_only,
            output_dir=parsed.output,
        )
    else:
        # Load from JSON files
        plan_content = json.loads(Path(parsed.plan).read_text(encoding="utf-8"))
        exec_content = json.loads(Path(parsed.execution).read_text(encoding="utf-8"))

        input_data = VerificationQAAgentInput(
            project={"title": parsed.project or "Engineering Project", "project_id": "proj_001"},
            implementation_plan=plan_content,
            execution_result=exec_content,
            validation={"verdict": "READY"},
            dry_run=parsed.dry_run,
            tests_only=parsed.tests_only,
            requirements_only=parsed.requirements_only,
            security_only=parsed.security_only,
            output_dir=parsed.output,
        )

    agent = VerificationQAAgent(reasoning_provider=MockQAProvider())
    output = agent.run_sync(input_data)
    fv = output.final_verdict

    print(f"\nProject:\n{input_data.project.get('title', 'Project')}\n")
    print("Implementation:\nAgent #11\n")
    print(f"Tasks Executed:\n{len(output.tasks)}\n")
    print(f"Tasks Verified:\n{fv.tasks_verified}\n")
    print(f"Tasks Failed:\n{fv.tasks_failed}\n")
    print(f"Tasks Incomplete:\n{fv.unknowns}\n")
    print(f"Tests:\nPassed: {fv.tests_passed}\nFailed: {fv.tests_failed}\n")
    print(f"Requirements:\nPassed: {fv.requirements_passed}\nFailed: {fv.requirements_failed}\nUnknown: {fv.requirements_unknown}\n")
    print(f"Security:\n{'PASS' if fv.security_failures == 0 else 'FAIL'}\n")
    print(f"Architecture:\n{output.architecture_conformance.status}\n")
    print(f"BOM:\n{output.bom_conformance.status}\n")
    print(f"Authorization:\n{output.authorization_verification.get('status', 'PASS')}\n")
    print(f"FINAL VERDICT:\n\n{fv.verdict}\n")
    print(f"Reason:\n\n{fv.recommendation}\n")


if __name__ == "__main__":
    main()
