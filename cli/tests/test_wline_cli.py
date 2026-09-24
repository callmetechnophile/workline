"""
Test suite for the canonical WORKLINE command model (wline).
Verifies the wline command hierarchy, bootstrap activation, APIs configuration,
Google Drive integration, and absence of wg.
"""

from pathlib import Path
from typing import List
import pytest
from typer.testing import CliRunner

from cli.wline import __version__
from cli.wline.core.activator import activate_environment
from cli.wline.core.credentials import APICredentialManager, REGISTERED_PROVIDERS
from cli.wline.core.session import EnvironmentSessionManager
from cli.wline.main import app

runner = CliRunner()


def _get_command_names() -> List[str]:
    return [cmd.name for cmd in app.registered_commands]


# ── Activation Bootstrap (workline --activate) ────────────────────────────────

class TestActivationBootstrap:
    def test_activate_environment_function(self, tmp_path: Path):
        rc = activate_environment(project_path=tmp_path, interactive=False)
        assert rc == 0
        state = EnvironmentSessionManager.load_state()
        assert state.status in ("ACTIVE", "DEGRADED")
        assert "Runtime" in state.services
        assert "Moss" in state.services
        assert "Agents" in state.services

    def test_session_manager_active_check(self):
        assert EnvironmentSessionManager.is_active()


# ── wline Command Inventory ───────────────────────────────────────────────────

class TestWlineCommandInventory:
    """wline must have the canonical command set and NO wg / separate CLIs."""

    REQUIRED_COMMANDS = [
        "new", "open", "inspect", "status",
        "doctor", "backup", "restore", "sync",
        "drive", "version",
    ]

    FORBIDDEN_COMMANDS = [
        # Domain engineering apps removed from terminal
        "bom", "components", "research", "architecture", "requirements",
        "thermal", "procurement", "search", "context", "ask",
    ]

    def test_required_commands_registered(self):
        names = _get_command_names()
        for cmd in self.REQUIRED_COMMANDS:
            assert cmd in names, f"Required command '{cmd}' not registered in wline"

    def test_forbidden_commands_absent(self):
        names = _get_command_names()
        for cmd in self.FORBIDDEN_COMMANDS:
            assert cmd not in names, f"Domain command '{cmd}' should not be in wline"


# ── wline Core Operations ─────────────────────────────────────────────────────

class TestWlineCoreOperations:
    def test_no_args_shows_environment_status(self):
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert "WORKLINE" in result.output
        assert "Project:" in result.output
        assert "State:" in result.output

    def test_version_command(self):
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_version_flag(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_help_flag(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output or "wline" in result.output

    @pytest.mark.parametrize("cmd", [
        "new", "open", "inspect", "status",
        "doctor", "backup", "restore", "sync", "drive",
    ])
    def test_command_help(self, cmd: str):
        result = runner.invoke(app, [cmd, "--help"])
        assert result.exit_code == 0
        assert len(result.output) > 20

    def test_runtime_subcommands_exist(self):
        result = runner.invoke(app, ["runtime", "--help"])
        assert result.exit_code == 0
        assert "status" in result.output
        assert "start" in result.output
        assert "stop" in result.output
        assert "logs" in result.output


# ── External API Configuration (wline --apis / wline apis) ───────────────────

class TestAPIConfiguration:
    def test_registered_providers_exist(self):
        assert "amazon-bedrock" in REGISTERED_PROVIDERS
        assert "nvidia-nim" in REGISTERED_PROVIDERS
        assert "github" in REGISTERED_PROVIDERS
        assert "livekit" in REGISTERED_PROVIDERS
        assert "nexar" in REGISTERED_PROVIDERS

    def test_apis_status_command(self):
        result = runner.invoke(app, ["apis", "status"])
        assert result.exit_code == 0
        assert "WORKLINE API STATUS" in result.output
        assert "Amazon Bedrock" in result.output
        assert "GitHub" in result.output
        assert "LiveKit Realtime" in result.output

    def test_credential_manager_storage_and_profiles(self):
        prof = "test-profile"
        APICredentialManager.set_provider_credentials(
            "github",
            {"github_token": "ghp_mocktesttoken123"},
            profile=prof,
        )
        creds = APICredentialManager.get_provider_credentials("github", profile=prof)
        assert creds.get("github_token") == "ghp_mocktesttoken123"

        # Check status detects completeness
        status_res = APICredentialManager.check_provider_status("github", profile=prof)
        assert status_res["status"] == "READY"

        # Cleanup
        APICredentialManager.remove_provider_credentials("github", profile=prof)
        status_res2 = APICredentialManager.check_provider_status("github", profile=prof)
        assert status_res2["status"] == "NOT_CONFIGURED"


# ── Google Drive Browser Agent (wline drive) ──────────────────────────────────

class TestGoogleDriveIntegration:
    def test_drive_help(self):
        result = runner.invoke(app, ["drive", "--help"])
        assert result.exit_code == 0
        assert "Google Drive" in result.output
        assert "--action" in result.output
        assert "--no-browser" in result.output

    def test_drive_backup_requires_valid_project(self, tmp_path: Path):
        empty = tmp_path / "empty"
        empty.mkdir()
        result = runner.invoke(app, ["drive", "--path", str(empty), "--no-browser"])
        assert result.exit_code != 0
        assert "not a valid workline project" in result.output.lower() or "missing" in result.output.lower()
