"""Tests for SecuritySanitizer credential redaction and secret exclusion in project packages."""

import pytest

from backend.workline.project.sanitizer import SecuritySanitizer


def test_sanitizer_removes_sensitive_dictionary_keys():
    """Test stripping api_key, auth_token, passwords, and private_key fields."""
    raw_data = {
        "project_id": "rover-v1",
        "api_key": "sk-1234567890abcdef1234567890abcdef",
        "nested": {
            "password": "SuperSecretPassword123!",
            "token": "ghp_1234567890abcdef1234567890abcdef",
            "safe_value": 42,
        },
        "x402_private_key": "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    }

    sanitized, warnings = SecuritySanitizer.sanitize_data(raw_data)
    assert sanitized["api_key"] == "[REDACTED_CREDENTIAL]"
    assert sanitized["nested"]["password"] == "[REDACTED_CREDENTIAL]"
    assert sanitized["nested"]["token"] == "[REDACTED_CREDENTIAL]"
    assert sanitized["nested"]["safe_value"] == 42
    assert sanitized["x402_private_key"] == "[REDACTED_CREDENTIAL]"

    assert len(warnings) >= 4
    assert all("Sensitive credential omitted from package" in w for w in warnings)


def test_sanitizer_detects_secrets_in_strings():
    """Test detecting secrets embedded inside arbitrary string values."""
    secret_str = 'Bearer ghp_AbCdEfGhIjKlMnOpQrStUvWxYz0123456789'
    sanitized, warnings = SecuritySanitizer.sanitize_data(secret_str, current_key="header")
    assert sanitized == "[REDACTED_CREDENTIAL]"
    assert len(warnings) == 1
    assert "GitHub Token" in warnings[0]


def test_sanitizer_toon_text_redaction():
    """Test replacing credentials line-by-line in TOON structured text."""
    toon_text = (
        "project_id: rover-core\n"
        "api_key: sk-123456789012345678901234567890\n"
        "safe_config: true\n"
    )
    sanitized, warnings = SecuritySanitizer.sanitize_toon_text(toon_text, label="config.toon")
    assert "[REDACTED_CREDENTIAL]" in sanitized
    assert "sk-123456789012345678901234567890" not in sanitized
    assert "project_id: rover-core" in sanitized
    assert len(warnings) > 0
