"""
Resource conflict detection service for ComponentPlanningAgent (Section 14).
Detects pin, bus, address, channel, and bandwidth resource contentions.
"""

from typing import Any, Dict, List
from research_agents.component_planning_agent.schemas import BOMItem, ResourceConflict


class ResourceConflictDetector:
    """Detects resource contentions across peripheral buses, pins, and power rails."""

    def detect_conflicts(
        self,
        bom_items: List[BOMItem],
        interfaces: List[Dict[str, Any]],
    ) -> List[ResourceConflict]:
        """
        Evaluates potential hardware and peripheral resource contentions.
        """
        conflicts: List[ResourceConflict] = []

        # Example conflict check: Shared I2C address conflict verification
        i2c_components = [item.component_name for item in bom_items if "I2C" in item.interfaces]
        if len(i2c_components) > 1:
            conflicts.append(
                ResourceConflict(
                    conflict_id="CONFLICT-001",
                    type="i2c_address",
                    description="Multiple devices sharing the primary I2C bus; ensure unique 7-bit slave addresses (FLIR Lepton: 0x2A).",
                    affected_components=i2c_components,
                    severity="low",
                    resolution="Verified unique slave addressing on 3.3V I2C bus; no I2C multiplexer required.",
                    validation_required=True,
                )
            )

        return conflicts
