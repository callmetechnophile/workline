"""Integration tests for all Workline CLI commands."""

from cli.wline.core.paths import get_active_project_name
from cli.wline.main import app


def test_main_banner_and_help(runner):
    """Test top-level wline invocation displays banner and commands."""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "WORKLINE" in result.stdout
    assert "Engineering Lifecycle Platform" in result.stdout
    assert "init" in result.stdout
    assert "project" in result.stdout
    assert "config" in result.stdout
    assert "version" in result.stdout


def test_version_command(runner):
    """Test 17: wline version and --version flag."""
    from cli.wline import __version__
    res1 = runner.invoke(app, ["version"])
    assert res1.exit_code == 0
    assert "Workline" in res1.stdout
    assert __version__ in res1.stdout
    assert "Schema" in res1.stdout

    res2 = runner.invoke(app, ["--version"])
    assert res2.exit_code == 0
    assert "Workline" in res2.stdout
    assert __version__ in res2.stdout


def test_init_command(runner, temp_env):
    """Test wline init command in temporary workspace."""
    # First execution creates workspace
    res1 = runner.invoke(app, ["init"])
    assert res1.exit_code == 0
    assert "Workline workspace" in res1.stdout

    # Second execution detects already initialized
    res2 = runner.invoke(app, ["init"])
    assert res2.exit_code == 0
    assert "Workline workspace already initialized" in res2.stdout


def test_project_create_interactive(runner, temp_env):
    """Test wline project create with interactive prompt inputs."""
    inputs = "\n".join([
        "autonomous rover",            # Project name
        "Autonomous agricultural rover", # Description
        "robotics",                    # Domain
        "20000",                       # Budget
        "8 weeks",                     # Timeline
        "medium",                      # Complexity
        "ESP32-S3",                    # Target platform
    ]) + "\n"

    result = runner.invoke(app, ["project", "create"], input=inputs)
    assert result.exit_code == 0
    assert "Workspace created" in result.stdout
    assert "Manifest created" in result.stdout
    assert "Lifecycle initialized" in result.stdout
    assert "autonomous-rover" in result.stdout

    # Verify active project was automatically set
    assert get_active_project_name() == "autonomous-rover"


def test_project_create_with_options(runner, temp_env):
    """Test wline project create using command-line options."""
    result = runner.invoke(app, [
        "project", "create",
        "--name", "smart-greenhouse",
        "--description", "Automated IoT Greenhouse",
        "--domain", "iot",
        "--budget", "15000",
        "--timeline", "4 weeks",
        "--complexity", "low",
        "--platform", "Raspberry Pi Pico",
    ])
    assert result.exit_code == 0
    assert "Workspace created" in result.stdout
    assert "smart-greenhouse" in result.stdout


def test_project_list_and_active_handling(runner, temp_env):
    """Test 8 & 10: wline project list and active project tracking."""
    # Create 2 projects
    runner.invoke(app, [
        "project", "create",
        "--name", "autonomous-rover",
        "--description", "Agricultural rover",
        "--domain", "robotics",
        "--budget", "20000",
        "--timeline", "8 weeks",
        "--complexity", "medium",
        "--platform", "ESP32-S3",
    ])
    runner.invoke(app, [
        "project", "create",
        "--name", "smart-greenhouse",
        "--description", "Greenhouse",
        "--domain", "iot",
        "--budget", "10000",
        "--timeline", "4 weeks",
        "--complexity", "low",
        "--platform", "ESP32",
    ])

    # List projects
    res_list = runner.invoke(app, ["project", "list"])
    assert res_list.exit_code == 0
    assert "autonomous-rover" in res_list.stdout
    assert "smart-greenhouse" in res_list.stdout


def test_project_open_and_status(runner, temp_env):
    """Test 9 & 11: wline project open and wline project status."""
    runner.invoke(app, [
        "project", "create",
        "--name", "autonomous-rover",
        "--description", "Agricultural rover",
        "--domain", "robotics",
        "--budget", "20000",
        "--timeline", "8 weeks",
        "--complexity", "medium",
        "--platform", "ESP32-S3",
    ])

    # Open project
    res_open = runner.invoke(app, ["project", "open", "autonomous-rover"])
    assert res_open.exit_code == 0
    assert "Active project set to" in res_open.stdout

    # View status of currently active project
    res_status = runner.invoke(app, ["project", "status"])
    assert res_status.exit_code == 0
    assert "AUTONOMOUS ROVER" in res_status.stdout
    assert "Engineering Lifecycle" in res_status.stdout
    assert "Requirements" in res_status.stdout
    assert "Progress: 0%" in res_status.stdout

    # View status by explicitly passing project name
    res_status2 = runner.invoke(app, ["project", "status", "autonomous-rover"])
    assert res_status2.exit_code == 0
    assert "AUTONOMOUS ROVER" in res_status2.stdout


def test_project_delete_flow(runner, temp_env):
    """Test 14: wline project delete with confirmation flow."""
    runner.invoke(app, [
        "project", "create",
        "--name", "temp-project",
        "--description", "Temporary project",
        "--domain", "testing",
        "--budget", "1000",
        "--timeline", "1 week",
        "--complexity", "low",
        "--platform", "Arduino",
    ])

    # Cancel deletion
    res_cancel = runner.invoke(app, ["project", "delete", "temp-project"], input="n\n")
    assert res_cancel.exit_code == 0
    assert "Deletion cancelled" in res_cancel.stdout

    # Confirm deletion
    res_confirm = runner.invoke(app, ["project", "delete", "temp-project"], input="y\n")
    assert res_confirm.exit_code == 0
    assert "deleted successfully" in res_confirm.stdout

    # Confirm project is no longer in list
    res_list = runner.invoke(app, ["project", "list"])
    assert "temp-project" not in res_list.stdout


def test_invalid_project_handling(runner, temp_env):
    """Test 15: Error handling when referencing non-existent projects."""
    # Open non-existent project
    res_open = runner.invoke(app, ["project", "open", "ghost-project"])
    assert res_open.exit_code == 1
    assert "Error:" in res_open.stdout

    # Status on non-existent project
    res_status = runner.invoke(app, ["project", "status", "ghost-project"])
    assert res_status.exit_code == 1
    assert "Error:" in res_status.stdout

    # Delete non-existent project
    res_delete = runner.invoke(app, ["project", "delete", "ghost-project"])
    assert res_delete.exit_code == 1
    assert "Error:" in res_delete.stdout


def test_config_commands(runner, temp_env):
    """Test 16: wline config show and wline config set."""
    res_show = runner.invoke(app, ["config", "show"])
    assert res_show.exit_code == 0
    assert "WORKLINE CONFIGURATION" in res_show.stdout
    assert "Workspace" in res_show.stdout

    # Update workspace path
    new_ws = temp_env["root"] / "MyCustomWorkspace"
    res_set = runner.invoke(app, ["config", "set", "workspace", str(new_ws)])
    assert res_set.exit_code == 0
    assert "Workspace path updated to:" in res_set.stdout
