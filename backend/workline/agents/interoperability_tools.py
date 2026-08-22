"""Google ADK agent tools for interacting with external agents through the Interoperability Gateway."""

from typing import Any, Dict, List, Optional

from backend.workline.interoperability.capabilities import AgentCapability
from backend.workline.interoperability.gateway import interoperability_gateway
from backend.workline.interoperability.registry import ExternalAgent, agent_registry
from backend.workline.interoperability.tasks import AgentTask


def discover_external_agents(
    protocol: Optional[str] = None,
    capability_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Discover registered external agents available on Bindu, Corsair, or other protocols.
    
    Args:
        protocol: Optional protocol filter ('BINDU_A2A', 'CORSAIR')
        capability_type: Optional capability filter (e.g., 'THERMAL_ANALYSIS', 'RESEARCH')
    
    Returns:
        List of agent summaries with IDs, names, status, and capabilities.
    """
    agents = agent_registry.discover_agents(protocol=protocol, capability_type=capability_type)
    return [
        {
            "agent_id": a.agent_id,
            "name": a.name,
            "provider": a.provider,
            "protocol": a.protocol,
            "status": a.status.value,
            "version": a.version,
            "capabilities": [c.capability_id for c in a.capabilities],
        }
        for a in agents
    ]


def get_external_capabilities(agent_id: str) -> List[Dict[str, Any]]:
    """Fetch declared capabilities and risk profiles for a given external agent.
    
    Args:
        agent_id: ID of the external agent (e.g. 'ThermalSolver')
    
    Returns:
        List of capabilities including input/output schemas, risk levels, and estimated costs.
    """
    caps = agent_registry.get_capabilities(agent_id)
    return [c.model_dump() for c in caps]


async def delegate_external_task(
    project_id: str,
    team_id: str,
    requesting_agent: str,
    target_agent: str,
    capability: str,
    payload: Dict[str, Any],
    idempotency_key: Optional[str] = None,
    actor_id: Optional[str] = None,
    human_approved: bool = False,
    timeout: float = 30.0,
) -> Dict[str, Any]:
    """Delegate a specialized subtask to an external agent through the security-governed Interoperability Gateway.
    
    Args:
        project_id: Project identifier
        team_id: Team identifier
        requesting_agent: Name of the invoking internal Google ADK agent (e.g., 'PCBAgent')
        target_agent: Target external agent ID (e.g., 'ThermalSolver')
        capability: Specific capability name (e.g., 'thermal_simulation')
        payload: Input parameters for the task
        idempotency_key: Optional idempotency key for state-changing or paid tasks
        actor_id: Initiating user or session identifier
        human_approved: Whether explicit human approval has been granted for HIGH/CRITICAL actions
        timeout: Execution timeout in seconds
    
    Returns:
        Structured task result with status, output payload, and provenance record.
    """
    task: AgentTask = await interoperability_gateway.submit_task(
        project_id=project_id,
        team_id=team_id,
        requesting_agent=requesting_agent,
        target_agent_id=target_agent,
        capability_id=capability,
        payload=payload,
        idempotency_key=idempotency_key,
        actor_id=actor_id,
        human_approved=human_approved,
        timeout=timeout,
    )
    return task.model_dump()


def get_external_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Inspect status, results, and provenance of a delegated external agent task."""
    task = interoperability_gateway.get_task(task_id)
    return task.model_dump() if task else None


async def cancel_external_task(task_id: str) -> bool:
    """Request best-effort cancellation of an active external agent task."""
    return await interoperability_gateway.cancel_task(task_id)
