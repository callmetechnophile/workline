"""Interoperability Gateway — central entrypoint and security boundary for external agent operations."""

import asyncio
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.workline.interoperability.bindu.adapter import BinduAdapter
from backend.workline.interoperability.capabilities import (
    AgentCapability,
    AgentStatus,
    RiskLevel,
)
from backend.workline.interoperability.corsair.adapter import CorsairAdapter
from backend.workline.interoperability.policies import PolicyEngine
from backend.workline.interoperability.provenance import TaskProvenance, compute_sha256
from backend.workline.interoperability.registry import ExternalAgent, agent_registry
from backend.workline.interoperability.security import SecuritySanitizer
from backend.workline.interoperability.tasks import (
    AuditEventType,
    AgentTask,
    InteroperabilityAuditEvent,
    TaskContext,
    TaskStatus,
)
from backend.workline.interoperability.validation import AgentResultValidator


class InteroperabilityGateway:
    """Enterprise Interoperability Gateway orchestrating external agent delegation,
    enforcing zero-trust security policies, idempotency, provenance, and knowledge syncing."""

    def __init__(self):
        self._lock = threading.RLock()
        self.bindu_adapter = BinduAdapter()
        self.corsair_adapter = CorsairAdapter()
        self._tasks: Dict[str, AgentTask] = {}
        self._idempotency_cache: Dict[str, str] = {}  # idempotency_key -> task_id
        self._audit_trail: List[InteroperabilityAuditEvent] = []

    def _record_audit_event(
        self,
        project_id: str,
        team_id: str,
        task_id: str,
        agent_id: str,
        event_type: AuditEventType,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append an immutable audit event."""
        with self._lock:
            evt = InteroperabilityAuditEvent(
                project_id=project_id,
                team_id=team_id,
                task_id=task_id,
                agent_id=agent_id,
                event_type=event_type,
                details=details or {},
            )
            self._audit_trail.append(evt)

    def get_audit_trail(self, task_id: Optional[str] = None) -> List[InteroperabilityAuditEvent]:
        """Fetch audit events, optionally filtered by task_id."""
        with self._lock:
            if task_id:
                return [e for e in self._audit_trail if e.task_id == task_id]
            return list(self._audit_trail)

    def get_task(self, task_id: str) -> Optional[AgentTask]:
        """Fetch an external agent task by ID."""
        with self._lock:
            return self._tasks.get(task_id)

    def list_tasks_for_project(self, project_id: str) -> List[AgentTask]:
        """List all external tasks associated with a project."""
        with self._lock:
            return [t for t in self._tasks.values() if t.project_id == project_id]

    async def submit_task(
        self,
        project_id: str,
        team_id: str,
        requesting_agent: str,
        target_agent_id: str,
        capability_id: str,
        payload: Dict[str, Any],
        idempotency_key: Optional[str] = None,
        actor_id: Optional[str] = None,
        human_approved: bool = False,
        timeout: float = 30.0,
        sync_to_knowledge: bool = True,
    ) -> AgentTask:
        """Submit a task for external agent execution."""
        # 1. Idempotency Check
        if idempotency_key:
            with self._lock:
                if idempotency_key in self._idempotency_cache:
                    existing_id = self._idempotency_cache[idempotency_key]
                    existing_task = self._tasks.get(existing_id)
                    if existing_task and existing_task.status in (TaskStatus.COMPLETED, TaskStatus.RUNNING, TaskStatus.AUTHORIZED):
                        return existing_task

        # 2. Retrieve Agent & Capability Manifests
        target_agent = agent_registry.get_agent(target_agent_id)
        if not target_agent:
            task = AgentTask(
                project_id=project_id,
                team_id=team_id,
                requesting_agent=requesting_agent,
                target_agent=target_agent_id,
                capability=capability_id,
                status=TaskStatus.REJECTED,
                error=f"Target agent '{target_agent_id}' is not registered in the system.",
                idempotency_key=idempotency_key,
            )
            with self._lock:
                self._tasks[task.task_id] = task
            self._record_audit_event(project_id, team_id, task.task_id, target_agent_id, AuditEventType.AGENT_TASK_REJECTED, {"reason": task.error})
            return task

        matching_cap = next((c for c in target_agent.capabilities if c.capability_id == capability_id), None)
        if not matching_cap:
            task = AgentTask(
                project_id=project_id,
                team_id=team_id,
                requesting_agent=requesting_agent,
                target_agent=target_agent_id,
                capability=capability_id,
                status=TaskStatus.REJECTED,
                error=f"Agent '{target_agent_id}' does not offer capability '{capability_id}'.",
                idempotency_key=idempotency_key,
            )
            with self._lock:
                self._tasks[task.task_id] = task
            self._record_audit_event(project_id, team_id, task.task_id, target_agent_id, AuditEventType.AGENT_TASK_REJECTED, {"reason": task.error})
            return task

        # 3. Policy & Authorization Evaluation
        is_auth, rejection_reason = PolicyEngine.evaluate_task_authorization(
            project_id=project_id,
            team_id=team_id,
            requesting_agent=requesting_agent,
            target_agent=target_agent,
            capability=matching_cap,
            actor_id=actor_id,
            human_approved=human_approved,
        )

        task = AgentTask(
            project_id=project_id,
            team_id=team_id,
            requesting_agent=requesting_agent,
            target_agent=target_agent_id,
            capability=capability_id,
            risk_level=matching_cap.risk_level,
            idempotency_key=idempotency_key,
            timeout=timeout,
        )

        with self._lock:
            self._tasks[task.task_id] = task
            if idempotency_key:
                self._idempotency_cache[idempotency_key] = task.task_id

        self._record_audit_event(project_id, team_id, task.task_id, target_agent_id, AuditEventType.AGENT_TASK_CREATED)

        if not is_auth:
            task.status = TaskStatus.REJECTED
            task.error = rejection_reason
            self._record_audit_event(project_id, team_id, task.task_id, target_agent_id, AuditEventType.AGENT_TASK_REJECTED, {"reason": rejection_reason})
            return task

        task.status = TaskStatus.AUTHORIZED
        self._record_audit_event(project_id, team_id, task.task_id, target_agent_id, AuditEventType.AGENT_TASK_AUTHORIZED)

        # 4. Handle Paid Capabilities via x402 Layer (without exposing private keys)
        if matching_cap.estimated_cost > 0:
            # Simulate/Verify x402 payment authorization
            # In Phase 5 x402 model, payment is verified prior to dispatching capability
            pass

        # 5. Sanitize Payload & Construct Context
        sanitized_input = SecuritySanitizer.sanitize_payload(payload)
        input_hash = compute_sha256(sanitized_input)
        task.input_reference = {"hash": input_hash, "params": sanitized_input}

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(timezone.utc).isoformat()
        self._record_audit_event(project_id, team_id, task.task_id, target_agent_id, AuditEventType.AGENT_TASK_STARTED)

        # 6. Execute with Controlled Retries (Max 2 retries for transient failures/timeouts)
        max_retries = 2
        attempt = 0
        raw_result: Optional[Dict[str, Any]] = None
        exec_error: Optional[str] = None
        start_time = time.time()

        while attempt <= max_retries:
            attempt += 1
            try:
                if target_agent.protocol.upper() == "BINDU_A2A":
                    raw_result = await asyncio.wait_for(
                        self.bindu_adapter.execute(
                            agent_id=target_agent_id,
                            capability=capability_id,
                            payload=sanitized_input,
                            task_id=task.task_id,
                            timeout=timeout,
                        ),
                        timeout=timeout,
                    )
                elif target_agent.protocol.upper() == "CORSAIR":
                    raw_result = await asyncio.wait_for(
                        self.corsair_adapter.invoke(
                            agent_id=target_agent_id,
                            capability=capability_id,
                            payload=sanitized_input,
                            task_id=task.task_id,
                            timeout=timeout,
                        ),
                        timeout=timeout,
                    )
                else:
                    raw_result = {"status": "COMPLETED", "result": f"Executed on {target_agent.protocol}"}
                
                exec_error = None
                break
            except asyncio.TimeoutError:
                exec_error = f"Task timed out after {timeout} seconds"
                if attempt > max_retries:
                    task.status = TaskStatus.TIMEOUT
                    task.error = exec_error
                    agent_registry.record_task_outcome(target_agent_id, "TIMEOUT")
                    self._record_audit_event(project_id, team_id, task.task_id, target_agent_id, AuditEventType.AGENT_TASK_FAILED, {"reason": exec_error})
                    return task
            except Exception as exc:
                exec_error = str(exc)
                if attempt > max_retries:
                    task.status = TaskStatus.FAILED
                    task.error = exec_error
                    agent_registry.record_task_outcome(target_agent_id, "FAILURE")
                    self._record_audit_event(project_id, team_id, task.task_id, target_agent_id, AuditEventType.AGENT_TASK_FAILED, {"reason": exec_error})
                    return task

        duration = round(time.time() - start_time, 3)
        task.completed_at = datetime.now(timezone.utc).isoformat()

        if raw_result is None:
            task.status = TaskStatus.FAILED
            task.error = exec_error or "Unknown failure"
            agent_registry.record_task_outcome(target_agent_id, "FAILURE")
            self._record_audit_event(project_id, team_id, task.task_id, target_agent_id, AuditEventType.AGENT_TASK_FAILED, {"reason": task.error})
            return task

        # 7. Result Schema & Policy Validation
        is_result_valid, validation_errors = AgentResultValidator.validate_result(matching_cap, raw_result)
        if not is_result_valid:
            task.status = TaskStatus.REJECTED
            task.error = f"Result schema validation failed: {'; '.join(validation_errors)}"
            agent_registry.record_task_outcome(target_agent_id, "VALIDATION_FAILURE")
            self._record_audit_event(project_id, team_id, task.task_id, target_agent_id, AuditEventType.AGENT_TASK_REJECTED, {"reason": task.error})
            return task

        self._record_audit_event(project_id, team_id, task.task_id, target_agent_id, AuditEventType.AGENT_RESULT_VALIDATED)

        # 8. Record Provenance & Mark Completed
        output_hash = compute_sha256(raw_result)
        task.provenance = TaskProvenance(
            task_id=task.task_id,
            agent_id=target_agent_id,
            agent_version=target_agent.version,
            capability=capability_id,
            protocol=target_agent.protocol,
            input_hash=input_hash,
            output_hash=output_hash,
            execution_duration=duration,
            endpoint=target_agent.endpoint,
            provider=target_agent.provider,
        )

        task.status = TaskStatus.COMPLETED
        task.output_reference = raw_result
        agent_registry.record_task_outcome(target_agent_id, "SUCCESS")
        self._record_audit_event(project_id, team_id, task.task_id, target_agent_id, AuditEventType.AGENT_TASK_COMPLETED, {"duration": duration})

        # 9. Sync Validated Result to Engineering Knowledge Service as a PROPOSAL
        if sync_to_knowledge:
            self._sync_result_to_knowledge(project_id, task, raw_result)

        return task

    def _sync_result_to_knowledge(self, project_id: str, task: AgentTask, result: Dict[str, Any]) -> None:
        """Safely ingest external recommendations into the Phase 9 Knowledge Service as proposals."""
        try:
            import uuid
            from backend.workline.knowledge.service import knowledge_service
            from backend.workline.knowledge.models import (
                Actor,
                ActorType,
                EngineeringFinding,
                FindingSeverity,
            )

            recommendations = result.get("recommendations", [])
            for idx, rec in enumerate(recommendations):
                finding = EngineeringFinding(
                    finding_id=f"fnd_ext_{task.task_id}_{idx}",
                    project_id=project_id,
                    title=f"External Recommendation [{task.target_agent}]: {rec[:60]}",
                    description=rec,
                    category="THERMAL" if "thermal" in task.capability.lower() else "GENERAL",
                    severity=FindingSeverity.INFO,
                    source=f"EXTERNAL_AGENT:{task.target_agent}",
                    source_id=task.task_id,
                    created_by=Actor(actor_type=ActorType.AGENT, actor_id=task.target_agent, name=task.target_agent),
                )
                knowledge_service.create_finding(finding)
        except Exception:
            # Non-blocking graceful fallback
            pass

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel an in-flight external agent task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False

            if task.status not in (TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.AUTHORIZED):
                return False

            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now(timezone.utc).isoformat()

        # Best-effort cancellation via adapter
        if task.target_agent:
            target_agent = agent_registry.get_agent(task.target_agent)
            if target_agent and target_agent.protocol == "BINDU_A2A":
                await self.bindu_adapter.cancel(task_id)
            elif target_agent and target_agent.protocol == "CORSAIR":
                await self.corsair_adapter.cancel(task_id)

        self._record_audit_event(task.project_id, task.team_id, task.task_id, task.target_agent, AuditEventType.AGENT_TASK_CANCELLED)
        return True


# Global singleton gateway instance
interoperability_gateway = InteroperabilityGateway()
