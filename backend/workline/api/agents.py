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
# Phase 10: External Agent Interoperability Endpoints
# ============================================================================

from backend.workline.interoperability.capabilities import AgentCapability, AgentStatus
from backend.workline.interoperability.gateway import interoperability_gateway
from backend.workline.interoperability.registry import ExternalAgent, agent_registry
from backend.workline.interoperability.tasks import AgentTask


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


@router.get("", response_model=list[ExternalAgent])
@router.get("/", response_model=list[ExternalAgent])
def list_external_agents(status: Optional[AgentStatus] = None):
    """List all registered external agents."""
    return agent_registry.list_agents(status=status)


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
def register_external_agent_endpoint(agent: ExternalAgent):
    """Register a new external agent manifest with Workline."""
    registered = agent_registry.register_agent(agent)
    return {"status": "REGISTERED", "agent": registered.model_dump()}


@router.post("/tasks")
async def submit_external_task_endpoint(req: AgentTaskSubmitRequest):
    """Submit a task for external agent execution via the Interoperability Gateway."""
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
        return task.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to execute external task: {str(exc)}")


@router.get("/tasks/{task_id}")
def get_external_task_status(task_id: str):
    """Fetch status, provenance, and output references for an external task."""
    task = interoperability_gateway.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    return task.model_dump()


@router.post("/tasks/{task_id}/cancel")
async def cancel_external_task_endpoint(task_id: str):
    """Cancel a running external agent task."""
    success = await interoperability_gateway.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=400, detail=f"Unable to cancel task '{task_id}'.")
    return {"status": "CANCELLED", "task_id": task_id}


@router.get("/{agent_id}")
def get_external_agent_details(agent_id: str):
    """Fetch details and trust score for a specific external agent."""
    agent = agent_registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"External agent '{agent_id}' not found.")
    trust = agent_registry.get_trust_record(agent_id)
    return {
        "agent": agent.model_dump(),
        "trust": trust.model_dump(),
    }


@router.get("/{agent_id}/capabilities", response_model=list[AgentCapability])
def get_external_agent_capabilities(agent_id: str):
    """Fetch all declared capabilities and risk profiles for an external agent."""
    agent = agent_registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"External agent '{agent_id}' not found.")
    return agent.capabilities


@router.delete("/{agent_id}")
def unregister_external_agent_endpoint(agent_id: str):
    """Unregister an external agent from Workline."""
    success = agent_registry.unregister_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"External agent '{agent_id}' not found.")
    return {"status": "UNREGISTERED", "agent_id": agent_id}

