"""
Unit tests for AgentRouter and Agent37Adapter.
Verifies routing decisions, ArmorIQ delegation tracking, capability constraints,
and Agent37 isolated sandbox lifecycle.
"""

import pytest
from backend.workline.agents.router import (
    AgentRouter,
    AgentRuntimeType,
    DelegationRecord,
)
from backend.workline.agents.agent37_adapter import (
    Agent37Adapter,
    SandboxExecutionResult,
)


class TestAgentRouter:
    @pytest.fixture
    def router(self):
        return AgentRouter()

    def test_decide_runtime_local_for_sensitive(self, router):
        # Strict privacy / sensitive data always stays LOCAL
        runtime = router.decide_runtime(
            task_type="bom_analysis",
            task_prompt="Analyze proprietary power rail component selections",
            requires_web=True,
            is_sensitive=True,
        )
        assert runtime == AgentRuntimeType.LOCAL

    def test_decide_runtime_agent37_when_configured(self, router, monkeypatch):
        # Mock agent37 configuration
        monkeypatch.setattr(router.agent37, "is_configured", lambda: True)
        runtime = router.decide_runtime(
            task_type="web_research",
            task_prompt="Scrape datasheets from distributor portals",
            requires_web=True,
            is_sensitive=False,
        )
        assert runtime == AgentRuntimeType.AGENT37

    def test_decide_runtime_fallback_to_local_when_not_configured(self, router, monkeypatch):
        monkeypatch.setattr(router.agent37, "is_configured", lambda: False)
        runtime = router.decide_runtime(
            task_type="web_research",
            task_prompt="Search web for part replacements",
            requires_web=True,
            is_sensitive=False,
        )
        assert runtime == AgentRuntimeType.LOCAL

    def test_create_delegation_armoriq_token(self, router):
        record = router.create_delegation(
            agent_name="bom_optimizer",
            task_prompt="Optimize passive component sourcing",
            runtime=AgentRuntimeType.LOCAL,
            requester="engineer_alice",
        )
        assert isinstance(record, DelegationRecord)
        assert record.delegation_id.startswith("DEL-")
        assert record.runtime == AgentRuntimeType.LOCAL
        assert record.receipt_id is not None
        assert "bom_write" in record.denied_capabilities or "secret_access" in record.denied_capabilities

    def test_dispatch_pipeline_local(self, router):
        result = router.dispatch(
            task_type="bom_analysis",
            task_prompt="Assess single-source risks across active line items",
        )
        assert result["runtime"] == AgentRuntimeType.LOCAL
        assert result["status"] in ("EXECUTED", "COMPLETED")
        assert result["delegation_id"].startswith("DEL-")
        assert "requires_approval" in result


class TestAgent37Adapter:
    @pytest.fixture
    def adapter(self):
        return Agent37Adapter()

    def test_adapter_authentication_mock(self, adapter, monkeypatch):
        monkeypatch.delenv("AGENT37_API_KEY", raising=False)
        auth = adapter.authenticate()
        assert auth["status"] in ("LOCAL_MOCK", "AUTHENTICATED")

    def test_sandbox_provision_and_lifecycle(self, adapter):
        sandbox_id = adapter.provision_sandbox(
            delegation_id="DEL-2026-TEST1",
            agent_name="research_worker",
            capabilities=["browser", "web", "pdf_download"],
        )
        assert sandbox_id.startswith("sbx_")

        # Execute task in sandbox
        result = adapter.execute_in_sandbox(
            sandbox_id=sandbox_id,
            task_prompt="Query parametric resistor tolerances",
        )
        assert isinstance(result, SandboxExecutionResult)
        assert result.sandbox_id == sandbox_id
        assert result.status == "COMPLETED"
        assert result.delegation_id == "DEL-2026-TEST1"

        # Terminate sandbox
        terminated = adapter.terminate_sandbox(sandbox_id)
        assert terminated is True
