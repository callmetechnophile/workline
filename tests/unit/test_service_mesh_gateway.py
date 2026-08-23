"""
Unit and Integration Tests for R1 Gateway Service Mesh, Authenticated Routing,
ArmourIQ Policy Evaluation, and Inter-Service Client.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.core.main import app as r1_core_app
from backend.workline.armouriq.capabilities import AgentCapability, RiskTier
from backend.workline.armouriq.trust_context import TrustContext
from backend.workline.mesh.client import ServiceMeshClient
from backend.workline.mesh.gateway import (
    SERVICE_AUTH_KEY,
    ServiceMeshGateway,
    ServiceMeshRequest,
    ServiceMeshResponse,
)


@pytest.mark.asyncio
async def test_mesh_invalid_service_token_denied():
    """Verify that inter-service requests with invalid service tokens are rejected with 401."""
    context = TrustContext(
        session_id="sess_mesh_01",
        project_id="proj_mesh_test",
        agent_id="workline.research_agent",
        capabilities=[AgentCapability.READ_RESEARCH, AgentCapability.READ_KNOWLEDGE],
    )
    req = ServiceMeshRequest(
        source_service="R2_AI",
        target_service="R3",
        action="knowledge.search",
        path="/api/knowledge/search",
        payload={"query": "buck converter"},
        context=context,
    )
    # Dispatch with bad token
    res = await ServiceMeshGateway.dispatch(req, service_token="invalid-forged-token")
    assert res.status_code == 401
    assert "Invalid internal service mesh" in res.error


@pytest.mark.asyncio
async def test_mesh_missing_project_context_denied():
    """Verify that requests lacking valid project context are rejected with 403."""
    context = TrustContext(
        session_id="sess_mesh_02",
        project_id="",  # Missing project
        agent_id="workline.research_agent",
        capabilities=[AgentCapability.READ_RESEARCH],
    )
    req = ServiceMeshRequest(
        source_service="R2_AI",
        target_service="R3",
        action="knowledge.search",
        path="/api/knowledge/search",
        payload={"query": "thermal dissipation"},
        context=context,
    )
    res = await ServiceMeshGateway.dispatch(req, service_token=SERVICE_AUTH_KEY)
    assert res.status_code == 403
    assert "Missing or invalid project_id" in res.error


@pytest.mark.asyncio
async def test_mesh_unauthorized_action_blocked_by_armouriq():
    """Verify that R2 attempting an unauthorized action (e.g. procurement order) is blocked by ArmourIQ."""
    context = TrustContext(
        session_id="sess_mesh_03",
        project_id="proj_mesh_test",
        agent_id="workline.research_agent",
        capabilities=[AgentCapability.READ_RESEARCH, AgentCapability.READ_KNOWLEDGE],  # Lacks EXECUTE_PROCUREMENT
    )
    req = ServiceMeshRequest(
        source_service="R2_AI",
        target_service="R5",
        action="procurement.order",
        path="/api/orders/execute",
        payload={"order_id": "ord_123"},
        context=context,
    )
    res = await ServiceMeshGateway.dispatch(req, service_token=SERVICE_AUTH_KEY)
    assert res.status_code == 403
    assert "ArmourIQ Policy Violation" in res.error


@pytest.mark.asyncio
async def test_mesh_downstream_unavailable_returns_graceful_503():
    """Verify that when a downstream service is offline, R1 returns a structured 503 instead of crashing."""
    context = TrustContext(
        session_id="sess_mesh_04",
        project_id="proj_mesh_test",
        agent_id="workline.research_agent",
        capabilities=[AgentCapability.READ_RESEARCH, AgentCapability.READ_KNOWLEDGE],
    )
    # Target R3 with dummy offline port
    req = ServiceMeshRequest(
        source_service="R2_AI",
        target_service="R3",
        action="knowledge.search",
        path="/api/knowledge/search",
        payload={"query": "test"},
        context=context,
    )
    # With R3 offline in local unit test environment
    res = await ServiceMeshGateway.dispatch(req, service_token=SERVICE_AUTH_KEY)
    assert res.status_code == 503
    assert "Service Mesh Error: Target microservice 'R3' unavailable" in res.error
    assert res.target_service == "R3"


@pytest.mark.asyncio
async def test_service_mesh_client_r2_to_r3_query():
    """Verify ServiceMeshClient helper method construction for R2 -> R1 -> R3."""
    client = ServiceMeshClient(source_service_id="R2_AI")
    context = TrustContext(
        session_id="sess_mesh_05",
        project_id="proj_mesh_test",
        agent_id="workline.research_agent",
        capabilities=[AgentCapability.READ_RESEARCH, AgentCapability.READ_KNOWLEDGE],
    )
    res = await client.r2_query_r3_knowledge(context, query="MOSFET switching", limit=3)
    assert res.target_service == "R3"
    assert res.request_id == context.request_id


@pytest.mark.asyncio
async def test_service_mesh_client_r2_to_r4_simulation():
    """Verify ServiceMeshClient helper method for R2 -> R1 -> R4."""
    client = ServiceMeshClient(source_service_id="R2_AI")
    context = TrustContext(
        session_id="sess_mesh_06",
        project_id="proj_mesh_test",
        agent_id="workline.builder_agent",
        capabilities=[AgentCapability.VALIDATE_PCB, AgentCapability.RUN_SIMULATION],
    )
    res = await client.r2_request_r4_simulation(context, pcb_id="pcb_alpha_01")
    assert res.target_service == "R4"


@pytest.mark.asyncio
async def test_service_mesh_client_r2_to_r5_procurement():
    """Verify ServiceMeshClient helper method for R2 -> R1 -> R5."""
    client = ServiceMeshClient(source_service_id="R2_AI")
    context = TrustContext(
        session_id="sess_mesh_07",
        project_id="proj_mesh_test",
        agent_id="workline.bom_agent",
        capabilities=[AgentCapability.LOOKUP_COMPONENT, AgentCapability.OPTIMIZE_BOM],
    )
    res = await client.r2_query_r5_procurement(context, query="TPS62130")
    assert res.target_service == "R5"


@pytest.mark.asyncio
async def test_r1_cluster_health_check():
    """Verify R1 cluster health endpoint returns real downstream health checks."""
    client = TestClient(app)
    resp = client.get("/health/cluster")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "downstream_services" in data
    assert "R2" in data["downstream_services"]
    assert "R3" in data["downstream_services"]
    assert "R4" in data["downstream_services"]
    assert "R5" in data["downstream_services"]
