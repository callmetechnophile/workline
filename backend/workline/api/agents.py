"""FastAPI router for Workline Multi-Agent Engine."""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.workline.agents.runtime import agent_runtime
from backend.workline.agents.shared.state import AgentState

router = APIRouter(prefix="/api/agents", tags=["Agents"])


class AgentRunRequest(BaseModel):
    project_id: str
    task: str
    stage: Optional[str] = None
    user_id: Optional[str] = "default_user"


class AgentApprovalRequest(BaseModel):
    decision: str  # START_BUILD or CONTINUE_RESEARCH


@router.post("/run")
async def run_agent(payload: AgentRunRequest):
    """Launch multi-agent execution for a project."""
    try:
        state: AgentState = await agent_runtime.start_execution(
            project_id=payload.project_id,
            task=payload.task,
            stage=payload.stage,
            user_id=payload.user_id or "default_user",
        )
        return {
            "execution_id": state.execution_id,
            "session_id": state.session_id,
            "project_id": state.project_id,
            "status": state.status.value,
            "agent_id": state.agent_id,
            "stage": state.stage,
            "requires_user_action": state.requires_user_action,
            "action_prompt": state.action_prompt,
            "output_summary": state.output_summary,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to start agent execution: {str(exc)}")


@router.get("/executions/{execution_id}")
def get_execution_status(execution_id: str):
    """Fetch status, events, and findings for an agent execution."""
    state = agent_runtime.get_execution(execution_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Execution '{execution_id}' not found.")

    return state.model_dump()


@router.post("/approval/{execution_id}")
async def submit_approval(execution_id: str, payload: AgentApprovalRequest):
    """Submit human decision at checkpoint (e.g. START_BUILD or CONTINUE_RESEARCH)."""
    try:
        state = await agent_runtime.submit_human_approval(
            execution_id=execution_id,
            decision=payload.decision,
        )
        return state.model_dump()
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Approval submission failed: {str(exc)}")


@router.get("/project/{project_id}/status")
def get_project_agent_status(project_id: str):
    """Get active or most recent agent execution for a project."""
    execs = agent_runtime.list_executions_for_project(project_id)
    if not execs:
        return {
            "project_id": project_id,
            "has_active_execution": False,
            "status": "IDLE",
            "current_agent": "None",
            "stage": "None",
        }

    latest = execs[-1]
    return {
        "project_id": project_id,
        "has_active_execution": latest.status.value in ("RUNNING", "WAITING_FOR_USER"),
        "execution_id": latest.execution_id,
        "status": latest.status.value,
        "current_agent": latest.agent_id,
        "stage": latest.stage,
        "requires_user_action": latest.requires_user_action,
        "action_prompt": latest.action_prompt,
        "events_count": len(latest.events),
    }


# ============================================================================
# Phase 10: External Agent & Architecture Cluster Interoperability Endpoints
# ============================================================================

import hashlib
from datetime import datetime, timezone
from loguru import logger
from backend.workline.database.repositories.agent_repository import agent_repository
from backend.workline.interoperability.capabilities import AgentCapability, AgentStatus
from backend.workline.interoperability.gateway import interoperability_gateway
from backend.workline.interoperability.registry import ExternalAgent, agent_registry
from backend.workline.interoperability.tasks import AgentTask, TaskStatus


class AgentDiscoverRequest(BaseModel):
    protocol: Optional[str] = None
    capability_type: Optional[str] = None
    force_refresh: bool = False


class AgentTaskSubmitRequest(BaseModel):
    project_id: str
    team_id: str = "default_team"
    requesting_agent: str = "WorklineUser"
    target_agent: str
    capability: str
    payload: dict = {}
    idempotency_key: Optional[str] = None
    actor_id: Optional[str] = "default_user"
    human_approved: bool = False
    timeout: float = 30.0


@router.get("")
@router.get("/")
async def list_external_agents(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    cluster: Optional[str] = None,
):
    """List all registered agents from SurrealDB / repository (canonical R1-R5 cluster and external agents)."""
    return await agent_repository.list_agents(project_id=project_id, status=status, cluster=cluster)


@router.post("/sync")
async def sync_agents():
    """Sync all canonical cluster agents to SurrealDB."""
    await agent_repository.sync_to_surrealdb()
    agents = await agent_repository.list_agents()
    return {"status": "SYNCED", "count": len(agents)}


@router.get("/tasks")
async def list_agent_tasks(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
):
    """List agent tasks, optionally filtered by project_id and status from SurrealDB."""
    return await agent_repository.list_tasks(project_id=project_id, status=status)


@router.get("/executions")
async def list_agent_executions(
    project_id: Optional[str] = None,
):
    """List execution history and timeline events with ArmorIQ provenance hashes."""
    return await agent_repository.list_executions(project_id=project_id)


@router.post("/discover")
def discover_external_agents(req: AgentDiscoverRequest):
    """Discover available external agents across Bindu, Corsair, and registered providers."""
    agents = agent_registry.discover_agents(
        protocol=req.protocol,
        capability_type=req.capability_type,
        force_refresh=req.force_refresh,
    )
    return {"agents": [a.model_dump() for a in agents], "total": len(agents)}


@router.post("/register")
async def register_external_agent_endpoint(agent_data: dict, project_id: Optional[str] = None):
    """Register a new agent manifest with Workline and persist into SurrealDB."""
    registered = await agent_repository.register_agent(agent_data, project_id=project_id)
    try:
        caps = []
        for c in registered.get("capabilities", []):
            if isinstance(c, dict):
                c_dict = dict(c)
                if "agent_id" not in c_dict:
                    c_dict["agent_id"] = registered["agent_id"]
                caps.append(AgentCapability(**c_dict))
            else:
                caps.append(c)
        ext = ExternalAgent(
            agent_id=registered["agent_id"],
            name=registered.get("name", registered["agent_id"]),
            description=registered.get("description", ""),
            provider=registered.get("provider", "External Provider"),
            protocol=registered.get("protocol", "BINDU_A2A"),
            endpoint=registered.get("endpoint"),
            version=registered.get("version", "1.0.0"),
            status=AgentStatus.AVAILABLE,
            capabilities=caps,
        )
        agent_registry.register_agent(ext)
    except Exception as exc:
        logger.warning(f"Error registering agent {registered.get('agent_id')} in gateway: {exc}")
    return {"status": "REGISTERED", "agent": registered}


@router.post("/tasks")
async def submit_external_task_endpoint(req: AgentTaskSubmitRequest):
    """Submit a task for external or cluster agent execution, persist in SurrealDB, and record ArmorIQ receipt."""
    # Ensure agent is registered with interoperability gateway if in repo
    repo_agent = await agent_repository.get_agent(req.target_agent)
    if repo_agent and not agent_registry.get_agent(req.target_agent):
        try:
            caps = []
            for c in repo_agent.get("capabilities", []):
                if isinstance(c, dict):
                    c_dict = dict(c)
                    if "agent_id" not in c_dict:
                        c_dict["agent_id"] = repo_agent["agent_id"]
                    caps.append(AgentCapability(**c_dict))
                else:
                    caps.append(c)
            ext = ExternalAgent(
                agent_id=repo_agent["agent_id"],
                name=repo_agent.get("name", repo_agent["agent_id"]),
                description=repo_agent.get("description", ""),
                provider=repo_agent.get("provider", "Workline"),
                protocol=repo_agent.get("protocol", "BINDU_A2A"),
                endpoint=repo_agent.get("endpoint"),
                version=repo_agent.get("version", "1.0.0"),
                status=AgentStatus.AVAILABLE,
                capabilities=caps,
            )
            agent_registry.register_agent(ext)
        except Exception as exc:
            logger.warning(f"Error registering repo agent {req.target_agent} in gateway: {exc}")

    try:
        task: AgentTask = await interoperability_gateway.submit_task(
            project_id=req.project_id,
            team_id=req.team_id,
            requesting_agent=req.requesting_agent,
            target_agent_id=req.target_agent,
            capability_id=req.capability,
            payload=req.payload,
            idempotency_key=req.idempotency_key,
            actor_id=req.actor_id,
            human_approved=req.human_approved,
            timeout=req.timeout,
        )
        task_dict = task.model_dump()

        # Persist task in SurrealDB
        await agent_repository.create_task(task_dict)

        # Record Execution timeline step
        exec_id = f"exec_{task.task_id}"
        dur = task.provenance.execution_duration if task.provenance else 0.5
        receipt_hash = hashlib.sha256(f"{task.task_id}_{task.status}".encode()).hexdigest()[:16]
        await agent_repository.create_execution({
            "execution_id": exec_id,
            "task_id": task.task_id,
            "project_id": req.project_id,
            "agent_name": f"{req.target_agent} ({req.capability})",
            "action": f"Executed {req.capability}" if task.status == TaskStatus.COMPLETED else f"Task {task.status.value}: {task.error or ''}",
            "status": "COMPLETED" if task.status == TaskStatus.COMPLETED else ("FAILED" if task.status in (TaskStatus.FAILED, TaskStatus.REJECTED) else "PENDING"),
            "created_at": task.completed_at or task.created_at,
            "duration": dur,
            "armoriq_receipt": f"receipt_armoriq_{receipt_hash}",
        })

        # Record ArmorIQ cryptographic audit event
        await agent_repository.record_armoriq_audit({
            "audit_id": f"audit_{task.task_id}",
            "project_id": req.project_id,
            "team_id": req.team_id,
            "task_id": task.task_id,
            "agent_id": req.target_agent,
            "capability": req.capability,
            "status": task.status.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "receipt_hash": receipt_hash,
            "provenance": task.provenance.model_dump() if task.provenance else {},
        })

        task_dict["armoriq_receipt"] = f"receipt_armoriq_{receipt_hash}"
        return task_dict
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to execute task: {str(exc)}")


@router.get("/tasks/{task_id}")
async def get_external_task_status(task_id: str):
    """Fetch status, provenance, and output references for a task."""
    task = await agent_repository.get_task(task_id)
    if not task:
        gtask = interoperability_gateway.get_task(task_id)
        if not gtask:
            raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
        return gtask.model_dump()
    return task


@router.post("/tasks/{task_id}/cancel")
async def cancel_external_task_endpoint(task_id: str):
    """Cancel a running external agent task."""
    success = await interoperability_gateway.cancel_task(task_id)
    await agent_repository.update_task(task_id, {"status": "CANCELLED"})
    if not success:
        raise HTTPException(status_code=400, detail=f"Unable to cancel task '{task_id}'.")
    return {"status": "CANCELLED", "task_id": task_id}


@router.get("/{agent_id}")
async def get_external_agent_details(agent_id: str):
    """Fetch details and trust score for a specific agent."""
    agent = await agent_repository.get_agent(agent_id)
    if not agent:
        ext = agent_registry.get_agent(agent_id)
        if not ext:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found.")
        agent = ext.model_dump()
    trust = agent_registry.get_trust_record(agent_id)
    return {
        "agent": agent,
        "trust": trust.model_dump() if trust else {"agent_id": agent_id, "trust_score": agent.get("trust_score", 1.0)},
    }


@router.get("/{agent_id}/capabilities")
async def get_external_agent_capabilities(agent_id: str):
    """Fetch all declared capabilities and risk profiles for an agent."""
    agent = await agent_repository.get_agent(agent_id)
    if not agent:
        ext = agent_registry.get_agent(agent_id)
        if not ext:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found.")
        return ext.capabilities
    return agent.get("capabilities", [])


@router.delete("/{agent_id}")
async def unregister_external_agent_endpoint(agent_id: str):
    """Unregister an agent from Workline."""
    await agent_repository.unregister_agent(agent_id)
    agent_registry.unregister_agent(agent_id)
    return {"status": "UNREGISTERED", "agent_id": agent_id}


