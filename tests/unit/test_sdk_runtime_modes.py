import pytest
from typer.testing import CliRunner

from backend.workline.sdk import (
    Workline,
    LocalRuntime,
    CloudRuntime,
    LocalKnowledgeStore,
    CloudKnowledgeStore,
    LocalGraphStore,
    CloudGraphStore,
)
from cli.wline.main import app as cli_app

runner = CliRunner()


def test_sdk_local_mode_initialization():
    """Verify SDK default local mode initialization."""
    wl = Workline(mode="local")
    assert isinstance(wl.runtime, LocalRuntime)
    assert isinstance(wl.runtime.knowledge, LocalKnowledgeStore)
    assert isinstance(wl.runtime.graph, LocalGraphStore)
    assert wl.mode == "local"


def test_sdk_cloud_mode_initialization():
    """Verify SDK cloud mode initialization."""
    wl = Workline(mode="cloud", api_url="https://api.workline.dev", token="test_token_123")
    assert isinstance(wl.runtime, CloudRuntime)
    assert isinstance(wl.runtime.knowledge, CloudKnowledgeStore)
    assert isinstance(wl.runtime.graph, CloudGraphStore)
    assert wl.mode == "cloud"
    assert wl.api_url == "https://api.workline.dev"


def test_sdk_invalid_mode_raises_error():
    """Verify SDK rejects unknown mode strings."""
    with pytest.raises(ValueError, match="Invalid mode"):
        Workline(mode="offline")  # Invalid mode string


@pytest.mark.asyncio
async def test_sdk_local_knowledge_and_graph_queries():
    """Verify SDK query methods return formatted data in local mode."""
    wl = Workline(mode="local")
    results = await wl.search_knowledge("TPS62130 power derating")
    assert isinstance(results, list)
    assert len(results) > 0

    graph_res = await wl.query_graph("SELECT * FROM requirement")
    assert isinstance(graph_res, list)


def test_sdk_mode_switching_preserves_project_identity():
    """Verify switching from local to cloud mode preserves active project identity."""
    local_wl = Workline(mode="local")
    pjt_local = local_wl.get_current_project()

    cloud_wl = Workline(mode="cloud", api_url="http://localhost:10000")
    pjt_cloud = cloud_wl.get_current_project()

    assert pjt_local == pjt_cloud

    sync_report = cloud_wl.sync()
    assert sync_report["status"] == "synchronized"
    assert sync_report["mode"] == "cloud"


def test_cli_auth_and_sync_commands():
    """Verify wline login, whoami, logout, and sync commands."""
    # 1. whoami
    whoami_res = runner.invoke(cli_app, ["whoami"])
    assert whoami_res.exit_code == 0
    assert "MODE" in whoami_res.output or "Authenticated" in whoami_res.output

    # 2. login with token flag
    login_res = runner.invoke(cli_app, ["login", "--token", "test_bearer_token_xyz"])
    assert login_res.exit_code == 0
    assert "Authenticated successfully" in login_res.output

    # 3. sync
    sync_res = runner.invoke(cli_app, ["sync"])
    assert sync_res.exit_code == 0
    assert "Synchronizing Project" in sync_res.output

    # 4. logout
    logout_res = runner.invoke(cli_app, ["logout"])
    assert logout_res.exit_code == 0
    assert "Logged out successfully" in logout_res.output
