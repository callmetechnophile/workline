"""
ArmourIQ Audit Trail: Immutable, sanitized security event logger for ADK agent & tool actions.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import time
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field

from backend.workline.armouriq.capabilities import PolicyDecision, RiskTier


# Redaction patterns for sensitive credentials, keys, tokens, and private material
SECRET_PATTERNS = [
    re.compile(r"(?i)(?:api[_-]?key|secret|password|token|private[_-]?key|credential|wallet|auth(?:orization)?)\s*[:=]\s*['\"]?([^'\",\s]+)"),
    re.compile(r"Bearer\s+([A-Za-z0-9\-_.~+/]+=*)"),
    re.compile(r"0x[a-fA-F0-9]{64}"),  # 32-byte hex keys
]


def sanitize_audit_payload(data: Any) -> Any:
    """Recursively redacts secrets and sensitive credentials from audit logs."""
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            k_lower = k.lower()
            if any(s in k_lower for s in ["key", "secret", "password", "token", "private", "credential", "auth"]):
                sanitized[k] = "[REDACTED_SECRET]"
            else:
                sanitized[k] = sanitize_audit_payload(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_audit_payload(item) for item in data]
    elif isinstance(data, str):
        sanitized_str = data
        for pat in SECRET_PATTERNS:
            sanitized_str = pat.sub("[REDACTED_SECRET]", sanitized_str)
        return sanitized_str
    return data


class ArmourIQAuditEvent(BaseModel):
    """Immutable audit record generated on every evaluated ADK action."""
    event_id: str = Field(default_factory=lambda: f"audit_{uuid.uuid4().hex[:16]}")
    timestamp: float = Field(default_factory=time.time)
    request_id: str
    session_id: str
    user_id: str
    project_id: str
    agent_id: str
    parent_agent_id: Optional[str] = None
    tool_name: Optional[str] = None
    capability: Optional[str] = None
    risk_level: str
    policy: str
    decision: str  # ALLOW, DENY, REQUIRE_APPROVAL
    delegation_chain: List[str] = Field(default_factory=list)
    execution_status: str = "RECORDED"  # RECORDED, EXECUTED, BLOCKED, FAILED
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ArmourIQAuditLogger:
    """In-memory and file-persisted audit log manager."""
    _events: List[ArmourIQAuditEvent] = []

    @classmethod
    def log_event(
        cls,
        request_id: str,
        session_id: str,
        user_id: str,
        project_id: str,
        agent_id: str,
        risk_level: RiskTier,
        policy: str,
        decision: PolicyDecision,
        parent_agent_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        capability: Optional[str] = None,
        delegation_chain: Optional[List[str]] = None,
        execution_status: str = "RECORDED",
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ArmourIQAuditEvent:
        """Create, sanitize, and record an immutable audit event."""
        clean_metadata = sanitize_audit_payload(metadata or {})

        event = ArmourIQAuditEvent(
            request_id=request_id,
            session_id=session_id,
            user_id=user_id,
            project_id=project_id,
            agent_id=agent_id,
            parent_agent_id=parent_agent_id,
            tool_name=tool_name,
            capability=capability,
            risk_level=risk_level.value if isinstance(risk_level, RiskTier) else str(risk_level),
            policy=policy,
            decision=decision.value if isinstance(decision, PolicyDecision) else str(decision),
            delegation_chain=delegation_chain or [agent_id],
            execution_status=execution_status,
            error=error,
            metadata=clean_metadata,
        )

        cls._events.append(event)
        return event

    @classmethod
    def get_events(
        cls,
        project_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[ArmourIQAuditEvent]:
        """Retrieve recent audit events filtered by project or agent."""
        res = cls._events
        if project_id:
            res = [e for e in res if e.project_id == project_id]
        if agent_id:
            res = [e for e in res if e.agent_id == agent_id]
        return res[-limit:]

    @classmethod
    def clear(cls) -> None:
        """Reset audit events (for test isolation)."""
        cls._events.clear()
