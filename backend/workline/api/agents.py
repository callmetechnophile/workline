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
