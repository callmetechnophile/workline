"""
Artifact file exporter for ProjectLifecycleOrchestrator (Section 68).
Generates the 8 mandated JSON and Markdown orchestration artifacts.
"""

import json
from pathlib import Path
from typing import List
from research_agents.project_lifecycle_orchestrator.schemas import (
    BlockerObject,
    DecisionObject,
    HumanRequestObject,
    NextAction,
    OrchestrationRun,
    ProjectHealthObject,
)


class OrchestrationFileExporter:
    """Exports 8 comprehensive JSON and Markdown artifacts for the orchestration run."""

    def export_artifacts(
        self,
        output_dir: str,
        run: OrchestrationRun,
        health: ProjectHealthObject,
        next_action: NextAction,
        blockers: List[BlockerObject],
        human_requests: List[HumanRequestObject],
        decisions: List[DecisionObject],
        report_md: str,
    ) -> List[str]:
        out_p = Path(output_dir).resolve()
        out_p.mkdir(parents=True, exist_ok=True)
        created_files: List[str] = []

        # 1. orchestration_run.json
        f1 = out_p / "orchestration_run.json"
        f1.write_text(json.dumps(run.model_dump(), indent=2), encoding="utf-8")
        created_files.append(str(f1))

        # 2. project_health.json
        f2 = out_p / "project_health.json"
        f2.write_text(json.dumps(health.model_dump(), indent=2), encoding="utf-8")
        created_files.append(str(f2))

        # 3. next_action.json
        f3 = out_p / "next_action.json"
        f3.write_text(json.dumps(next_action.model_dump(), indent=2), encoding="utf-8")
        created_files.append(str(f3))

        # 4. decision_history.json
        f4 = out_p / "decision_history.json"
        f4.write_text(json.dumps([d.model_dump() for d in decisions], indent=2), encoding="utf-8")
        created_files.append(str(f4))

        # 5. blockers.json
        f5 = out_p / "blockers.json"
        f5.write_text(json.dumps([b.model_dump() for b in blockers], indent=2), encoding="utf-8")
        created_files.append(str(f5))

        # 6. human_requests.json
        f6 = out_p / "human_requests.json"
        f6.write_text(json.dumps([h.model_dump() for h in human_requests], indent=2), encoding="utf-8")
        created_files.append(str(f6))

        # 7. state_transitions.json
        f7 = out_p / "state_transitions.json"
        f7.write_text(json.dumps(run.state_transitions, indent=2), encoding="utf-8")
        created_files.append(str(f7))

        # 8. orchestration_report.md
        f8 = out_p / "orchestration_report.md"
        f8.write_text(report_md, encoding="utf-8")
        created_files.append(str(f8))

        return created_files
