import pytest
from httpx import AsyncClient, ASGITransport

from backend.services.core.main import app as r1_app
from backend.services.ai.main import app as r2_app
from backend.services.knowledge.main import app as r3_app
from backend.services.engineering.main import app as r4_app
from backend.services.procurement.main import app as r5_app


# ==============================================================================
# 1. R1 Core Gateway Isolation
# ==============================================================================

@pytest.mark.asyncio
async def test_r1_core_health():
    """Verify R1 Core starts independently and serves /health."""
    async with AsyncClient(transport=ASGITransport(app=r1_app), base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "workline-core-gateway"


@pytest.mark.asyncio
async def test_r1_failure_isolation_graceful_503():
    """Verify R1 handles downstream service unavailability gracefully with 503 instead of crashing."""
    async with AsyncClient(transport=ASGITransport(app=r1_app), base_url="http://test") as client:
        # Proxy to nonexistent or down service
        resp = await client.post("/api/proxy/ai/api/research/query", json={"query": "test"})
        assert resp.status_code == 503
        assert "unavailable" in resp.json()["detail"].lower()


# ==============================================================================
# 2. R2 AI & Agents Isolation
# ==============================================================================

@pytest.mark.asyncio
async def test_r2_ai_health():
    """Verify R2 AI & Agents service starts independently and serves /health."""
    async with AsyncClient(transport=ASGITransport(app=r2_app), base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "workline-ai-agents"


# ==============================================================================
# 3. R3 Knowledge & Documents Isolation
# ==============================================================================

@pytest.mark.asyncio
async def test_r3_knowledge_health():
    """Verify R3 Knowledge & Documents service starts independently and serves /health."""
    async with AsyncClient(transport=ASGITransport(app=r3_app), base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "workline-knowledge-documents"


# ==============================================================================
# 4. R4 Engineering & Simulation Isolation
# ==============================================================================

@pytest.mark.asyncio
async def test_r4_engineering_health():
    """Verify R4 Engineering & Simulation service starts independently and serves /health."""
    async with AsyncClient(transport=ASGITransport(app=r4_app), base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "workline-engineering-simulation"


# ==============================================================================
# 5. R5 Procurement & Collaboration Isolation
# ==============================================================================

@pytest.mark.asyncio
async def test_r5_procurement_health():
    """Verify R5 Procurement & Collaboration service starts independently and serves /health."""
    async with AsyncClient(transport=ASGITransport(app=r5_app), base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "workline-procurement"
