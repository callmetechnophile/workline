"""
Unit tests for ExecutionFileExporter service (Section 62).
"""

from pathlib import Path
import tempfile
from research_agents.engineering_execution_agent.schemas import (
    EngineeringExecutionAgentOutput,
    ExecutionAuditItem,
    ExecutionGraph,
)
from research_agents.engineering_execution_agent.services.file_exporter import ExecutionFileExporter


def test_file_export_creates_7_artifacts():
    exporter = ExecutionFileExporter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = EngineeringExecutionAgentOutput(
            status="success",
            execution_id="exec_001",
            project_id="proj_01",
            authorization_id="AUTH-01",
            completed_tasks=[{"task_id": "TASK-01", "title": "Sensor Task"}],
            changed_files=["firmware/sensors/lepton.py"],
            audit_trail=[
                ExecutionAuditItem(
                    audit_id="AUD-01",
                    timestamp="2026-08-30T12:00:00Z",
                    project_id="proj_01",
                    execution_id="exec_001",
                    task_id="TASK-01",
                    agent_id="EngineeringExecutionAgent",
                    authorization_id="AUTH-01",
                    tool="filesystem",
                    operation="create",
                    resource="firmware/sensors/lepton.py",
                    status="SUCCESS",
                )
            ],
            structured_report_markdown="# Engineering Execution Report",
        )

        files = exporter.export_artifacts(output, tmp_dir, overwrite=True)
        assert len(files) == 7

        dir_p = Path(tmp_dir)
        assert (dir_p / "execution_result.json").exists()
        assert (dir_p / "execution_report.md").exists()
        assert (dir_p / "execution_graph.json").exists()
        assert (dir_p / "audit_trail.json").exists()
        assert (dir_p / "task_results.json").exists()
        assert (dir_p / "changed_files.json").exists()
        assert (dir_p / "authorization_events.json").exists()
