"""Tests for database health and graph REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


def test_database_health_endpoint():
    """Test 26: GET /health/database returns status for SurrealDB and Qdrant."""
    client = TestClient(app)
    res = client.get("/health/database")
    assert res.status_code == 200
    data = res.json()
    assert "surrealdb" in data
    assert "qdrant" in data


def test_graph_endpoints():
    """Test 27-28: GET /api/graph/project/{id} and /api/graph/explorer/project/{id}."""
    client = TestClient(app)
    # Workline graph endpoint
    res = client.get("/api/graph/project/autonomous-rover")
    assert res.status_code == 200
    data = res.json()
    assert "nodes" in data
    assert "edges" in data

    # GraphExplorer legacy endpoint format compatibility
    res_exp = client.get("/api/graph/explorer/project/autonomous-rover")
    assert res_exp.status_code == 200
    data_exp = res_exp.json()
    assert "nodes" in data_exp
    assert "edges" in data_exp
