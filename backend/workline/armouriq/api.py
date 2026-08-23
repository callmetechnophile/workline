"""
FastAPI router exposing ArmourIQ trust, health, audit, and governance endpoints.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from backend.workline.armouriq.audit import ArmourIQAuditEvent, ArmourIQAuditLogger
from backend.workline.armouriq.capabilities import AgentCapability, RiskTier
from backend.workline.armouriq.health import ArmourIQHealthService
from backend.workline.armouriq.identity import CANONICAL_AGENT_PROFILES

router = APIRouter(prefix="/api/armouriq", tags=["ArmourIQ Trust & Governance"])


class ApprovalRequest(BaseModel):
    decision: str  # APPROVE or REJECT
    reason: Optional[str] = None


@router.get("/health")
def get_armouriq_health():
    """Retrieve operational status and subsystem metrics for ArmourIQ."""
    return ArmourIQHealthService.get_health_status()


@router.get("/audit", response_model=List[ArmourIQAuditEvent])
def get_audit_trail(
    project_id: Optional[str] = Query(None, description="Filter audit events by project"),
    agent_id: Optional[str] = Query(None, description="Filter audit events by agent"),
    limit: int = Query(50, ge=1, le=200),
):
    """Fetch sanitized, immutable audit trail records."""
    return ArmourIQAuditLogger.get_events(project_id=project_id, agent_id=agent_id, limit=limit)


@router.get("/agents")
def list_governed_agents():
    """List ADK agent identities, trust classifications, capabilities, and policy profiles."""
    agents = []
    for agent_name, profile in CANONICAL_AGENT_PROFILES.items():
        agents.append({
            "agent_id": f"workline.{agent_name}",
            "agent_name": agent_name.replace("_", " ").title(),
            "agent_type": profile["agent_type"],
            "trust_level": profile["trust_level"],
            "policy_profile": profile["policy_profile"],
            "capabilities": [c.value for c in profile["capabilities"]],
            "risk_tier": "CRITICAL" if agent_name == "procurement_agent" else "LOW",
        })
    return {"agents": agents}


@router.get("/capabilities")
def list_capabilities():
    """List standard capabilities and risk tiers."""
    return {
        "capabilities": [c.value for c in AgentCapability],
        "risk_tiers": [r.value for r in RiskTier],
    }
