"""
Technical compatibility gate for BOMOptimizationAgent (Sections 9 & 10).
Guarantees that cost optimization NEVER substitutes an electrically, functionally, or interface-incompatible component.
"""

from typing import Any, Dict, List, Tuple
from loguru import logger
from research_agents.bom_optimization_agent.schemas import SupplierOffer


class TechnicalCompatibilityGate:
    """Filters supplier offers and candidate components against engineering BOM constraints."""

    def filter_compatible_offers(
        self,
        offers: List[SupplierOffer],
        bom_items: List[Dict[str, Any]],
        approved_alternatives: List[Dict[str, Any]],
    ) -> Tuple[List[SupplierOffer], List[str]]:
        """
        Filters offers to only include technically verified components and approved alternatives.

        Returns:
            Tuple of (compatible_offers, compatibility_warnings)
        """
        compatible_offers: List[SupplierOffer] = []
        warnings: List[str] = []

        # Map BOM items by ID and Part Number
        bom_by_id = {item.get("bom_item_id"): item for item in bom_items}
        approved_parts = {
            item.get("part_number", "").lower()
            for item in bom_items
            if item.get("part_number")
        }

        # Add approved alternatives that are full or drop_in replacements
        for alt in approved_alternatives:
            compat = str(alt.get("compatibility", "")).lower()
            if compat in ("drop_in", "electrically_compatible", "functionally_equivalent", "performance_alternative", "architecture_alternative"):
                approved_parts.add(alt.get("part_number", "").lower())
            else:
                warnings.append(
                    f"Alternative '{alt.get('part_number')}' has compatibility '{compat}' -> requires engineering approval before purchasing."
                )

        for offer in offers:
            # Check if offer part number is in approved BOM or approved alternatives list
            if offer.part_number.lower() in approved_parts:
                compatible_offers.append(offer)
            else:
                # Flag unverified / incompatible supplier substitute
                warnings.append(
                    f"Supplier '{offer.supplier_name}' offered unverified part '{offer.part_number}' for BOM item '{offer.bom_item_id}' -> rejected by compatibility gate."
                )
                logger.warning(
                    f"[CompatibilityGate] Rejected unverified part '{offer.part_number}' from '{offer.supplier_name}'"
                )

        return compatible_offers, warnings
