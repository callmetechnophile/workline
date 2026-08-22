"""
Unit and Integration Tests for Workline R2 AI, Agents & Research Standalone Service.
Verifies health check, Bearer service token authentication, POST /internal/research, and controlled error handling.
"""

import pytest
from fastapi.testclient import TestClient
import os
from unittest.mock import patch

from backend.r2.main import app


@pytest.fixture
def client():
    """Provides TestClient for R2 FastAPI application."""
    return TestClient(app)


def test_r2_health_endpoint(client):
    """Verifies that R2 /health returns HTTP 200 without requiring authentication or external services."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "workline-r2"
    assert data["version"] == "1.0.0-rc1"


def test_internal_research_unauthorized_without_token(client):
    """Verifies that POST /internal/research returns 401 when no token is provided."""
    with patch("backend.r2.main.R2_SERVICE_TOKEN", "prod-secret-token-xyz"):
        response = client.post("/internal/research", json={"intent": "Autonomous Drone", "target_days": 14})
        assert response.status_code == 401
        assert "Unauthorized" in response.json()["detail"]


def test_internal_research_unauthorized_with_invalid_token(client):
    """Verifies that POST /internal/research returns 401 with invalid Bearer token."""
    with patch("backend.r2.main.R2_SERVICE_TOKEN", "prod-secret-token-xyz"):
        response = client.post(
            "/internal/research",
            json={"intent": "Autonomous Drone", "target_days": 14},
            headers={"Authorization": "Bearer wrong-token-123"},
        )
        assert response.status_code == 401


def test_internal_research_authorized_with_valid_bearer_token(client):
    """Verifies that POST /internal/research succeeds with valid Authorization: Bearer token."""
    with patch("backend.r2.main.R2_SERVICE_TOKEN", "prod-secret-token-xyz"):
        with patch("backend.r2.main.run_engineering_pipeline") as mock_pipeline:
            mock_pipeline.return_value = {
                "intent": "Autonomous Drone",
                "components": [{"name": "ESC 40A", "part_number": "ESC-40A"}],
                "projects": [],
                "papers": [],
                "paper_summary": {"key_takeaways": "High efficiency MOSFETs recommended"},
                "validation": {"readiness_score": 92, "risk_score": 8},
                "optimization": {"bom_cost_reduction": "15%"},
                "roadmap": [],
                "gantt": [],
                "exports": {},
                "decision_trace": [],
                "audit_trail": [],
                "blocked_test_success": True
            }
            response = client.post(
                "/internal/research",
                json={"intent": "Autonomous Drone", "target_days": 14},
                headers={
                    "Authorization": "Bearer prod-secret-token-xyz",
                    "X-Request-ID": "req-trace-test-001"
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data["intent"] == "Autonomous Drone"
            assert data["validation"]["readiness_score"] == 92
            assert data["blocked_test_success"] is True


def test_internal_research_empty_intent_returns_422(client):
    """Verifies that POST /internal/research returns 422 Unprocessable Entity when intent is empty."""
    with patch("backend.r2.main.R2_SERVICE_TOKEN", "prod-secret-token-xyz"):
        response = client.post(
            "/internal/research",
            json={"intent": "   ", "target_days": 14},
            headers={"Authorization": "Bearer prod-secret-token-xyz"},
        )
        assert response.status_code == 422


def test_internal_research_pipeline_failure_returns_controlled_500(client):
    """Verifies that unexpected pipeline errors return controlled 500 without leaking secrets."""
    with patch("backend.r2.main.R2_SERVICE_TOKEN", "prod-secret-token-xyz"):
        with patch("backend.r2.main.run_engineering_pipeline", side_effect=RuntimeError("LLM API Timeout")):
            response = client.post(
                "/internal/research",
                json={"intent": "Smart Irrigation Node", "target_days": 7},
                headers={"Authorization": "Bearer prod-secret-token-xyz"},
            )
            assert response.status_code == 500
            assert response.json()["detail"] == "Internal research pipeline execution failed"
