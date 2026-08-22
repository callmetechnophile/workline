import pytest
from httpx import AsyncClient, ASGITransport
from backend.services.procurement.main import app


@pytest.mark.asyncio
async def test_procurement_service_health():
    """Test standalone R5 health endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "workline-procurement"


@pytest.mark.asyncio
async def test_procurement_service_bom_endpoint():
    """Test standalone BOM retrieval on R5."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/bom")
        assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_procurement_service_search_endpoint():
    """Test standalone procurement component search."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/procurement/search", json={"query": "TPS62130", "limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert "candidates" in data
