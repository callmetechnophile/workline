"""Entity resolver preventing blind merges of ambiguous part numbers."""

from enum import Enum
from typing import NamedTuple
from backend.workline.documents.models import EngineeringEntity


class ResolutionStatus(str, Enum):
    MATCHED = "MATCHED"
    ALIAS = "ALIAS"
    UNRESOLVED = "UNRESOLVED"


class ResolutionResult(NamedTuple):
    status: ResolutionStatus
    canonical_id: str
    confidence: float
    reason: str


class EntityResolver:
    """Safely resolves entities without blind assumptions."""

    @classmethod
    def resolve(cls, entity_a: EngineeringEntity, entity_b: EngineeringEntity) -> ResolutionResult:
        val_a = entity_a.normalized_value.upper()
        val_b = entity_b.normalized_value.upper()

        if val_a == val_b:
            return ResolutionResult(
                status=ResolutionStatus.MATCHED,
                canonical_id=entity_a.entity_id,
                confidence=1.0,
                reason="Exact case-insensitive match",
            )

        # Base part vs package suffix (e.g. TPS62130 vs TPS62130RGTR)
        if val_b.startswith(val_a) or val_a.startswith(val_b):
            canonical = entity_a.entity_id if len(val_a) <= len(val_b) else entity_b.entity_id
            return ResolutionResult(
                status=ResolutionStatus.ALIAS,
                canonical_id=canonical,
                confidence=0.85,
                reason="Base part number match with package suffix",
            )

        return ResolutionResult(
            status=ResolutionStatus.UNRESOLVED,
            canonical_id=entity_a.entity_id,
            confidence=0.1,
            reason="Distinct part numbers or ambiguous context",
        )
