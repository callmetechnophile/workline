"""Routing constraint engine and design rule configuration."""

from typing import Dict, List, Optional
from backend.workline.pcb.models.net import Net, NetClass
from backend.workline.pcb.models.routing import RoutingConstraint, RoutingModel


class RoutingEngine:
    """Manages routing rule assignments, layer preferences, and trace geometry."""

    @staticmethod
    def get_default_routing_rules() -> Dict[str, RoutingConstraint]:
        """Provides default routing constraints for standard net classes."""
        return {
            NetClass.POWER.value: RoutingConstraint(
                id="rule_power",
                net_class=NetClass.POWER,
                trace_width=0.500,     # mm (20 mil) for higher current
                clearance=0.254,       # mm (10 mil)
                preferred_layer="TOP",
                max_via_count=6,
                priority=4,
            ),
            NetClass.GROUND.value: RoutingConstraint(
                id="rule_ground",
                net_class=NetClass.GROUND,
                trace_width=0.500,
                clearance=0.200,
                preferred_layer="L2",  # Dedicated internal plane
                max_via_count=8,
                priority=5,
            ),
            NetClass.HIGH_SPEED.value: RoutingConstraint(
                id="rule_high_speed",
                net_class=NetClass.HIGH_SPEED,
                trace_width=0.200,
                clearance=0.300,       # Extra spacing to prevent crosstalk
                max_length=50.0,       # Length matched
                preferred_layer="TOP",
                max_via_count=2,       # Minimize via impedance discontinuities
                priority=4,
            ),
            NetClass.DIGITAL.value: RoutingConstraint(
                id="rule_digital",
                net_class=NetClass.DIGITAL,
                trace_width=0.254,
                clearance=0.200,
                preferred_layer="TOP",
                max_via_count=4,
                priority=1,
            ),
        }
