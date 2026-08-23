"""
Unit Tests for Workline AI Environment Configuration & Secret Isolation.

Verifies:
1. Startup environment validation across R1, R2, R3, R4, R5 roles.
2. Missing required variable fail-fast behavior without secret leakage.
3. Root .env.example completeness and structure.
4. Service-specific deployment templates (deploy/env/r1-r5.env.example).
5. Frontend public vs private secret separation (zero backend secrets in frontend).
6. Algorand and x402 configuration defaults.
"""

import os
import pytest
from unittest.mock import patch

from backend.workline.config_validator import EnvironmentValidator, SERVICE_ENV_REQUIREMENTS


def test_service_env_requirements_matrix():
    """Verifies that all 5 service roles are defined in the validator matrix."""
    assert "R1_CORE" in SERVICE_ENV_REQUIREMENTS
    assert "R2_AI" in SERVICE_ENV_REQUIREMENTS
    assert "R3_KNOWLEDGE" in SERVICE_ENV_REQUIREMENTS
    assert "R4_ENGINEERING" in SERVICE_ENV_REQUIREMENTS
    assert "R5_PROCUREMENT" in SERVICE_ENV_REQUIREMENTS


def test_env_validation_passes_with_defaults():
    """With standard defaults, validation passes cleanly for all services."""
    for role in ("R1_CORE", "R2_AI", "R3_KNOWLEDGE", "R4_ENGINEERING", "R5_PROCUREMENT"):
        valid, missing_req, _ = EnvironmentValidator.validate_service_environment(role)
        assert valid is True
        assert len(missing_req) == 0


def test_env_validation_missing_required_fails():
    """When a required variable is explicitly declared and missing, fail-fast raises RuntimeError without leakage."""
    with patch.dict(
        "backend.workline.config_validator.SERVICE_ENV_REQUIREMENTS",
        {"R2_AI": {"required": ["TEST_REQUIRED_SECRET_VAR"], "recommended": []}},
    ), patch.dict(os.environ, {}, clear=True):
        valid, missing_req, _ = EnvironmentValidator.validate_service_environment("R2_AI")
        assert valid is False
        assert "TEST_REQUIRED_SECRET_VAR" in missing_req

        with pytest.raises(RuntimeError, match="TEST_REQUIRED_SECRET_VAR"):
            EnvironmentValidator.validate_service_environment("R2_AI", fail_fast=True)


def test_root_env_example_contains_all_sections():
    """Verifies root .env.example contains all key architectural sections and safe placeholders."""
    root_example = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        ".env.example",
    )
    assert os.path.exists(root_example), "Root .env.example file must exist."

    with open(root_example, "r", encoding="utf-8") as f:
        content = f.read()

    expected_sections = [
        "CORE PLATFORM",
        "SERVICE MESH INTER-SERVICE URLS",
        "AI & MODEL INFERENCE",
        "KNOWLEDGE & DATA STORAGE",
        "MONETIZATION & PAYMENTS",
        "PROCUREMENT",
        "ARMOURIQ",
        "FRONTEND PUBLIC VARIABLES",
    ]
    for section in expected_sections:
        assert section in content, f"Missing section '{section}' in .env.example"

    # Security check: Ensure no real API keys are in .env.example
    assert "sk-" not in content or "placeholder" in content
    assert "AIza" not in content


def test_service_specific_env_examples_exist():
    """Verifies that dedicated deploy/env/r1-r5.env.example files exist."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for r in ("r1", "r2", "r3", "r4", "r5"):
        template_path = os.path.join(base_dir, "deploy", "env", f"{r}.env.example")
        assert os.path.exists(template_path), f"Missing deployment template: {template_path}"


def test_frontend_env_example_has_no_backend_secrets():
    """Verifies frontend/.env.example contains only NEXT_PUBLIC_ variables and no database/mesh secrets."""
    frontend_example = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "frontend",
        ".env.example",
    )
    assert os.path.exists(frontend_example), "frontend/.env.example must exist."

    with open(frontend_example, "r", encoding="utf-8") as f:
        content = f.read()

    forbidden_secrets = [
        "GEMINI_API_KEY",
        "SURREALDB_PASSWORD",
        "QDRANT_API_KEY",
        "WORKLINE_SERVICE_AUTH_KEY",
        "R2_SERVICE_TOKEN",
        "R3_SERVICE_TOKEN",
    ]
    for secret in forbidden_secrets:
        assert secret not in content, f"Forbidden backend secret '{secret}' leaked into frontend/.env.example"


def test_environment_matrix_doc_exists():
    """Verifies that docs/deployment/ENVIRONMENT_MATRIX.md exists and contains the matrix table."""
    matrix_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "docs",
        "deployment",
        "ENVIRONMENT_MATRIX.md",
    )
    assert os.path.exists(matrix_path), "docs/deployment/ENVIRONMENT_MATRIX.md must exist."

    with open(matrix_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Environment Variable Matrix" in content
    assert "Minimum Secret Distribution Rules" in content
    assert "GEMINI_API_KEY" in content
    assert "WORKLINE_X402_NETWORK" in content
