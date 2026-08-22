"""Bindu A2A protocol messaging format and envelope serialization."""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class BinduMessageEnvelope(BaseModel):
    """Standardized Bindu A2A wire protocol envelope."""
    message_id: str = Field(default_factory=lambda: f"bindu-msg-{uuid.uuid4().hex[:12]}")
    conversation_id: str = Field(default_factory=lambda: f"bindu-conv-{uuid.uuid4().hex[:12]}")
    sender_id: str
    recipient_id: str
    action: str  # "DISCOVER", "CAPABILITIES", "SUBMIT_TASK", "TASK_STATUS", "CANCEL_TASK", "RESULT"
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    signature: Optional[str] = None

    def serialize(self) -> str:
        """Serialize envelope to JSON."""
        return self.model_dump_json()

    @classmethod
    def deserialize(cls, raw: str) -> "BinduMessageEnvelope":
        """Deserialize envelope from JSON string."""
        return cls.model_validate_json(raw)
