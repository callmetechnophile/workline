"""
Operational mode and graceful degradation mapping engine.
"""

from typing import Any, Dict, List
from research_agents.deployment_operations.schemas import OperationalMode


class OperationalModeEngine:
    """Defines rules, entry/exit conditions, and permitted behaviors across operational modes."""

    def get_mode_matrix(self) -> Dict[str, Dict[str, Any]]:
        return {
            OperationalMode.NORMAL.value: {
                "permitted": ["Full throughput processing", "Automated deployment verification", "Normal telemetry streaming"],
                "prohibited": ["Live electrical wiring disconnect", "Production database wipe"],
                "exit_condition": "Fault alert triggered or manual shutdown requested",
            },
            OperationalMode.DEGRADED.value: {
                "permitted": ["Local heuristic evaluation", "Cached queries", "Emergency read-only operations"],
                "prohibited": ["High-capacity batch execution", "Production releases"],
                "exit_condition": "Primary subsystem restored and healthy for 5 minutes",
            },
            OperationalMode.MAINTENANCE.value: {
                "permitted": ["Diagnostic routines", "Filter replacement", "Firmware reflashing"],
                "prohibited": ["Routing live production requests"],
                "exit_condition": "Commissioning smoke tests pass and technician signs off",
            },
            OperationalMode.EMERGENCY.value: {
                "permitted": ["Immediate actuator safe-state lock", "Emergency telemetry burst"],
                "prohibited": ["All non-safety operations"],
                "exit_condition": "Manual reset and authorized physical inspection",
            },
        }
