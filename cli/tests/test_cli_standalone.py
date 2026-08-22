import pytest
from typer.testing import CliRunner
from httpx import AsyncClient, ASGITransport

from cli.wline.main import app as cli_app
from cli.wline import __version__
from cli.wline.commands.doctor import get_doctor_status
from backend.services.cli.main import app as r6_app

runner = CliRunner()


def test_cli_version_flag():
    """Verify wline --version returns version string."""
    result = runner.invoke(cli_app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output or "Workline" in result.output


def test_cli_help_flag():
    """Verify wline --help displays standard command list."""
    result = runner.invoke(cli_app, ["--help"])
    assert result.exit_code == 0
    assert "Workline - Engineering Lifecycle Platform CLI" in result.output
    assert "init" in result.output
    assert "project" in result.output
    assert "doctor" in result.output


def test_cli_doctor_command():
    """Verify wline doctor runs and outputs diagnostic checks."""
    result = runner.invoke(cli_app, ["doctor"])
    assert result.exit_code == 0
    assert "Workline Version" in result.output
    assert "Python Version" in result.output
    
    # Programmatic check
    doc = get_doctor_status()
    assert doc["cli_version"] == __version__
    assert doc["git_installed"] is True


def test_cli_config_show():
    """Verify wline config show outputs current workspace configuration."""
    result = runner.invoke(cli_app, ["config", "show"])
    assert result.exit_code == 0
    assert "WORKLINE CONFIGURATION" in result.output


@pytest.mark.asyncio
async def test_r6_cli_distribution_service():
    """Verify R6 CLI distribution service endpoints."""
    async with AsyncClient(transport=ASGITransport(app=r6_app), base_url="http://test") as client:
        # Health check
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["service"] == "workline-cli-distribution"

        # Version query
        v_resp = await client.get("/api/cli/version")
        assert v_resp.status_code == 200
        assert v_resp.json()["latest_version"] == __version__

        # Manifest query
        m_resp = await client.get("/api/cli/manifest")
        assert m_resp.status_code == 200
        assert m_resp.json()["executable"] == "wline"
