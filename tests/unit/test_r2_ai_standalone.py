"""
Unit and Integration Tests for Workline R2 AI, Agents & Research Standalone Service.
Verifies health check, service token authentication, and controlled failure handling.
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
    """Verifies that R2 /health returns HTTP 200 with service metadata without external dependencies."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "workline-r2"
    assert data["version"] == "1.0.0-rc1"


def test_r2_service_token_auth_allowed_when_unset(client):
    """When WORKLINE_SERVICE_AUTH_KEY is unset/empty, internal endpoints allow requests."""
    with patch.dict(os.environ, {"WORKLINE_SERVICE_AUTH_KEY": ""}, clear=False):
        response = client.get("/api/cache/stats")
        # Should not be 401 Unauthorized
        assert response.status_code in [200, 404]


def test_r2_service_token_auth_enforced_when_set(client):
    """When WORKLINE_SERVICE_AUTH_KEY is set, requests without valid token return 401."""
    with patch("backend.r2.main.INTERNAL_SERVICE_TOKEN", "secret-test-token-12345"):
        # Without header -> 401
        response = client.post("/api/research", json={"intent": "test", "target_days": 10})
        assert response.status_code == 401

        # With invalid header -> 401
        response = client.post(
            "/api/research",
            json={"intent": "test", "target_days": 10},
            headers={"X-Workline-Service-Token": "wrong-token"},
        )
        assert response.status_code == 401

        # With valid header -> accepted through auth layer
        with patch("backend.routes.research.run_agent_pipeline") as mock_pipeline:
            mock_pipeline.return_value = {"status": "success", "intent": "test"}
            response = client.post(
                "/api/research",
                json={"intent": "test", "target_days": 10},
                headers={"X-Workline-Service-Token": "secret-test-token-12345"},
            )
            assert response.status_code == 200
