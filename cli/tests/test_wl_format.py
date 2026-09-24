"""
Test suite for the .wl project format — README.wl v2 schema.
"""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from cli.workline.project.readme import (
    AnalysisEntrypoint,
    LiveKitConfig,
    MossStatus,
    ProjectIdentity,
    ProjectIntent,
    ProjectState,
    generate_readme_wl,
    parse_readme_wl,
)


class TestReadmeWLParsing:
    def test_parse_v1_readme(self, tmp_path: Path):
        """v1 flat README.wl should parse without crashing."""
        readme = tmp_path / "README.wl"
        readme.write_text(
            "WORKLINE_PROJECT\n================\n"
            "name: Battery Monitor\n"
            "project_id: BMS-16S-PRO\n"
            "version: 2.1\n"
            "status: ACTIVE\n"
            "domain: power-electronics\n"
            "description: 16S BMS for lithium cells\n"
        )
        identity = parse_readme_wl(readme)
        assert identity.name == "Battery Monitor"
        assert identity.project_id == "BMS-16S-PRO"
        assert identity.version == "2.1"
        assert identity.domain == "power-electronics"
        assert identity.description == "16S BMS for lithium cells"

    def test_parse_v2_readme_with_intent(self, tmp_path: Path):
        """v2 README.wl with intent block parses correctly."""
        content = (
            "WORKLINE_PROJECT\n================\n"
            "name: Robotics Arm\n"
            "project_id: ROBOT-001\n"
            "version: 1.0\n"
            "status: ACTIVE\n"
            "domain: robotics\n"
            "description: 6-DOF robotic arm\n"
            "intent:\n"
            "  goal: Build a 6DOF arm\n"
            "  problem_statement: Need precision manipulation\n"
            "  target_platform: stm32\n"
            "  budget_usd: 500.0\n"
            "  constraints:\n"
            "    - Must fit in 30cm cube\n"
            "    - Max 5A total current\n"
        )
        readme = tmp_path / "README.wl"
        readme.write_text(content)
        identity = parse_readme_wl(readme)
        assert identity.name == "Robotics Arm"
        assert identity.intent.goal == "Build a 6DOF arm"
        assert identity.intent.target_platform == "stm32"
        assert identity.intent.budget_usd == 500.0
        assert len(identity.intent.constraints) == 2
        assert "30cm cube" in identity.intent.constraints[0]

    def test_parse_v2_readme_with_state(self, tmp_path: Path):
        content = (
            "WORKLINE_PROJECT\n================\n"
            "name: IoT Device\nproject_id: IOT-001\nversion: 1.0\n"
            "state:\n"
            "  stage: bom\n"
            "  phase: active\n"
            "  completion_pct: 45\n"
            "  active_milestone: M2\n"
        )
        readme = tmp_path / "README.wl"
        readme.write_text(content)
        identity = parse_readme_wl(readme)
        assert identity.state.stage == "bom"
        assert identity.state.completion_pct == 45
        assert identity.state.active_milestone == "M2"

    def test_parse_v2_readme_with_livekit(self, tmp_path: Path):
        content = (
            "WORKLINE_PROJECT\n================\n"
            "name: Voice Project\nproject_id: VOICE-001\nversion: 1.0\n"
            "livekit:\n"
            "  room_name: workline-project-VOICE-001\n"
            "  enabled: true\n"
            "  session_ttl_minutes: 120\n"
        )
        readme = tmp_path / "README.wl"
        readme.write_text(content)
        identity = parse_readme_wl(readme)
        assert identity.livekit.room_name == "workline-project-VOICE-001"
        assert identity.livekit.enabled is True
        assert identity.livekit.session_ttl_minutes == 120
        # CRITICAL: no API keys should be in the README.wl
        text = readme.read_text()
        assert "api_key" not in text.lower()
        assert "api_secret" not in text.lower()
        assert "password" not in text.lower()

    def test_parse_v2_readme_with_moss(self, tmp_path: Path):
        content = (
            "WORKLINE_PROJECT\n================\n"
            "name: Indexed Project\nproject_id: IDX-001\nversion: 1.0\n"
            "moss:\n"
            "  status: READY\n"
            "  document_count: 47\n"
            "  indexed_at: 2026-09-20T10:00:00Z\n"
            "  index_path: .wl/index/\n"
        )
        readme = tmp_path / "README.wl"
        readme.write_text(content)
        identity = parse_readme_wl(readme)
        assert identity.moss.status == "READY"
        assert identity.moss.document_count == 47

    def test_parse_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            parse_readme_wl(tmp_path / "README.wl")


class TestReadmeWLGeneration:
    def test_generate_v2_readme_has_all_blocks(self):
        identity = ProjectIdentity(
            name="Test Project",
            project_id="TEST-001",
            intent=ProjectIntent(goal="Test goal", target_platform="esp32"),
            state=ProjectState(stage="architecture", completion_pct=30),
            analysis_entrypoint=AnalysisEntrypoint(),
            livekit=LiveKitConfig(enabled=True),
            moss=MossStatus(status="READY", document_count=12),
        )
        output = generate_readme_wl(identity)

        # Core fields
        assert "name: Test Project" in output
        assert "project_id: TEST-001" in output

        # Extended blocks
        assert "intent:" in output
        assert "goal: Test goal" in output
        assert "state:" in output
        assert "stage: architecture" in output
        assert "completion_pct: 30" in output
        assert "analysis_entrypoint:" in output
        assert "livekit:" in output
        assert "moss:" in output
        assert "status: READY" in output
        assert "document_count: 12" in output

    def test_generate_readme_no_secrets(self):
        """Generated README.wl must never contain API keys or secrets."""
        identity = ProjectIdentity(
            name="Secure Project",
            project_id="SEC-001",
            livekit=LiveKitConfig(enabled=True, room_name="workline-project-SEC-001"),
        )
        output = generate_readme_wl(identity)
        assert "api_key" not in output.lower()
        assert "api_secret" not in output.lower()
        assert "password" not in output.lower()
        assert "token" not in output.lower()

    def test_roundtrip(self, tmp_path: Path):
        """Generate then parse should produce equivalent identity."""
        identity = ProjectIdentity(
            name="Roundtrip Project",
            project_id="RT-001",
            version="3.0",
            domain="robotics",
            description="Roundtrip test",
            intent=ProjectIntent(goal="Test goal", budget_usd=1000.0),
            state=ProjectState(stage="bom", completion_pct=55),
        )
        content = generate_readme_wl(identity)
        readme = tmp_path / "README.wl"
        readme.write_text(content, encoding="utf-8")
        parsed = parse_readme_wl(readme)

        assert parsed.name == identity.name
        assert parsed.project_id == identity.project_id
        assert parsed.version == identity.version
        assert parsed.intent.goal == identity.intent.goal
        assert parsed.state.stage == identity.state.stage
        assert parsed.state.completion_pct == identity.state.completion_pct
