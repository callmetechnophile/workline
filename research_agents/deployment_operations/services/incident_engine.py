"""
Operational incident lifecycle management engine.
"""

from typing import List, Optional
from research_agents.deployment_operations.schemas import (
    AlertSeverity,
    IncidentRecord,
    IncidentState,
)


class IncidentEngine:
    """Manages incidents through triage, containment, recovery, and review."""

    def log_incident(
        self,
        incident_id: str,
        project_id: str,
        system_id: str,
        symptoms: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
        root_cause: Optional[str] = None,
        is_confirmed: bool = False,
    ) -> IncidentRecord:
        rc_type = "ROOT_CAUSE_CONFIRMED" if is_confirmed else "ROOT_CAUSE_HYPOTHESIS"
        return IncidentRecord(
            incident_id=incident_id,
            project_id=project_id,
            system_id=system_id,
            symptoms=symptoms,
            severity=severity,
            state=IncidentState.DETECTED,
            root_cause_type=rc_type,
            root_cause_description=root_cause,
        )
