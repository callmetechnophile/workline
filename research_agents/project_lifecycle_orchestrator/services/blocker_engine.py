"""
Blocker detection engine for ProjectLifecycleOrchestrator (Sections 17 & 18).
Identifies hard and soft blockers halting workflow progression.
"""

from typing import Any, Dict, List, Optional
import uuid
from research_agents.project_lifecycle_orchestrator.schemas import BlockerObject


class BlockerEngine:
    """Detects validation, QA, authorization, and environmental blockers."""

    def evaluate_blockers(
        self,
        project_id: str,
        graph_data: Dict[str, Any],
        validation_status: Optional[str] = None,
        qa_status: Optional[str] = None,
        auth_granted: bool = True,
        db_healthy: bool = True,
    ) -> List[BlockerObject]:
        blockers: List[BlockerObject] = []

        # 1. Database Health Check
        if not db_healthy:
            blockers.append(
                BlockerObject(
                    blocker_id=f"BLK-DB-{uuid.uuid4().hex[:4].upper()}",
                    type="DATABASE_UNAVAILABLE",
                    severity="critical",
                    source="SurrealDB",
                    affected_project=project_id,
                    resolution="Restore SurrealDB connection before resuming orchestration.",
                    requires_human=False,
                )
            )

        # 2. Authorization Failure
        if not auth_granted:
            blockers.append(
                BlockerObject(
                    blocker_id=f"BLK-AUTH-{uuid.uuid4().hex[:4].upper()}",
                    type="AUTHORIZATION_DENIED",
                    severity="critical",
                    source="ArmorIQ",
                    affected_project=project_id,
                    resolution="Request explicit execution grant from ArmorIQ policy engine.",
                    requires_human=True,
                )
            )

        # 3. Validation Gate Failures (Agent #9)
        if validation_status and validation_status.upper() in ("BLOCKED", "FAILED", "CRITICAL_FAILURES"):
            blockers.append(
                BlockerObject(
                    blocker_id=f"BLK-VAL-{uuid.uuid4().hex[:4].upper()}",
                    type="VALIDATION_GATE_FAILURE",
                    severity="critical",
                    source="EngineeringValidationAgent",
                    affected_project=project_id,
                    resolution="Resolve engineering design rule violations before proceeding to planning or execution.",
                    requires_human=False,
                )
            )

        # 4. QA Quality Gate Failures (Agent #12)
        if qa_status and qa_status.upper() in ("FAILED", "BLOCKED"):
            blockers.append(
                BlockerObject(
                    blocker_id=f"BLK-QA-{uuid.uuid4().hex[:4].upper()}",
                    type="QA_GATE_FAILURE",
                    severity="critical",
                    source="VerificationQAAgent",
                    affected_project=project_id,
                    resolution="Execute remediation task plan to correct test, security, or conformance failures.",
                    requires_human=False,
                )
            )

        return blockers
