"""
Operational dependency and Single Point of Failure (SPOF) analysis engine.
"""

from typing import List, Optional
from research_agents.deployment_operations.schemas import (
    OperationalDependency,
    SystemType,
)


class DependencyEngine:
    """Maps operational dependencies and detects critical single points of failure."""

    def analyze_dependencies(
        self,
        system_id: str,
        system_type: SystemType,
        custom_deps: Optional[List[OperationalDependency]] = None,
    ) -> List[OperationalDependency]:
        if custom_deps:
            return custom_deps

        deps: List[OperationalDependency] = []

        # Platform dependencies
        deps.append(
            OperationalDependency(
                dep_id="DEP-SURREALDB",
                system_id=system_id,
                target_service_or_component="SurrealDB Graph Database",
                dependency_type="DATABASE",
                is_critical=True,
                is_single_point_of_failure=False,
                fallback_available=True,  # in-memory fallback
            )
        )
        deps.append(
            OperationalDependency(
                dep_id="DEP-BEDROCK",
                system_id=system_id,
                target_service_or_component="Amazon Bedrock Inference",
                dependency_type="INFERENCE",
                is_critical=True,
                is_single_point_of_failure=False,
                fallback_available=True,  # mock/heuristic fallback
            )
        )
        deps.append(
            OperationalDependency(
                dep_id="DEP-FABRIC",
                system_id=system_id,
                target_service_or_component="Unified Agent Control Fabric",
                dependency_type="FABRIC",
                is_critical=True,
                is_single_point_of_failure=True,
                fallback_available=False,
            )
        )

        if system_type in [SystemType.PHYSICAL, SystemType.CYBER_PHYSICAL, SystemType.HYBRID]:
            deps.append(
                OperationalDependency(
                    dep_id="DEP-MAINS-POWER",
                    system_id=system_id,
                    target_service_or_component="Primary Grid AC Power",
                    dependency_type="POWER",
                    is_critical=True,
                    is_single_point_of_failure=True,
                    fallback_available=False,  # unless UPS is configured
                )
            )

        return deps
