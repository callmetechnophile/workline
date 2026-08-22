"""Tests for project manifest serialization, validation, and name normalization."""

from pathlib import Path
import pytest
import yaml
from pydantic import ValidationError

from cli.wline.core.manifest import (
    BudgetConfig,
    ProjectManifest,
    TargetPlatformConfig,
    TimelineConfig,
    load_manifest,
    normalize_project_name,
    parse_budget_amount,
    parse_timeline_days,
    save_manifest,
)


def test_project_name_normalization():
    """Test 4: Project name normalization handles spaces, special chars, and hyphens."""
    assert normalize_project_name("My Autonomous Solar-Powered Rover") == "my-autonomous-solar-powered-rover"
    assert normalize_project_name("autonomous rover") == "autonomous-rover"
    assert normalize_project_name("   smart---greenhouse_v2   ") == "smart-greenhouse-v2"
    assert normalize_project_name("ESP32-S3 IoT Node!!") == "esp32-s3-iot-node"
    assert normalize_project_name("") == "untitled-project"
    assert normalize_project_name("   ") == "untitled-project"


def test_parsers():
    """Test timeline and budget string parsing helpers."""
    assert parse_timeline_days("8 weeks") == 56
    assert parse_timeline_days("4w") == 28
    assert parse_timeline_days("30 days") == 30
    assert parse_timeline_days("2 months") == 60
    assert parse_timeline_days("45") == 45
    assert parse_timeline_days("") == 56

    assert parse_budget_amount("20000") == 20000.0
    assert parse_budget_amount("INR 50,000.50") == 50000.50
    assert parse_budget_amount("$1500") == 1500.0
    assert parse_budget_amount("") == 0.0


def test_manifest_creation_and_serialization(tmp_path, sample_manifest):
    """Test 5: Manifest creation and save/load cycle."""
    manifest_file = tmp_path / "workline.yaml"
    save_manifest(sample_manifest, manifest_file)

    assert manifest_file.is_file()
    loaded = load_manifest(manifest_file)

    assert loaded.name == sample_manifest.name
    assert loaded.display_name == sample_manifest.display_name
    assert loaded.description == sample_manifest.description
    assert loaded.budget.amount == 20000.0
    assert loaded.budget.currency == "INR"
    assert loaded.timeline.target_days == 56
    assert loaded.target_platform.controller == "ESP32-S3"
    assert len(loaded.lifecycle.stages) == 36


def test_manifest_validation(tmp_path):
    """Test 6: Invalid manifest validation errors."""
    # Test non-existent file
    with pytest.raises(FileNotFoundError):
        load_manifest(tmp_path / "does_not_exist.yaml")

    # Test invalid YAML content (e.g. integer or list instead of dictionary)
    invalid_file = tmp_path / "invalid.yaml"
    invalid_file.write_text("- item1\n- item2", encoding="utf-8")
    with pytest.raises(ValueError):
        load_manifest(invalid_file)

    # Test missing mandatory fields
    corrupt_file = tmp_path / "corrupt.yaml"
    corrupt_file.write_text("description: only description", encoding="utf-8")
    with pytest.raises(ValidationError):
        load_manifest(corrupt_file)
