"""
Unit and Integration Tests for Workline R3 Knowledge Infrastructure Standalone Service.
Verifies health check, Bearer service token authentication, Qdrant/SurrealDB operations, and error handling.
"""

import pytest
from fastapi.testclient import TestClient
import os
from unittest.mock import patch, MagicMock, AsyncMock

from backend.r3.main import app


@pytest.fixture
def client():
    """Provides TestClient for R3 FastAPI application."""
    return TestClient(app)


def test_r3_health_endpoint(client):
    """Verifies that R3 /health returns HTTP 200 with database status without external dependencies."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "workline-r3"
    assert data["version"] == "1.0.0-rc1"
    assert "databases" in data
    assert "surrealdb" in data["databases"]
    assert "qdrant" in data["databases"]


def test_r3_search_unauthorized_without_token(client):
    """Verifies that POST /internal/knowledge/search returns 401 when no token is provided."""
    with patch("backend.r3.main.R3_SERVICE_TOKEN", "r3-secret-token-12345"):
        response = client.post("/internal/knowledge/search", json={"query": "Buck Converter", "limit": 5})
        assert response.status_code == 401
        assert "Unauthorized" in response.json()["detail"]


def test_r3_search_unauthorized_with_invalid_token(client):
    """Verifies that POST /internal/knowledge/search returns 401 with invalid Bearer token."""
    with patch("backend.r3.main.R3_SERVICE_TOKEN", "r3-secret-token-12345"):
        response = client.post(
            "/internal/knowledge/search",
            json={"query": "Buck Converter", "limit": 5},
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401


def test_r3_search_authorized_with_valid_bearer_token(client):
    """Verifies that POST /internal/knowledge/search succeeds with valid Bearer token."""
    with patch("backend.r3.main.R3_SERVICE_TOKEN", "r3-secret-token-12345"):
        with patch("backend.r3.main.qdrant_manager.search") as mock_search:
            mock_search.return_value = [
                {"id": "doc_1", "score": 0.95, "payload": {"name": "LM2596 Buck Regulator"}}
            ]
            response = client.post(
                "/internal/knowledge/search",
                json={"query": "LM2596", "limit": 5},
                headers={
                    "Authorization": "Bearer r3-secret-token-12345",
                    "X-Request-ID": "req-trace-r3-001"
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data["query"] == "LM2596"
            assert data["count"] == 1
            assert data["results"][0]["id"] == "doc_1"


def test_r3_search_empty_query_returns_422(client):
    """Verifies that POST /internal/knowledge/search returns 422 when query is empty."""
    with patch("backend.r3.main.R3_SERVICE_TOKEN", "r3-secret-token-12345"):
        response = client.post(
            "/internal/knowledge/search",
            json={"query": "   ", "limit": 5},
            headers={"Authorization": "Bearer r3-secret-token-12345"},
        )
        assert response.status_code == 422


def test_r3_graph_query_authorized(client):
    """Verifies that POST /internal/graph/query executes SurrealDB queries."""
    with patch("backend.r3.main.R3_SERVICE_TOKEN", "r3-secret-token-12345"):
        with patch("backend.r3.main.surreal_db.query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = [{"id": "node_1", "type": "component"}]
            response = client.post(
                "/internal/graph/query",
                json={"query": "SELECT * FROM component"},
                headers={"Authorization": "Bearer r3-secret-token-12345"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["query"] == "SELECT * FROM component"
            assert len(data["result"]) == 1


def test_r3_index_document_authorized(client):
    """Verifies that POST /internal/knowledge/index ingests documents."""
    with patch("backend.r3.main.R3_SERVICE_TOKEN", "r3-secret-token-12345"):
        response = client.post(
            "/internal/knowledge/index",
            json={
                "document_id": "doc_stm32_datasheet",
                "content": "STM32F401 ARM Cortex-M4 Microcontroller with FPU",
                "metadata": {"category": "MCU"}
            },
            headers={"Authorization": "Bearer r3-secret-token-12345"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "indexed"
        assert data["document_id"] == "doc_stm32_datasheet"
