"""Tests for Security Sanitization, Secret Redaction, and Team/Project Isolation."""

import pytest
from backend.workline.interoperability.security import (
    ArtifactReference,
    SecuritySanitizer,
)


def test_payload_secret_redaction():
    raw_payload = {
        "board_width": 100.0,
        "api_key": "sk-secret-token-12345",
        "nested": {
            "password": "super-secret-password",
            "db_connection_string": "surrealdb://root:pass@localhost:8000",
            "file_path": "C:\\Users\\worka\\.gemini\\secret_schematic.json",
            "unix_path": "/home/user/project/secrets.env",
            "public_metric": 42.0,
        },
        "token_list": ["auth_token_xyz"],
    }

    sanitized = SecuritySanitizer.sanitize_payload(raw_payload)

    # Verify sensitive keys redacted
    assert sanitized["api_key"] == "[REDACTED_SECRET]"
    assert sanitized["nested"]["password"] == "[REDACTED_SECRET]"
    assert sanitized["nested"]["db_connection_string"] == "[REDACTED_SECRET]"

    # Verify absolute filesystem paths redacted
    assert sanitized["nested"]["file_path"] == "[RESTRICTED_INTERNAL_PATH]"
    assert sanitized["nested"]["unix_path"] == "[RESTRICTED_INTERNAL_PATH]"

    # Verify safe fields preserved
    assert sanitized["board_width"] == 100.0
    assert sanitized["nested"]["public_metric"] == 42.0


def test_team_and_project_isolation():
    # Valid matching team and project
    assert SecuritySanitizer.validate_team_project_isolation(
        request_team_id="team_alpha",
        request_project_id="proj_rover",
        target_team_id="team_alpha",
        target_project_id="proj_rover",
    ) is True

    # Cross-team access attempt -> Rejected
    assert SecuritySanitizer.validate_team_project_isolation(
        request_team_id="team_beta",
        request_project_id="proj_rover",
        target_team_id="team_alpha",
        target_project_id="proj_rover",
    ) is False

    # Empty / Missing team context -> Rejected
    assert SecuritySanitizer.validate_team_project_isolation(
        request_team_id="",
        request_project_id="proj_rover",
        target_team_id="team_alpha",
        target_project_id="proj_rover",
    ) is False


def test_artifact_reference_integrity():
    ref = ArtifactReference(
        artifact_id="art-pcb-001",
        type="application/json",
        size=4096,
        sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        access_scope="read-only",
    )
    assert ref.artifact_id == "art-pcb-001"
    assert ref.access_scope == "read-only"
