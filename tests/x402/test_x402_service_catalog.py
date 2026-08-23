"""
Unit tests for x402 Service Catalog, pricing invariants, and execution registry.
"""

import pytest
from backend.workline.x402.catalog import ServiceCatalog, service_catalog
from backend.workline.x402.config import x402_config


def test_service_catalog_initialization():
    """Verify that all 5 authoritative payable Workline services are registered with non-zero pricing."""
    catalog = ServiceCatalog()
    services = catalog.list_services()

    assert len(services) == 5
    service_ids = {s.id for s in services}
    expected_ids = {
        "bom.optimize",
        "component.analyze",
        "research.engineering",
        "simulation.thermal",
        "procurement.quote",
    }
    assert service_ids == expected_ids

    for service in services:
        assert service.price_usdc > 0
        assert service.asset == "USDC"
        assert service.asset_id in (31566704, 10458941)
        assert service.enabled is True
        assert service.endpoint.startswith("/api/x402/")


def test_service_catalog_lookup():
    """Test retrieving individual service definitions."""
    bom_service = service_catalog.get_service("bom.optimize")
    assert bom_service is not None
    assert bom_service.price_usdc == 0.50

    thermal_service = service_catalog.get_service("simulation.thermal")
    assert thermal_service is not None
    assert thermal_service.price_usdc == 0.75

    non_existent = service_catalog.get_service("non.existent.service")
    assert non_existent is None


@pytest.mark.asyncio
async def test_service_execution_dispatch():
    """Test executing a registered service handler."""
    catalog = ServiceCatalog()

    # Default fallback execution test
    result = await catalog.execute_service(
        "bom.optimize",
        {"project_id": "test_project", "bom_items": [{"ref": "U1", "part_number": "TPS62130"}]},
    )

    assert result["project_id"] == "test_project"
    assert result["optimization_status"] == "COMPLETED"
    assert "savings_ratio" in result
