"""
Change-driven simulation invalidation and re-simulation planning engine (Sections 60–62, 100).
"""

from typing import List, Tuple
from research_agents.engineering_simulation.schemas import ModelObject, SimulationObject


class ReSimulationEngine:
    """Detects invalidation impacts from upstream changes and plans re-simulations."""

    def process_change_impact(
        self,
        target_artifact: str,
        models: List[ModelObject],
        simulations: List[SimulationObject],
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Returns:
            (stale_models, invalidated_simulations, required_resimulations)
        """
        stale_models: List[str] = []
        invalidated_sims: List[str] = []
        required_resim: List[str] = []

        for m in models:
            if target_artifact.lower() in m.description.lower() or target_artifact.lower() in str(m.parameters).lower():
                stale_models.append(m.model_id)

        for s in simulations:
            if s.model_id in stale_models or target_artifact.lower() in str(s.inputs).lower():
                invalidated_sims.append(s.simulation_id)
                required_resim.append(s.simulation_id)

        return stale_models, invalidated_sims, required_resim
