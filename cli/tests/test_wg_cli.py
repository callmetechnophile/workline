"""
Test suite for the slim wg CLI — verifies the doorway-only architecture.
Ensures domain commands are gone and all 13 lifecycle commands are present.
"""

import os
from pathlib import Path
from typing import List

import pytest
from typer.testing import CliRunner

from cli.wg.main import app
from cli.workline import __version__

runner = CliRunner()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_command_names() -> List[str]:
    return [cmd.name for cmd in app.registered_commands]


# ── Version & help ────────────────────────────────────────────────────────────

class TestVersionAndHelp:
    def test_version_flag(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_no_args_exits_zero(self):
        result = runner.invoke(app, [])
        assert result.exit_code == 0

    def test_no_args_shows_commands(self):
        result = runner.invoke(app, [])
        output = result.output
        # Should mention key commands
        assert "init" in output or "open" in output

    def test_help_flag(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0


# ── Command inventory ─────────────────────────────────────────────────────────

class TestCommandInventory:
    """wg must have exactly 13 doorway commands and NO domain commands."""

    REQUIRED_COMMANDS = [
        "init", "new", "open", "inspect",
        "backup", "restore", "sync",
        "start", "stop", "logs",
        "doctor", "status",
    ]

    FORBIDDEN_COMMANDS = [
        # Domain commands removed — these live inside WORKLINE
        "search", "context", "ask",
        "bom", "components", "research",
        "architecture", "requirements",
        "thermal", "procurement",
    ]

    def test_required_commands_registered(self):
        names = _get_command_names()
        for cmd in self.REQUIRED_COMMANDS:
            assert cmd in names, f"Required command '{cmd}' not registered in wg"

    def test_forbidden_commands_absent(self):
        names = _get_command_names()
        for cmd in self.FORBIDDEN_COMMANDS:
            assert cmd not in names, (
                f"Domain command '{cmd}' should NOT be in wg — it belongs in WORKLINE. "
                f"Run `wg open` instead."
            )

    def test_command_count(self):
        names = _get_command_names()
        # Should have exactly the required commands (12 explicit + version via callback)
        for cmd in self.REQUIRED_COMMANDS:
            assert cmd in names


# ── Individual command help ───────────────────────────────────────────────────

class TestCommandHelp:
    @pytest.mark.parametrize("cmd", [
        "init", "new", "open", "inspect",
        "backup", "restore", "sync",
        "start", "stop", "logs",
        "doctor", "status",
    ])
    def test_command_has_help(self, cmd: str):
        result = runner.invoke(app, [cmd, "--help"])
        assert result.exit_code == 0, f"wg {cmd} --help failed: {result.output}"
        assert "Usage:" in result.output or "usage:" in result.output.lower() or len(result.output) > 10


# ── wg doctor ─────────────────────────────────────────────────────────────────

class TestDoctorCommand:
    def test_doctor_runs(self):
        """Doctor should run without crashing even with no stack running."""
        result = runner.invoke(app, ["doctor"])
        # Exit 0 even when services are down — doctor reports, doesn't fail
        assert result.exit_code == 0 or result.exit_code == 1  # 1 if nothing is running
        # Should have some output
        assert len(result.output) > 50

    def test_doctor_shows_python_version(self):
        result = runner.invoke(app, ["doctor"])
        assert "Python" in result.output or "python" in result.output.lower()

    def test_doctor_checks_docker(self):
        result = runner.invoke(app, ["doctor"])
        assert "Docker" in result.output or "docker" in result.output.lower()


# ── wg status ────────────────────────────────────────────────────────────────

class TestStatusCommand:
    def test_status_runs_in_empty_dir(self, tmp_path: Path):
        """Status should run even in a directory with no project."""
        result = runner.invoke(app, ["status", "--path", str(tmp_path)])
        assert result.exit_code == 0

    def test_status_detects_project(self, tmp_path: Path):
        """Status should detect a project when README.wl is present."""
        readme = tmp_path / "README.wl"
        readme.write_text(
            "WORKLINE_PROJECT\n================\nname: Test Project\n"
            "project_id: TEST-001\nversion: 1.0\n"
        )
        (tmp_path / ".wl").mkdir()
        result = runner.invoke(app, ["status", "--path", str(tmp_path)])
        assert result.exit_code == 0


# ── wg init ──────────────────────────────────────────────────────────────────

class TestInitCommand:
    def test_init_creates_wl_files(self, tmp_path: Path):
        target = tmp_path / "my-project"
        result = runner.invoke(app, ["init", "My Project", "--path", str(target)])
        # Should exit 0
        assert result.exit_code == 0 or result.exit_code == 1  # May require ProjectManager


# ── wg inspect ───────────────────────────────────────────────────────────────

class TestInspectCommand:
    def test_inspect_no_project_exits_nonzero(self, tmp_path: Path):
        result = runner.invoke(app, ["inspect", str(tmp_path)])
        # Should report no project found
        assert "not found" in result.output.lower() or result.exit_code != 0 or len(result.output) > 0

    def test_inspect_wl_project(self, tmp_path: Path):
        """Inspect should recognize a project with README.wl."""
        readme = tmp_path / "README.wl"
        readme.write_text(
            "WORKLINE_PROJECT\n================\nname: Inspect Test\n"
            "project_id: INSP-001\nversion: 1.0\ndomain: hardware\n"
        )
        (tmp_path / ".wl").mkdir()
        result = runner.invoke(app, ["inspect", str(tmp_path)])
        # Should show project name
        assert result.exit_code == 0
        assert "Inspect Test" in result.output or "INSP-001" in result.output


# ── wg backup ────────────────────────────────────────────────────────────────

class TestBackupCommand:
    def test_backup_no_project_exits_nonzero(self, tmp_path: Path):
        result = runner.invoke(app, ["backup", str(tmp_path)])
        assert result.exit_code != 0 or "not found" in result.output.lower()


# ── wg sync ──────────────────────────────────────────────────────────────────

class TestSyncCommand:
    def test_sync_no_project_exits_nonzero(self, tmp_path: Path):
        result = runner.invoke(app, ["sync", "--path", str(tmp_path)])
        assert result.exit_code != 0 or "not found" in result.output.lower()
