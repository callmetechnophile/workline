"""
Isolated what-if scenario engine for EngineeringSimulationAgent (Sections 31–33, 41, 99).
Ensures that exploratory scenario branches NEVER mutate base project BOM, architecture, or state.
"""

from typing import Any, Dict
import uuid
from research_agents.engineering_simulation.schemas import ScenarioObject


class ScenarioEngine:
    """Creates isolated what-if branches for exploratory engineering simulation."""

    def create_scenario(
        self,
        project_id: str,
        name: str,
        description: str,
        changes: Dict[str, Any],
        base_version: str = "v1.0.0",
    ) -> ScenarioObject:
        scen_id = f"SCEN-{uuid.uuid4().hex[:6].upper()}"
        return ScenarioObject(
            scenario_id=scen_id,
            project_id=project_id,
            base_version=base_version,
            name=name,
            description=description,
            changes=changes,
            parameters=changes.get("parameters", {}),
            status="COMPLETE",
        )
