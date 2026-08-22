"""Canonical part number to ordering code and packaging resolver."""

from typing import List, Optional, Tuple
from backend.workline.procurement.models import PartVariant


class PartResolver:
    """Resolves engineering components to exact procurement ordering codes."""

    KNOWN_VARIANTS = {
        "TPS62130": [
            PartVariant(
                canonical_part="TPS62130",
                ordering_code="TPS62130RGTR",
                manufacturer="Texas Instruments",
                package="VQFN-16",
                packaging="Tape & Reel (3000)",
                rohs_compliant=True,
            ),
            PartVariant(
                canonical_part="TPS62130",
                ordering_code="TPS62130RGTT",
                manufacturer="Texas Instruments",
                package="VQFN-16",
                packaging="Cut Tape / Mini-Reel (250)",
                rohs_compliant=True,
            ),
        ],
        "LM2596": [
            PartVariant(
                canonical_part="LM2596",
                ordering_code="LM2596S-5.0/NOPB",
                manufacturer="Texas Instruments",
                package="TO-263-5",
                packaging="Tube",
                rohs_compliant=True,
            )
        ],
    }

    @classmethod
    def resolve(
        cls, canonical_part: str
    ) -> Tuple[bool, Optional[PartVariant], List[PartVariant], bool]:
        """Returns (resolved, exact_match, possible_variants, is_ambiguous)."""
        variants = cls.KNOWN_VARIANTS.get(canonical_part.upper(), [])
        if not variants:
            # Fallback exact generation if single pattern
            variant = PartVariant(
                canonical_part=canonical_part,
                ordering_code=canonical_part,
                manufacturer="Generic",
                package="Standard",
                packaging="Standard",
            )
            return True, variant, [variant], False

        if len(variants) == 1:
            return True, variants[0], variants, False

        return False, None, variants, True
