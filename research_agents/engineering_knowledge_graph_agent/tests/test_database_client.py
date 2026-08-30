"""
Unit tests for SurrealDB client and in-memory graph repository (Sections 4, 84, 85).
"""

import pytest
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient


@pytest.mark.asyncio
async def test_database_client_lifecycle_and_crud():
    client = SurrealDBClient()
    connected = await client.connect()
    assert connected is True

    health = await client.health_check()
    assert health["status"] == "healthy"

    # Create node
    node = await client.create_node("component", "500-0771-01", {"part_number": "500-0771-01", "name": "FLIR Lepton"})
    assert node["id"] == "component:500-0771-01"

    # Upsert node
    updated_node, is_new = await client.upsert_node("component", "500-0771-01", {"manufacturer": "Teledyne FLIR"})
    assert is_new is False
    assert updated_node["manufacturer"] == "Teledyne FLIR"

    # Relate nodes
    edge = await client.relate_nodes("subsystem:Thermal", "USES", "component:500-0771-01")
    assert edge.relation_type == "USES"

    outbound = await client.get_outbound("subsystem:Thermal")
    assert len(outbound) == 1
    assert outbound[0].target_id == "component:500-0771-01"


@pytest.mark.asyncio
async def test_database_client_simulated_failure():
    client_fail = SurrealDBClient(simulate_failure=True)
    health = await client_fail.health_check()
    assert health["status"] == "unhealthy"

    with pytest.raises(RuntimeError, match="DATABASE_UNAVAILABLE"):
        await client_fail.create_node("project", "p1", {"name": "Test"})
