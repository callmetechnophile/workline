"""
Compliance waiver and exception management for EngineeringComplianceAgent (Sections 43–46).
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid
from research_agents.engineering_compliance.schemas import ComplianceWaiver


class WaiverManager:
    """Manages creation, validation, and expiration of compliance waivers."""

    def create_waiver(
        self,
        project_id: str,
        rule_id: str,
        artifact_id: str,
        reason: str,
        risk: str,
        approved_by: str,
        duration_days: int = 30,
    ) -> ComplianceWaiver:
        exp = (datetime.now(timezone.utc) + timedelta(days=duration_days)).isoformat()
        return ComplianceWaiver(
            waiver_id=f"WAIV-{uuid.uuid4().hex[:6].upper()}",
            project_id=project_id,
            rule_id=rule_id,
            artifact_id=artifact_id,
            reason=reason,
            risk=risk,
            approved_by=approved_by,
            expires_at=exp,
            status="APPROVED",
        )

    def is_waiver_expired(self, waiver: ComplianceWaiver) -> bool:
        return datetime.fromisoformat(waiver.expires_at) <= datetime.now(timezone.utc)
