"""
Component role mapping service for EngineeringArchitectureAgent (Sections 8 & 9).
Maps components to architectural roles with mandatory/optional status tags.
"""

from typing import Any, Dict, List
from research_agents.engineering_architecture_agent.schemas import ComponentRoleItem, SubsystemItem


class ComponentRoleMapper:
    """Assigns functional roles and criticality status to components."""

    def map_roles(
        self,
        subsystems: List[SubsystemItem],
        decisions: List[Dict[str, Any]],
        project_components: List[str],
    ) -> List[ComponentRoleItem]:
        """
        Maps components to their designated subsystems and architectural roles.
        """
        role_items: List[ComponentRoleItem] = []

        for sub in subsystems:
            for comp in sub.components:
                # Determine role & status based on subsystem
                role = "primary_processor" if "Compute" in sub.name else (
                    "primary_sensor" if "Sensing" in sub.name else (
                        "power_converter" if "Power" in sub.name else "controller"
                    )
                )

                # Link supporting decisions if any
                matching_decs = [
                    d.get("decision_id", "") for d in decisions
                    if comp.lower() in str(d.get("selected_option", "")).lower()
                ]

                role_items.append(
                    ComponentRoleItem(
                        component=comp,
                        role=role,
                        subsystem_id=sub.subsystem_id,
                        status="mandatory",
                        reason=f"Assigned to {sub.name} to fulfill: {', '.join(sub.responsibilities[:2])}",
                        supporting_decision_ids=[d for d in matching_decs if d],
                        confidence=0.95,
                    )
                )

        return role_items
