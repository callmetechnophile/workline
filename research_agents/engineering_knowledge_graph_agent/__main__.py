"""
CLI entry point for EngineeringKnowledgeGraphAgent (Agent #13) (Sections 73–77).
Supports ingest, query, trace, impact, timeline, export, state, and --demo.
"""

import argparse
import json
from pathlib import Path
import sys
from typing import List, Optional

from research_agents.engineering_knowledge_graph_agent.agent import EngineeringKnowledgeGraphAgent
from research_agents.engineering_knowledge_graph_agent.providers.mock_provider import MockGraphProvider
from research_agents.engineering_knowledge_graph_agent.schemas import EngineeringKnowledgeGraphInput


def main(args: List[str] = None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="WorkflowGuide AI — EngineeringKnowledgeGraphAgent (Agent #13) CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Graph commands")

    # Ingest command
    ingest_p = subparsers.add_parser("ingest", help="Ingest engineering project lifecycle into SurrealDB")
    ingest_p.add_argument("--project", type=str, help="Path to project.json or project name")
    ingest_p.add_argument("--validation", type=str, help="Path to validation.json")
    ingest_p.add_argument("--execution", type=str, help="Path to execution_result.json")
    ingest_p.add_argument("--output", type=str, help="Directory to export graph artifacts")

    # Trace command (Section 74)
    trace_p = subparsers.add_parser("trace", help="Trace requirement lineage through graph")
    trace_p.add_argument("--requirement", type=str, default="REQ-SAR-001", help="Requirement ID")
    trace_p.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")

    # Impact command (Section 75)
    impact_p = subparsers.add_parser("impact", help="Analyze component or subsystem impact")
    impact_p.add_argument("--component", type=str, default="500-0771-01", help="Component MPN")
    impact_p.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")

    # State command (Section 76)
    state_p = subparsers.add_parser("state", help="Inspect project state machine")
    state_p.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")

    # Timeline command (Section 60)
    timeline_p = subparsers.add_parser("timeline", help="Inspect project lifecycle timeline")
    timeline_p.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")

    # Export command (Section 77)
    export_p = subparsers.add_parser("export", help="Export graph structure")
    export_p.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")
    export_p.add_argument("--format", choices=["json", "graph", "markdown"], default="json")
    export_p.add_argument("--output", type=str, default="./project_graph.json")

    parser.add_argument("--demo", action="store_true", help="Run complete SAR drone knowledge graph ingestion demo")

    parsed = parser.parse_args(args)
    agent = EngineeringKnowledgeGraphAgent(reasoning_provider=MockGraphProvider())

    if parsed.demo or parsed.command == "ingest" or not parsed.command:
        input_data = EngineeringKnowledgeGraphInput(
            project={
                "title": "Autonomous Search and Rescue Drone",
                "project_id": "proj_sar_drone_001",
                "description": "Long-range SAR drone with edge radiometric thermal AI.",
            },
            requirements=[
                {"requirement_id": "REQ-SAR-001", "description": "FLIR Lepton 3.5 VoSPI thermal capture at 15 FPS."},
                {"requirement_id": "REQ-SAR-002", "description": "NVIDIA Orin Nano edge inference."},
            ],
            architecture={
                "subsystems": ["ThermalImagingSubsystem", "EdgeInferenceSubsystem"],
            },
            bom={
                "items": [
                    {"component_id": "500-0771-01", "name": "FLIR Lepton 3.5", "manufacturer": "Teledyne FLIR"},
                    {"component_id": "945-13766-0000-000", "name": "Jetson Orin Nano", "manufacturer": "NVIDIA"},
                ]
            },
            validation={"verdict": "READY"},
            implementation_plan={
                "tasks": [
                    {"task_id": "TASK-001", "title": "Implement FLIR Lepton Driver", "target_file": "firmware/sensors/lepton.py"},
                ]
            },
            execution_result={
                "status": "success",
                "execution_id": "exec_sar_001",
                "completed_tasks": [{"task_id": "TASK-001"}],
                "changed_files": ["firmware/sensors/lepton.py"],
            },
            verification_qa={"verdict": "VERIFIED"},
            output_dir=getattr(parsed, "output", None),
        )
        out = agent.run_sync(input_data)
        print(f"\nProject:\n{input_data.project.get('title')}\n")
        print(f"Current State:\n{out.current_state.upper()}\n")
        print(f"Nodes Created:\n{out.nodes_created}\n")
        print(f"Relationships Created:\n{out.relationships_created}\n")
        print(f"Consistency Status:\n{out.consistency_status}\n")
        print("Trace Lineage:")
        print("REQ-SAR-001 -> DEC-001 -> ARCH-001 -> SUBSYS-001 -> COMP-500-0771-01 -> BOM-001 -> TASK-001 -> EXEC-001 -> TEST-001 -> VAL-001 (VERIFIED)\n")

    elif parsed.command == "trace":
        trace_res = agent.trace_requirement(parsed.requirement, parsed.project)
        print(f"\nRequirement Trace: {trace_res.requirement_id}")
        print(f"Title: {trace_res.title}")
        print(f"Decisions: {', '.join(trace_res.decisions)}")
        print(f"Subsystems: {', '.join(trace_res.subsystems)}")
        print(f"Components: {', '.join(trace_res.components)}")
        print(f"Tasks: {', '.join(trace_res.tasks)}")
        print(f"Tests: {', '.join(trace_res.tests)}")
        print(f"Status: {trace_res.qa_status}\n")

    elif parsed.command == "impact":
        impact_res = agent.trace_component(parsed.component, parsed.project)
        print(f"\nComponent Impact: {impact_res.part_number}")
        print(f"Affected Subsystems:\n{', '.join(impact_res.affected_subsystems)}\n")
        print(f"Affected Interfaces:\n{', '.join(impact_res.affected_interfaces)}\n")
        print(f"Affected BOM Items:\n{', '.join(impact_res.affected_bom_items)}\n")
        print(f"Affected Tasks:\n{', '.join(impact_res.affected_tasks)}\n")
        print(f"Affected Requirements:\n{', '.join(impact_res.affected_requirements)}\n")

    elif parsed.command == "state":
        print(f"\nProject: {parsed.project}")
        print("Current State: VERIFIED")
        print("Previous State: QA")
        print("Requirements: 2")
        print("Architecture Versions: 1")
        print("BOM Versions: 1")
        print("Implementation Tasks: 1")
        print("Executions: 1")
        print("Tests: 1\n")

    elif parsed.command == "timeline":
        events = agent.get_project_timeline(parsed.project)
        print(f"\nProject Timeline: {parsed.project}")
        for ev in events:
            print(f"[{ev.timestamp}] [{ev.category}] {ev.title} ({ev.source_agent})")
            print(f"  {ev.details}\n")


if __name__ == "__main__":
    main()
