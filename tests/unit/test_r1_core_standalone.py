import pytest
from httpx import AsyncClient, ASGITransport
from backend.services.core.main import app as r1_app


@pytest.mark.asyncio
async def test_r1_health_endpoint():
    """Verify R1 Core Gateway health check."""
    async with AsyncClient(transport=ASGITransport(app=r1_app), base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "workline-core-gateway"
        assert "downstream" in data


@pytest.mark.asyncio
async def test_r1_proxy_graceful_503_when_downstream_offline():
    """Verify R1 returns clean 503 instead of 500 when downstream is unreachable."""
    async with AsyncClient(transport=ASGITransport(app=r1_app), base_url="http://test") as client:
        # R2 proxy test
        r2_resp = await client.post("/api/proxy/ai/api/agents/run", json={"test": "data"})
        assert r2_resp.status_code == 503
        assert "R2 AI Service unavailable" in r2_resp.json()["detail"]

        # R3 proxy test
        r3_resp = await client.post("/api/proxy/knowledge/api/documents", json={"test": "data"})
        assert r3_resp.status_code == 503
        assert "R3 Knowledge Service unavailable" in r3_resp.json()["detail"]

        # R4 proxy test
        r4_resp = await client.post("/api/proxy/engineering/api/pcb/validate", json={"test": "data"})
        assert r4_resp.status_code == 503
        assert "R4 Engineering Service unavailable" in r4_resp.json()["detail"]

        # R5 proxy test
        r5_resp = await client.post("/api/proxy/procurement/api/procurement/search", json={"test": "data"})
        assert r5_resp.status_code == 503
        assert "R5 Procurement Service unavailable" in r5_resp.json()["detail"]


@pytest.mark.asyncio
async def test_r1_cors_and_404_handling():
    """Verify CORS headers and 404 response on unknown routes."""
    async with AsyncClient(transport=ASGITransport(app=r1_app), base_url="http://test") as client:
        # 404 check
        resp = await client.get("/api/unknown/route/not_found")
        assert resp.status_code == 404

        # Health check with CORS headers
        h_resp = await client.get("/health", headers={"Origin": "https://worklineai.netlify.app"})
        assert h_resp.status_code == 200
