"""FastAPI router for External Agent Interoperability."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.workline.interoperability.capabilities import AgentCapability, AgentStatus
from backend.workline.interoperability.gateway import interoperability_gateway
from backend.workline.interoperability.registry import ExternalAgent, agent_registry
from backend.workline.interoperability.tasks import AgentTask

router = APIRouter(prefix="/api/agents", tags=["External Agents"])


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
    payload: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: Optional[str] = None
    actor_id: Optional[str] = "default_user"
    human_approved: bool = False
    timeout: float = 30.0


@router.get("", response_model=List[ExternalAgent])
@router.get("/", response_model=List[ExternalAgent])
def list_agents(status: Optional[AgentStatus] = None):
    """List all registered external agents."""
    return agent_registry.list_agents(status=status)


@router.get("/{agent_id}")
def get_agent_details(agent_id: str):
    """Fetch details and trust score for a specific external agent."""
    agent = agent_registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"External agent '{agent_id}' not found.")
    trust = agent_registry.get_trust_record(agent_id)
    return {
        "agent": agent.model_dump(),
        "trust": trust.model_dump(),
    }


@router.get("/{agent_id}/capabilities", response_model=List[AgentCapability])
def get_agent_capabilities(agent_id: str):
    """Fetch all declared capabilities and risk profiles for an external agent."""
    agent = agent_registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"External agent '{agent_id}' not found.")
    return agent.capabilities


@router.post("/discover")
def discover_agents(req: AgentDiscoverRequest):
    """Discover available external agents across Bindu, Corsair, and registered providers."""
    agents = agent_registry.discover_agents(
        protocol=req.protocol,
        capability_type=req.capability_type,
        force_refresh=req.force_refresh,
    )
    return {"agents": [a.model_dump() for a in agents], "total": len(agents)}


@router.post("/register")
def register_external_agent(agent: ExternalAgent):
    """Register a new external agent manifest with Workline."""
    registered = agent_registry.register_agent(agent)
    return {"status": "REGISTERED", "agent": registered.model_dump()}


@router.delete("/{agent_id}")
def unregister_external_agent(agent_id: str):
    """Unregister an external agent from Workline."""
    success = agent_registry.unregister_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"External agent '{agent_id}' not found.")
    return {"status": "UNREGISTERED", "agent_id": agent_id}


@router.post("/tasks")
async def submit_external_task(req: AgentTaskSubmitRequest):
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
def get_task_status(task_id: str):
    """Fetch status, provenance, and output references for an external task."""
    task = interoperability_gateway.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    return task.model_dump()


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Cancel a running external agent task."""
    success = await interoperability_gateway.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=400, detail=f"Unable to cancel task '{task_id}'. Task may not exist or is already completed/failed.")
    return {"status": "CANCELLED", "task_id": task_id}
