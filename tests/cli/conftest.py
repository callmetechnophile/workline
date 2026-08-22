"""Test fixtures for Workline CLI tests."""

import os
from pathlib import Path
import pytest
from typer.testing import CliRunner

from cli.wline.core.manifest import BudgetConfig, ProjectManifest, TargetPlatformConfig, TimelineConfig


@pytest.fixture
def runner():
    """Typer CLI runner fixture."""
    return CliRunner()


@pytest.fixture
def temp_env(tmp_path, monkeypatch):
    """
    Isolate Workline configuration and workspace to a temporary directory.
    Ensures that tests never modify the user's real home directory.
    """
    config_dir = tmp_path / ".workline"
    workspace_dir = tmp_path / "Workline"

    config_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("WORKLINE_CONFIG_DIR", str(config_dir))
    monkeypatch.setenv("WORKLINE_WORKSPACE", str(workspace_dir))

    return {
        "root": tmp_path,
        "config_dir": config_dir,
        "workspace_dir": workspace_dir,
    }


@pytest.fixture
def sample_manifest():
    """Sample valid project manifest fixture."""
    return ProjectManifest(
        name="autonomous-rover",
        display_name="Autonomous Rover",
        description="Autonomous agricultural rover",
        domain="robotics",
        budget=BudgetConfig(amount=20000.0, currency="INR"),
        timeline=TimelineConfig(target_days=56),
        complexity="medium",
        target_platform=TargetPlatformConfig(controller="ESP32-S3"),
    )
