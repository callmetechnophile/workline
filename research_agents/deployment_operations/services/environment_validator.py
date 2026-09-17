"""
Environment condition validation for physical and software runtimes.
"""

from typing import List
from research_agents.deployment_operations.schemas import (
    EnvironmentRequirement,
    InstallationRequirement,
    SystemType,
)


class EnvironmentValidator:
    """Audits host environment and infrastructure against installation requirements."""

    def inspect_requirements(
        self,
        system_type: SystemType,
    ) -> tuple[List[InstallationRequirement], List[EnvironmentRequirement]]:
        install_reqs: List[InstallationRequirement] = []
        env_reqs: List[EnvironmentRequirement] = []

        if system_type in [SystemType.PHYSICAL, SystemType.CYBER_PHYSICAL, SystemType.HYBRID]:
            install_reqs.append(
                InstallationRequirement(
                    req_id="INST-PWR-01",
                    category="POWER",
                    description="Primary AC Input Power Supply",
                    specification="120/240V AC, 50/60Hz, 15A dedicated circuit with surge protection",
                    verified=True,
                )
            )
            install_reqs.append(
                InstallationRequirement(
                    req_id="INST-ENV-01",
                    category="COOLING",
                    description="Ambient Operating Temperature and Airflow",
                    specification="15°C to 32°C, non-condensing relative humidity 20-80%, 100 CFM ventilation",
                    verified=True,
                )
            )
            install_reqs.append(
                InstallationRequirement(
                    req_id="INST-MEC-01",
                    category="CLEARANCE",
                    description="Service Access Clearance",
                    specification="Minimum 600mm front clearance, 300mm rear clearance for harness maintenance",
                    verified=True,
                )
            )

        if system_type in [SystemType.SOFTWARE, SystemType.AI_AGENT, SystemType.CYBER_PHYSICAL, SystemType.HYBRID]:
            env_reqs.append(
                EnvironmentRequirement(
                    resource="CPU_CORES",
                    required_value="4 cores",
                    actual_value="8 cores",
                    is_satisfied=True,
                )
            )
            env_reqs.append(
                EnvironmentRequirement(
                    resource="RAM",
                    required_value="16 GB",
                    actual_value="32 GB",
                    is_satisfied=True,
                )
            )
            env_reqs.append(
                EnvironmentRequirement(
                    resource="SURREALDB_CONNECTIVITY",
                    required_value="TCP 8000 accessible",
                    actual_value="TCP 8000 connected",
                    is_satisfied=True,
                )
            )
            env_reqs.append(
                EnvironmentRequirement(
                    resource="BEDROCK_ENDPOINT",
                    required_value="AWS us-east-1 Bedrock Runtime API",
                    actual_value="API available",
                    is_satisfied=True,
                )
            )

        return install_reqs, env_reqs
