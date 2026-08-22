"""Tests for workspace initialization, directory discovery, creation, and deletion."""

from pathlib import Path
import pytest

from cli.wline.core.manifest import (
    BudgetConfig,
    ProjectManifest,
    TargetPlatformConfig,
    TimelineConfig,
)
from cli.wline.core.paths import get_active_project_name, set_active_project_name
from cli.wline.core.workspace import (
    PROJECT_SUBDIRECTORIES,
    create_project,
    delete_project_dir,
    find_project,
    get_workspace_config,
    init_workspace,
    list_projects,
    update_workspace_config,
)


def test_workspace_initialization(temp_env):
    """Test 1: Workspace initialization creates target directory."""
    target_ws = temp_env["root"] / "NewWorkspace"
    assert not target_ws.exists()

    path, already_init = init_workspace(target_ws)
    assert path == target_ws.resolve()
    assert not already_init
    assert target_ws.exists()
    assert target_ws.is_dir()


def test_repeated_workspace_initialization(temp_env):
    """Test 2: Repeated initialization is safe and reports already initialized."""
    target_ws = temp_env["workspace_dir"]
    path1, init1 = init_workspace(target_ws)
    assert path1.exists()

    path2, init2 = init_workspace(target_ws)
    assert path2 == path1
    assert init2 is True


def test_project_creation(temp_env, sample_manifest):
    """Test 3: Project creation creates all 20 lifecycle subdirectories and workline.yaml."""
    ws = temp_env["workspace_dir"]
    project_dir = create_project(sample_manifest, ws)

    assert project_dir.exists()
    assert (project_dir / "workline.yaml").is_file()

    # Verify all 20 required subdirectories exist
    for sub in PROJECT_SUBDIRECTORIES:
        subdir = project_dir / sub
        assert subdir.exists(), f"Missing lifecycle subdirectory: {sub}"
        assert subdir.is_dir(), f"Expected directory: {sub}"

    # Verify attempting to create same project again raises FileExistsError
    with pytest.raises(FileExistsError):
        create_project(sample_manifest, ws)


def test_project_discovery(temp_env, sample_manifest):
    """Test 7: Project discovery lists only valid projects with workline.yaml."""
    ws = temp_env["workspace_dir"]
    # Initially empty
    assert list_projects(ws) == []

    # Create project 1
    create_project(sample_manifest, ws)

    # Create a non-project dummy folder
    (ws / "random_folder").mkdir()

    # Create project 2
    p2 = ProjectManifest(
        name="smart-greenhouse",
        display_name="Smart Greenhouse",
        domain="iot",
        budget=BudgetConfig(amount=10000.0, currency="INR"),
        timeline=TimelineConfig(target_days=30),
        complexity="low",
        target_platform=TargetPlatformConfig(controller="Raspberry Pi"),
    )
    create_project(p2, ws)

    discovered = list_projects(ws)
    assert len(discovered) == 2
    names = [p.name for p in discovered]
    assert "autonomous-rover" in names
    assert "smart-greenhouse" in names
    assert "random_folder" not in names


def test_find_project(temp_env, sample_manifest):
    """Test find project by name or display name."""
    ws = temp_env["workspace_dir"]
    create_project(sample_manifest, ws)

    # Search by normalized name
    res1 = find_project("autonomous-rover", ws)
    assert res1 is not None
    assert res1[1].name == "autonomous-rover"

    # Search by raw display name
    res2 = find_project("Autonomous Rover", ws)
    assert res2 is not None
    assert res2[1].name == "autonomous-rover"

    # Search non-existent
    assert find_project("non-existent-proj", ws) is None


def test_project_deletion_confirmation_and_safety(temp_env, sample_manifest):
    """Test 14: Project deletion removes project directory and clears active project."""
    ws = temp_env["workspace_dir"]
    project_dir = create_project(sample_manifest, ws)
    assert project_dir.exists()

    set_active_project_name(sample_manifest.name)
    assert get_active_project_name() == sample_manifest.name

    # Delete project
    success = delete_project_dir(sample_manifest.name, ws)
    assert success is True
    assert not project_dir.exists()
    # Active project reference should be cleared
    assert get_active_project_name() is None

    # Deleting non-existent returns False
    assert delete_project_dir("non-existent", ws) is False


def test_configuration(temp_env):
    """Test 16: Configuration reading and updating."""
    new_ws = temp_env["root"] / "CustomWorklineLocation"
    update_workspace_config(new_ws)

    cfg = get_workspace_config()
    assert str(new_ws.resolve()) in cfg["workspace"]
