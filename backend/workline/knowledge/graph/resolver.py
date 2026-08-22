"""Prioritized Entity Resolution Engine."""

from typing import List, NamedTuple, Optional
from backend.workline.knowledge.graph.models import CanonicalEntity, EntityMention


class ResolutionResult(NamedTuple):
    status: str  # "RESOLVED", "ALIAS_VARIANT", "UNRESOLVED"
    canonical_entity_id: Optional[str]
    matched_entity: Optional[CanonicalEntity]
    confidence: float
    strategy: str
    reason: str


class EntityResolver:
    """Multi-stage prioritized resolution engine."""

    @classmethod
    def resolve_mention(
        cls,
        mention: EntityMention,
        existing_entities: List[CanonicalEntity],
        manufacturer_context: Optional[str] = None,
    ) -> ResolutionResult:
        mention_text = mention.original_text.strip().upper()
        norm_text = mention.normalized_text.strip().upper()

        # 1. Exact Canonical Name Match
        for ent in existing_entities:
            if ent.canonical_name.upper() == mention_text:
                return ResolutionResult(
                    status="RESOLVED",
                    canonical_entity_id=ent.entity_id,
                    matched_entity=ent,
                    confidence=1.0,
                    strategy="EXACT_CANONICAL_MATCH",
                    reason=f"Exact match with canonical entity '{ent.canonical_name}'",
                )

        # 2. Manufacturer + Part Number Match
        if manufacturer_context:
            mfr_upper = manufacturer_context.strip().upper()
            for ent in existing_entities:
                if ent.manufacturer and ent.manufacturer.upper() == mfr_upper:
                    if (
                        ent.canonical_name.upper() == mention_text
                        or (ent.base_part_number and ent.base_part_number.upper() == mention_text)
                    ):
                        return ResolutionResult(
                            status="RESOLVED",
                            canonical_entity_id=ent.entity_id,
                            matched_entity=ent,
                            confidence=0.98,
                            strategy="MANUFACTURER_PART_MATCH",
                            reason=f"Matched with manufacturer '{ent.manufacturer}' and part number '{mention_text}'",
                        )

        # 3. Known Aliases Match
        for ent in existing_entities:
            if any(a.upper() == mention_text or a.upper() == norm_text for a in ent.aliases):
                return ResolutionResult(
                    status="RESOLVED",
                    canonical_entity_id=ent.entity_id,
                    matched_entity=ent,
                    confidence=0.95,
                    strategy="ALIAS_MATCH",
                    reason=f"Matched known alias for entity '{ent.canonical_name}'",
                )

        # 4. Base Part Number & Package Variant Check (e.g. TPS62130 vs TPS62130RGTR)
        for ent in existing_entities:
            canon_upper = ent.canonical_name.upper()
            if mention_text.startswith(canon_upper) or canon_upper.startswith(mention_text):
                return ResolutionResult(
                    status="ALIAS_VARIANT",
                    canonical_entity_id=ent.entity_id,
                    matched_entity=ent,
                    confidence=0.85,
                    strategy="PART_NUMBER_VARIANT",
                    reason=f"Packaging or order code variant of base part '{ent.canonical_name}'",
                )

        # 5. Unresolved (Preserve ambiguity, do not blindly merge)
        return ResolutionResult(
            status="UNRESOLVED",
            canonical_entity_id=None,
            matched_entity=None,
            confidence=0.2,
            strategy="UNRESOLVED",
            reason=f"No high-confidence match found for '{mention.original_text}'. Retaining as unresolved mention.",
        )
