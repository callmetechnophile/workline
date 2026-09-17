"""
Comprehensive Platform End-to-End Integration Tests.
Validates:
1. Environment & Configuration loading
2. Central clients (SurrealDB fallback, Bedrock, ArmorIQ)
3. Authoritative Agent Registry (all 27 agents registered & importable)
4. Capability routing & dynamic dispatch (Control Fabric)
5. Google ADK task execution & result retrieval
6. A2A & Bindu interoperability layer
7. External research services (Tavily, FreePHDLabor, Anakin)
8. Multi-agent collaborative workflow (Agent #24 Manufacturing -> Agent #26 Deployment -> Agent #27 Documentation)
9. Platform Evaluation Harness execution
"""

import pytest
import asyncio
from armourflow.config import get_settings, ConfigurationValidator
from armourflow.data import get_database_client
from armourflow.models import get_model_provider
from armourflow.security import get_security_boundary
from armourflow.registry import get_agent_registry
from armourflow.fabric import get_control_fabric, CapabilityRouter, TaskState
from armourflow.adk import get_adk_runtime
from armourflow.interop import A2AInteroperabilityBridge, BinduExternalAdapter
from armourflow.external import CentralTavilyClient, CentralFreePHDLaborClient, CentralAnakinClient
from armourflow.evals import get_evaluation_harness


def test_platform_settings_and_diagnostics():
    """Verify settings loaded without secret leakage and diagnostics pass."""
    settings = get_settings()
    assert settings.app_name == "ArmourFlow AI"
    assert settings.app_version == "1.0.0"
    
    validator = ConfigurationValidator()
    checks = validator.run_diagnostics()
    assert len(checks) >= 12
    # Ensure no secrets leak in diagnostic outputs
    text = str([c.model_dump() for c in checks])
    assert "sk-" not in text
    assert "aws_secret" not in text.lower()


def test_central_services_initialization():
    """Verify central service clients initialize cleanly."""
    db = get_database_client()
    assert db is not None

    bedrock = get_model_provider()
    assert bedrock.region == "us-east-1"

    armoriq = get_security_boundary()
    authorized, _ = armoriq.authorize("TechDocAgent", "create_document", "default")
    assert authorized is True
    # Test multi-tenant isolation enforcement
    denied, reason = armoriq.authorize("TechDocAgent", "create_document", "default", unauthorized_access=True)
    assert denied is False
    assert "PROJECT_ACCESS_DENIED" in reason


def test_authoritative_agent_registry_27_agents():
    """Verify all 27 agents are registered and healthy."""
    reg = get_agent_registry()
    agents = reg.list_agents()
    assert len(agents) == 27, f"Expected 27 agents, got {len(agents)}"

    for a in agents:
        health = reg.check_health(a.agent_id)
        assert health["importable"] is True, f"Agent {a.agent_id} ({a.name}) failed import: {health.get('error')}"
        assert health["status"] == "HEALTHY"


@pytest.mark.asyncio
async def test_capability_routing_and_fabric_execution():
    """Verify capability-based task routing through the Control Fabric."""
    fabric = get_control_fabric()
    
    # Route via capability 'dfm_analysis' -> Agent 24
    task = await fabric.submit_task(
        payload={"action": "dfm_analysis", "components": []},
        target_capability="dfm_analysis",
        project_id="test-proj-01",
    )
    assert task.state == TaskState.COMPLETED
    assert task.target_agent_id == "agent.24"
    assert task.result is not None
    assert task.result.get("status") == "success"


@pytest.mark.asyncio
async def test_google_adk_runtime_delegation():
    """Verify Google ADK runtime delegates execution to Control Fabric."""
    adk = get_adk_runtime()
    
    # Execute document generation task via ADK
    result = await adk.run(
        task_name="list_documents",
        parameters={"operation": "list_documents", "project_id": "test-proj-adk"},
        project_id="test-proj-adk",
        agent_id="agent.27",
    )
    assert result.get("state") == "COMPLETED"
    assert result.get("adk_status") == "SUCCESS"
    assert result.get("result", {}).get("status") == "ok"


