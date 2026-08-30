"""
Unit tests for SupplierAdapter and MockDistributorAdapter (Sections 6 & 7).
"""

import pytest
from research_agents.bom_optimization_agent.adapters.mock_adapter import MockDistributorAdapter


@pytest.mark.asyncio
async def test_supplier_adapter_queries():
    robu = MockDistributorAdapter("SUPP-ROBU", "Robu.in", "Pune", "Maharashtra")
    mouser = MockDistributorAdapter("SUPP-MOUSER", "Mouser Electronics", "Bengaluru", "Karnataka")

    offers_robu = await robu.get_offers_for_bom_item("BOM-001", "900-13766-0000-000", "SBC", 1)
    assert len(offers_robu) >= 1
    assert offers_robu[0].supplier_id == "SUPP-ROBU"
    assert offers_robu[0].unit_price == 45000.0
    assert offers_robu[0].location.city == "Pune"
    assert offers_robu[0].stock_status == "in_stock"

    offers_mouser = await mouser.get_offers_for_bom_item("BOM-001", "900-13766-0000-000", "SBC", 1)
    assert len(offers_mouser) >= 1
    assert offers_mouser[0].supplier_id == "SUPP-MOUSER"
    assert offers_mouser[0].unit_price == 44200.0
