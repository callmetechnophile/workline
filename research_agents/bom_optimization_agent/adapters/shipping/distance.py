"""
Distance calculation service for major Indian logistics hubs (Section 15).
"""

from typing import Dict, Tuple
from research_agents.bom_optimization_agent.schemas import Location


class DistanceMatrixService:
    """Provides road and air transport distance estimates between major Indian cities."""

    # Approximate road distance matrix in km between hubs
    DISTANCES: Dict[Tuple[str, str], float] = {
        ("pune", "bengaluru"): 840.0,
        ("bengaluru", "pune"): 840.0,
        ("mumbai", "bengaluru"): 980.0,
        ("bengaluru", "mumbai"): 980.0,
        ("delhi", "bengaluru"): 2150.0,
        ("bengaluru", "delhi"): 2150.0,
        ("hyderabad", "bengaluru"): 570.0,
        ("bengaluru", "hyderabad"): 570.0,
        ("chennai", "bengaluru"): 350.0,
        ("bengaluru", "chennai"): 350.0,
        ("kochi", "bengaluru"): 550.0,
        ("bengaluru", "kochi"): 550.0,
        ("pune", "mumbai"): 150.0,
        ("mumbai", "pune"): 150.0,
        ("pune", "delhi"): 1450.0,
        ("delhi", "pune"): 1450.0,
    }

    def get_distance_km(self, origin: Location, destination: Location) -> float:
        """Returns distance in km between two locations, or default estimate if unmapped."""
        orig_city = (origin.city or "").strip().lower()
        dest_city = (destination.city or "").strip().lower()

        if orig_city == dest_city:
            return 25.0  # Intra-city local transit

        pair = (orig_city, dest_city)
        if pair in self.DISTANCES:
            return self.DISTANCES[pair]

        # Generic inter-state fallback
        return 1000.0
