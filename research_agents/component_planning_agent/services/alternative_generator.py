"""
Component alternative generation and classification service for ComponentPlanningAgent (Sections 18 & 19).
"""

from typing import List
from research_agents.component_planning_agent.schemas import BOMItem, ComponentAlternativeItem


class AlternativeGenerator:
    """Extracts and classifies candidate alternative components from BOM items."""

    def generate_alternatives(
        self,
        bom_items: List[BOMItem],
    ) -> List[ComponentAlternativeItem]:
        """
        Gathers all classified alternatives across BOM items.
        """
        all_alternatives: List[ComponentAlternativeItem] = []

        for item in bom_items:
            for alt in item.alternatives:
                all_alternatives.append(alt)

        return all_alternatives
