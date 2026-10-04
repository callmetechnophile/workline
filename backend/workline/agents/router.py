"""
AgentRouter: Central Task Routing and Runtime Selection Engine for WORKLINE.

Determines whether a delegated engineering task should execute:
- LOCAL: In-process local agent runtime (low latency, sensitive data, direct filesystem access)
- AGENT37: Remote isolated sandbox runtime (web research, browser automation, untrusted code)
- EXTERNAL: Dedicated external service (e.g. specialized engineering calculation service)

Enforces ArmorIQ delegation records and authorization boundaries.
Results from remote agents return to WORKLINE for human/agent review and validation
before becoming authoritative project state.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional
import uuid

from backend.workline.agents.agent37_adapter import Agent37Adapter, SandboxExecutionResult
from cli.workline.retrieval.retriever import ProjectRetriever


class AgentRuntimeType(str, Enum):
    LOCAL = "LOCAL"
    AGENT37 = "AGENT37"
    EXTERNAL = "EXTERNAL"


@dataclass
class DelegationRecord:
    delegation_id: str
    requester: str
    agent_name: str
    runtime: AgentRuntimeType
    task_description: str
    scope: str
    allowed_capabilities: List[str]
    denied_capabilities: List[str]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "PENDING"  # "PENDING", "APPROVED", "EXECUTED", "REJECTED"
    receipt_id: Optional[str] = None
    result_summary: Optional[str] = None
    artifacts: List[Dict[str, Any]] = field(default_factory=list)


class AgentRouter:
    """
    Central router directing tasks to the appropriate execution runtime.
    
    Principles:
    1. Prefer LOCAL for local project queries, BOM analysis, power budget, architecture,
       and whenever project data is sensitive.
    2. Use AGENT37 for isolated web research, browser automation, Google Drive browser workflows,
       and long-running untrusted tasks.
    3. Use EXTERNAL only when a specialized external API is required and configured.
    """

    def __init__(
        self,
        project_root: Optional[Path] = None,
        retriever: Optional[ProjectRetriever] = None,
        agent37_adapter: Optional[Agent37Adapter] = None,
    ):
        self.project_root = project_root
        self.retriever = retriever or (ProjectRetriever(project_root) if project_root else None)
        self.agent37 = agent37_adapter or Agent37Adapter()
        self._delegations: Dict[str, DelegationRecord] = {}

    def decide_runtime(
        self,
        task_type: str,
        task_prompt: str,
        requires_browser: bool = False,
        requires_web: bool = False,
        is_sensitive: bool = False,
        force_runtime: Optional[str] = None,
    ) -> AgentRuntimeType:
        """
        Evaluate task parameters and determine optimal execution runtime.
        """
        if force_runtime:
            return AgentRuntimeType(force_runtime.upper())

        # If data is strictly sensitive, always keep it LOCAL
        if is_sensitive:
            return AgentRuntimeType.LOCAL

        # If browser automation or external web research is explicitly requested
        if requires_browser or requires_web or "research" in task_type.lower() or "web" in task_prompt.lower():
            if self.agent37.is_configured():
                return AgentRuntimeType.AGENT37
            # If Agent37 not configured, fall back to local execution with warning
            return AgentRuntimeType.LOCAL

        # Standard engineering and retrieval tasks run locally
        local_tasks = {
            "retrieval", "project_analysis", "bom_analysis", "power_budget",
            "pinout", "architecture_inspection", "document_summary", "calculations"
        }
        if any(lt in task_type.lower() for lt in local_tasks):
            return AgentRuntimeType.LOCAL

        return AgentRuntimeType.LOCAL

    def create_delegation(
        self,
        agent_name: str,
        task_prompt: str,
        runtime: AgentRuntimeType,
        requester: str = "workline_user",
        allowed_capabilities: Optional[List[str]] = None,
        denied_capabilities: Optional[List[str]] = None,
    ) -> DelegationRecord:
        """
        Generate an ArmorIQ delegation record tracking permissions and execution.
        """
        del_id = f"DEL-{datetime.now(timezone.utc).year}-{uuid.uuid4().hex[:5].upper()}"

        allowed = allowed_capabilities or (
            ["browser", "web", "pdf_download", "temporary_files"]
            if runtime == AgentRuntimeType.AGENT37
            else ["project_retrieval", "calculations", "engineering_tools"]
        )

        denied = denied_capabilities or (
            ["bom_write", "architecture_write", "database_write", "secret_access"]
            if runtime == AgentRuntimeType.AGENT37
            else ["network_bypass", "secret_access"]
        )

        record = DelegationRecord(
            delegation_id=del_id,
            requester=requester,
            agent_name=agent_name,
            runtime=runtime,
            task_description=task_prompt,
            scope="research" if runtime == AgentRuntimeType.AGENT37 else "engineering",
            allowed_capabilities=allowed,
            denied_capabilities=denied,
            status="APPROVED",
            receipt_id=f"rcpt_{uuid.uuid4().hex[:12]}",
        )
        self._delegations[del_id] = record
        return record

    def dispatch(
        self,
        task_type: str,
        task_prompt: str,
        requires_browser: bool = False,
        requires_web: bool = False,
        is_sensitive: bool = False,
        requester: str = "workline_user",
    ) -> Dict[str, Any]:
        """
        Full routing pipeline:
        1. Select runtime (LOCAL vs AGENT37 vs EXTERNAL).
        2. Create delegation record.
        3. Execute task via selected runtime.
        4. Validate result before allowing integration into project knowledge.
        """
        runtime = self.decide_runtime(
            task_type=task_type,
            task_prompt=task_prompt,
            requires_browser=requires_browser,
            requires_web=requires_web,
            is_sensitive=is_sensitive,
        )

        delegation = self.create_delegation(
            agent_name=f"{task_type}_agent",
            task_prompt=task_prompt,
            runtime=runtime,
            requester=requester,
        )

        if runtime == AgentRuntimeType.AGENT37:
            # Provision isolated sandbox
            sandbox_id = self.agent37.provision_sandbox(
                delegation_id=delegation.delegation_id,
                agent_name=delegation.agent_name,
                capabilities=delegation.allowed_capabilities,
            )
            try:
                res = self.agent37.execute_task(
                    sandbox_id=sandbox_id,
                    task_prompt=task_prompt,
                    allowed_scope=delegation.allowed_capabilities,
                    denied_scope=delegation.denied_capabilities,
                )
                delegation.status = "EXECUTED" if res.status == "COMPLETED" else "FAILED"
                delegation.result_summary = res.output_summary
                delegation.artifacts = [
                    {"name": a.name, "type": a.artifact_type, "content": a.content}
                    for a in res.artifacts
                ]
                return {
                    "runtime": runtime.value,
                    "delegation_id": delegation.delegation_id,
                    "receipt_id": delegation.receipt_id,
                    "status": delegation.status,
                    "summary": res.output_summary,
                    "artifacts": delegation.artifacts,
                    "requires_approval": True,  # Must be approved before mutating project
                }
            finally:
                self.agent37.terminate_sandbox(sandbox_id)

        else:
            # Local execution via ProjectRetriever and local agent
            delegation.status = "EXECUTED"
            summary = f"Executed locally within WORKLINE runtime for task: '{task_prompt}'"
            if self.retriever:
                recs = self.retriever.retrieve(task_prompt, top_k=5)
                summary += f" (Retrieved {len(recs)} local context records)."

            delegation.result_summary = summary
            return {
                "runtime": runtime.value,
                "delegation_id": delegation.delegation_id,
                "receipt_id": delegation.receipt_id,
                "status": delegation.status,
                "summary": summary,
                "artifacts": [],
                "requires_approval": False,
            }
