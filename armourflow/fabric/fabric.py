from armourflow.registry.manifest import AgentManifest
"""Unified Agent Control Fabric orchestrating tasks, idempotency, retries, and execution via async job pipeline."""

import asyncio
import importlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from loguru import logger

from armourflow.config.settings import PlatformSettings, get_settings
from armourflow.data.client import PlatformDatabaseClient, get_database_client
from armourflow.fabric.events import FabricEventBus, get_event_bus
from armourflow.fabric.router import CapabilityRouter
from armourflow.fabric.schemas import FabricTask, TaskContext, TaskState
from armourflow.registry.registry import AuthoritativeAgentRegistry, get_agent_registry
from armourflow.security.armoriq import ArmorIQBoundary, get_security_boundary

# Workline async job system integration
from backend.workline.jobs.models import Job
from backend.workline.jobs.queue import JobQueue, default_job_queue
from backend.workline.jobs.states import JobState
from backend.workline.jobs.worker import JobRegistry, default_job_registry, default_job_worker
from backend.workline.jobs.errors import AuthorizationError, ContractValidationError, NonRetryableJobError


class AgentControlFabric:
    """
    Central routing, task state, event, lifecycle, and execution coordination fabric.
    Tasks are enqueued to the Workline asynchronous job pipeline with durable SQLite idempotency.
    """

    _instance: Optional["AgentControlFabric"] = None

    def __init__(
        self,
        settings: Optional[PlatformSettings] = None,
        registry: Optional[AuthoritativeAgentRegistry] = None,
        db_client: Optional[PlatformDatabaseClient] = None,
        security: Optional[ArmorIQBoundary] = None,
        job_queue: Optional[JobQueue] = None,
        job_registry: Optional[JobRegistry] = None,
    ):
        self.settings = settings or get_settings()
        self.registry = registry or get_agent_registry()
        self.db = db_client or get_database_client()
        self.security = security or get_security_boundary()
        self.job_queue = job_queue or default_job_queue
        self.job_registry = job_registry or default_job_registry

        self.router = CapabilityRouter(self.registry)
        self.event_bus = get_event_bus()

        self._tasks: Dict[str, FabricTask] = {}
        self._idempotency_cache: Dict[str, str] = {}  # key -> task_id

        # Register control fabric task handler in the asynchronous job registry
        self._register_job_handlers()

    def _register_job_handlers(self):
        """Register the fabric agent execution job handler with JobRegistry."""
        async def fabric_job_handler(job: Job) -> Dict[str, Any]:
            task_id = job.input_reference.get("task_id")
            agent_id = job.input_reference.get("agent_id")
            task = self._tasks.get(task_id)
            if not task:
                raise NonRetryableJobError(f"Fabric task '{task_id}' not found in fabric state.")

            manifest = self.registry.get_agent(agent_id)
            if not manifest:
                raise NonRetryableJobError(f"Agent '{agent_id}' not registered in manifest registry.")

            # Perform agent invocation
            await self._execute_task(task, manifest)

            if task.state == TaskState.FAILED:
                if "AUTHORIZATION_DENIED" in (task.error or ""):
                    raise AuthorizationError(task.error or "Authorization denied")
                raise RuntimeError(task.error or "Agent execution failed")
            elif task.state == TaskState.TIMEOUT:
                raise TimeoutError(task.error or "Agent execution timed out")

            return task.result or {}

        self.job_registry.register("fabric_agent_execution", fabric_job_handler)

    @classmethod
    def get_instance(cls) -> "AgentControlFabric":
        if cls._instance is None:
            cls._instance = AgentControlFabric()
        return cls._instance

    async def submit_task(
        self,
        payload: Dict[str, Any],
        target_agent_id: Optional[str] = None,
        target_capability: Optional[str] = None,
        project_id: str = "default",
        user_id: str = "system",
        idempotency_key: Optional[str] = None,
        unauthorized_project_access: bool = False,
        sync_wait: bool = True,
    ) -> FabricTask:
        """
        Create, route, authorize, enqueue into async job queue, execute, and persist a task.
        Supports durable SQLite idempotency deduplication across process restarts.
        """
        # 1. Durable Idempotency Check (In-Memory + Database)
        if idempotency_key:
            if idempotency_key in self._idempotency_cache:
                existing_id = self._idempotency_cache[idempotency_key]
                if existing_id in self._tasks:
                    logger.info(f"[ControlFabric] Returning in-memory cached result for idempotency key '{idempotency_key}'")
                    return self._tasks[existing_id]

            # Check persistent database
            try:
                from backend.database import get_idempotency_record
                record = get_idempotency_record(idempotency_key)
                if record and record.get("task_id"):
                    cached_task_id = record["task_id"]
                    if cached_task_id in self._tasks:
                        return self._tasks[cached_task_id]
                    # Reconstitute task from database record if possible
                    reconstituted = FabricTask(
                        task_id=cached_task_id,
                        context=TaskContext(project_id=project_id, user_id=user_id),
                        target_agent_id=target_agent_id,
                        target_capability=target_capability,
                        payload=payload,
                        idempotency_key=idempotency_key,
                        state=TaskState(record.get("status", "COMPLETED")),
                        result=record.get("result"),
                        error=record.get("error"),
                    )
                    self._tasks[cached_task_id] = reconstituted
                    self._idempotency_cache[idempotency_key] = cached_task_id
                    logger.info(f"[ControlFabric] Reconstituted cached task from database for key '{idempotency_key}'")
                    return reconstituted
            except Exception as e:
                logger.debug(f"[ControlFabric] Idempotency database lookup skipped: {e}")

        context = TaskContext(
            project_id=project_id,
            user_id=user_id,
        )
        task = FabricTask(
            context=context,
            target_agent_id=target_agent_id,
            target_capability=target_capability,
            payload=payload,
            idempotency_key=idempotency_key,
            state=TaskState.QUEUED,
        )
        self._tasks[task.task_id] = task
        if idempotency_key:
            self._idempotency_cache[idempotency_key] = task.task_id
            try:
                from backend.database import upsert_idempotency_record
                upsert_idempotency_record(
                    key=idempotency_key,
                    task_id=task.task_id,
                    status=task.state.value,
                )
            except Exception as e:
                logger.debug(f"[ControlFabric] Idempotency record insertion skipped: {e}")

        self.event_bus.publish("task.queued", task.task_id, {"project_id": project_id})

        # 2. Route Target
        manifest, route_err = self.router.resolve_target(
            capability=target_capability,
            agent_id=target_agent_id,
        )
        if route_err or not manifest:
            task.state = TaskState.FAILED
            task.error = route_err or "ROUTING_FAILED"
            self.event_bus.publish("task.failed", task.task_id, {"error": task.error})
            await self._persist_task(task)
            self._update_durable_idempotency(task)
            return task

        task.target_agent_id = manifest.agent_id
        task.state = TaskState.ROUTED
        self.event_bus.publish("task.routed", task.task_id, {"agent_id": manifest.agent_id})

        # 3. ArmorIQ Authorization Boundary
        action = payload.get("operation") or payload.get("action") or "execute"
        authorized, auth_err = self.security.authorize(
            agent_name=manifest.name,
            action=action,
            project_id=project_id,
            unauthorized_access=unauthorized_project_access,
        )
        if not authorized:
            task.state = TaskState.FAILED
            task.error = auth_err or "AUTHORIZATION_DENIED"
            self.event_bus.publish("task.denied", task.task_id, {"error": task.error})
            await self._persist_task(task)
            self._update_durable_idempotency(task)
            return task

        task.state = TaskState.AUTHORIZED

        # 4. Enqueue into Asynchronous Job Pipeline
        job = Job(
            project_id=project_id,
            job_type="fabric_agent_execution",
            requested_by=user_id,
            input_reference={
                "task_id": task.task_id,
                "agent_id": manifest.agent_id,
                "payload": payload,
            },
            correlation_id=task.context.task_id,
        )
        await self.job_queue.enqueue(job)
        logger.info(f"[ControlFabric] Dispatched task {task.task_id} to job queue (job_id={job.job_id})")

        # 5. Execution resolution: worker execution or direct inline wait
        if sync_wait:
            await self._execute_task(task, manifest)
            # Sync job state with queue
            job.status = JobState.SUCCEEDED if task.state == TaskState.COMPLETED else JobState.FAILED
            job.output_reference = task.result
            job.error = task.error
            job.completed_at = datetime.now(timezone.utc).isoformat()
            await self.job_queue.update_job(job)

        await self._persist_task(task)
        self._update_durable_idempotency(task)
        return task

    def _update_durable_idempotency(self, task: FabricTask):
        """Update persistent idempotency record with task completion/failure details."""
        if task.idempotency_key:
            try:
                from backend.database import upsert_idempotency_record
                upsert_idempotency_record(
                    key=task.idempotency_key,
                    task_id=task.task_id,
                    status=task.state.value,
                    result=task.result,
                    error=task.error,
                )
            except Exception as e:
                logger.debug(f"[ControlFabric] Failed to update durable idempotency record: {e}")

    async def _execute_task(self, task: FabricTask, manifest: AgentManifest):
        """Invoke the target agent entrypoint with timeout and error handling."""
        task.state = TaskState.EXECUTING
        self.event_bus.publish("task.executing", task.task_id, {"agent_id": manifest.agent_id})

        module_name, class_name = manifest.entrypoint.split(":")
        try:
            mod = importlib.import_module(module_name)
            agent_cls = getattr(mod, class_name)
            agent_instance = agent_cls()

            # Execute run method with polymorphic input conversion
            payload = dict(task.payload)
            payload["project_id"] = task.context.project_id
            payload["user_id"] = task.context.user_id
            if "operation" not in payload and task.target_capability:
                payload["operation"] = task.target_capability

            import inspect
            sig = inspect.signature(agent_instance.run)
            params = list(sig.parameters.values())
            arg = payload
            if params:
                param_type = params[0].annotation
                if param_type != inspect.Parameter.empty and hasattr(param_type, "model_validate"):
                    try:
                        arg = param_type.model_validate(payload)
                    except Exception as val_err:
                        # Try constructing with only known fields or default operation
                        try:
                            valid_fields = getattr(param_type, "model_fields", {})
                            filtered = {k: v for k, v in payload.items() if k in valid_fields}
                            arg = param_type.model_validate(filtered)
                        except Exception:
                            logger.warning(f"[ControlFabric] Model validation fallback for {param_type}: {val_err}")
                            arg = payload
                elif param_type != inspect.Parameter.empty and hasattr(param_type, "__dataclass_fields__"):
                    try:
                        valid_keys = {k: payload[k] for k in param_type.__dataclass_fields__ if k in payload}
                        arg = param_type(**valid_keys)
                    except Exception:
                        arg = payload

            # Pass timeout guard
            if asyncio.iscoroutinefunction(getattr(agent_instance, "run", None)):
                res = await asyncio.wait_for(agent_instance.run(arg), timeout=task.timeout_seconds)
            elif hasattr(agent_instance, "run"):
                res = agent_instance.run(arg)
                if asyncio.iscoroutine(res):
                    res = await asyncio.wait_for(res, timeout=task.timeout_seconds)
            else:
                raise AttributeError(f"Agent '{manifest.name}' has no callable run() method.")

            # Record success & normalize output
            task.state = TaskState.COMPLETED
            if hasattr(res, "model_dump"):
                task.result = res.model_dump()
            elif hasattr(res, "_as_dict"):
                task.result = res._as_dict()
            elif isinstance(res, dict):
                task.result = res
            else:
                task.result = {"result": str(res)}
            self.event_bus.publish("task.completed", task.task_id, {"status": "ok"})

        except asyncio.TimeoutError:
            task.state = TaskState.TIMEOUT
            task.error = f"TASK_TIMEOUT: Execution exceeded {task.timeout_seconds} seconds."
            self.event_bus.publish("task.timeout", task.task_id, {"error": task.error})
        except Exception as e:
            task.state = TaskState.FAILED
            task.error = f"EXECUTION_ERROR: {str(e)}"
            self.event_bus.publish("task.failed", task.task_id, {"error": task.error})

    async def _persist_task(self, task: FabricTask):
        """Persist task record in SurrealDB graph state."""
        try:
            await self.db.create_node("fabric_task", task.task_id, task.model_dump())
            await self.db.relate_nodes(
                f"project:{task.context.project_id}",
                "has_task",
                f"fabric_task:{task.task_id}",
            )
        except Exception as e:
            logger.warning(f"[ControlFabric] Failed to persist task {task.task_id} to graph: {e}")

    def get_task(self, task_id: str) -> Optional[FabricTask]:
        return self._tasks.get(task_id)

    def list_tasks(self, project_id: Optional[str] = None) -> List[FabricTask]:
        if project_id:
            return [t for t in self._tasks.values() if t.context.project_id == project_id]
        return list(self._tasks.values())

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY",
            "component": "AgentControlFabric",
            "active_tasks": len(self._tasks),
            "registered_agents": len(self.registry.list_agents()),
            "idempotency_cache_size": len(self._idempotency_cache),
        }


def get_control_fabric() -> AgentControlFabric:
    return AgentControlFabric.get_instance()