@pytest.mark.asyncio
async def test_a2a_and_bindu_interoperability():
    """Verify A2A message formatting and Bindu identity discovery."""
    a2a = A2AInteroperabilityBridge()
    msg = a2a.format_message(
        source_agent_id="agent.24",
        target_agent_id="agent.26",
        action="handoff_readiness",
        payload={"readiness_verdict": "PROTOTYPE_READY"},
    )
    assert msg["source_agent_id"] == "agent.24"
    assert msg["target_agent_id"] == "agent.26"
    assert msg["action"] == "handoff_readiness"

    bindu = BinduExternalAdapter()
    h = bindu.health_check()
    assert h["status"] in ("HEALTHY", "DISABLED")


@pytest.mark.asyncio
async def test_external_services_graceful_fallbacks():
    """Verify external research services execute without crashing when offline."""
    tavily = CentralTavilyClient()
    res_t = await tavily.search("DIN EN ISO 2768 manufacturing standards")
    assert isinstance(res_t, list)
    assert len(res_t) > 0

    phd = CentralFreePHDLaborClient()
    res_p = await phd.search_papers("titanium additive manufacturing residual stress")
    assert isinstance(res_p, list)
    assert len(res_p) > 0

    anakin = CentralAnakinClient()
    h_a = anakin.health_check()
    assert h_a["status"] == "DISABLED"


@pytest.mark.asyncio
async def test_multi_agent_collaborative_workflow():
    """
    Test end-to-end multi-agent pipeline:
    Agent #24 (Manufacturing/DFM) -> Agent #26 (Deployment/Ops) -> Agent #27 (Technical Documentation).
    State is persisted to graph/database at each stage.
    """
    fabric = get_control_fabric()
    project_id = "E2E-WORKFLOW-PROJ"

    # Step 1: Run Manufacturing DFM Analysis (Agent #24)
    task_mfg = await fabric.submit_task(
        payload={
            "action": "dfm_analysis",
            "project_id": project_id,
            "components": [
                {
                    "component_id": "CHASSIS-E2E-01",
                    "intended_process": "CNC_MACHINING",
                    "pocket_depth_mm": 20.0,
                    "pocket_corner_radius_mm": 5.0,
                }
            ],
        },
        target_agent_id="agent.24",
        project_id=project_id,
    )
    assert task_mfg.state == TaskState.COMPLETED
    readiness_verdict = task_mfg.result.get("readiness", {}).get("verdict", "UNKNOWN")
    assert readiness_verdict in ("PROTOTYPE_READY", "PRODUCTION_READY", "CONDITIONAL_APPROVAL")

    # Step 2: Handoff DFM readiness to Deployment & Operations (Agent #26)
    task_ops = await fabric.submit_task(
        payload={
            "project_id": project_id,
            "system_id": "SYS-E2E-01",
            "dfm_handoff": {"readiness_score": 0.88, "verdict": readiness_verdict},
            "commissioning_steps": [{"step_number": 1, "description": "Power-on self test"}],
        },
        target_agent_id="agent.26",
        project_id=project_id,
    )
    assert task_ops.state == TaskState.COMPLETED
    assert task_ops.result.get("status") == "success"

    # Step 3: Formalize documentation and publication record (Agent #27)
    task_doc = await fabric.submit_task(
        payload={
            "project_id": project_id,
            "operation": "create_document",
            "user_id": "lead.engineer",
            "document_type": "MANUFACTURING_READINESS_REPORT",
            "title": "E2E Platform Manufacturing and Deployment Gate Summary",
            "content": f"Verdict: {readiness_verdict}. Commissioning planned successfully.",
        },
        target_agent_id="agent.27",
        project_id=project_id,
    )
    assert task_doc.state == TaskState.COMPLETED
    assert task_doc.result.get("status") == "ok"
    assert task_doc.result.get("document", {}).get("status") == "DRAFT"


@pytest.mark.asyncio
async def test_platform_evaluation_harness():
    """Verify evaluation harness completes 15/15 benchmarks with 100% pass rate."""
    harness = get_evaluation_harness()
    report = await harness.run_platform_benchmarks()
    assert report.total_agents_evaluated >= 3
    assert report.total_benchmarks == 15
    assert report.total_passed == 15
    assert report.overall_pass_rate == 100.0
