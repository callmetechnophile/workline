"""
Maintenance planning and serviceability analysis engine.
"""

from typing import List
from research_agents.deployment_operations.schemas import (
    MaintenanceTask,
    MaintenanceType,
    ServiceabilityEvaluation,
    ServiceabilityRating,
    SystemType,
)


class MaintenanceServiceabilityEngine:
    """Creates preventive/corrective maintenance plans and audits serviceability."""

    def create_maintenance_tasks(
        self,
        system_id: str,
        system_type: SystemType,
    ) -> List[MaintenanceTask]:
        tasks: List[MaintenanceTask] = []

        if system_type in [SystemType.PHYSICAL, SystemType.CYBER_PHYSICAL, SystemType.HYBRID]:
            tasks.append(
                MaintenanceTask(
                    task_id="MAINT-PREV-01",
                    component_id="CHASSIS_AIR_FILTER",
                    maintenance_type=MaintenanceType.PREVENTIVE,
                    action="Inspect and replace chassis particulate intake filter",
                    interval="90_DAYS",
                    required_tools=["Screwdriver Phillips #2"],
                    required_spares=["FILTER-ELEM-01"],
                    skill_level="TECHNICIAN",
                    safety_prerequisite="Ensure fan intake is clear of debris before opening cowl.",
                )
            )
            tasks.append(
                MaintenanceTask(
                    task_id="MAINT-COND-02",
                    component_id="COOLING_FAN_BEARINGS",
                    maintenance_type=MaintenanceType.CONDITION_BASED,
                    action="Check fan vibration levels; lubricate or replace blower assembly if noise > 60dB",
                    interval="MAINTENANCE_INTERVAL_UNKNOWN",
                    required_tools=["Acoustic/vibration probe"],
                    required_spares=["FAN-ASSY-12V"],
                    skill_level="MAINTENANCE_TECH",
                    safety_prerequisite="LOTO electrical power disconnect before servicing rotating fan blades.",
                )
            )

        if system_type in [SystemType.SOFTWARE, SystemType.AI_AGENT, SystemType.CYBER_PHYSICAL, SystemType.HYBRID]:
            tasks.append(
                MaintenanceTask(
                    task_id="MAINT-SW-01",
                    component_id="SURREALDB_COMPACT",
                    maintenance_type=MaintenanceType.PREVENTIVE,
                    action="Compact graph storage index and purge expired ephemeral logs",
                    interval="30_DAYS",
                    required_tools=["Database CLI client"],
                    required_spares=[],
                    skill_level="DATABASE_ADMIN",
                    safety_prerequisite="Perform full backup snapshot prior to executing index compaction.",
                )
            )

        return tasks

    def evaluate_serviceability(
        self,
        system_id: str,
        system_type: SystemType,
    ) -> List[ServiceabilityEvaluation]:
        evals: List[ServiceabilityEvaluation] = []

        if system_type in [SystemType.PHYSICAL, SystemType.CYBER_PHYSICAL, SystemType.HYBRID]:
            evals.append(
                ServiceabilityEvaluation(
                    subsystem_id="POWER_SUPPLY_MODULE",
                    rating=ServiceabilityRating.SERVICEABILITY_ACCEPTABLE,
                    access_notes="Module slide-mounted on rear panel with quick-disconnect Anderson power poles.",
                    replaceability_notes="Mean time to replace (MTTR) estimated under 10 minutes without dismounting main enclosure.",
                    concerns=[],
                )
            )
            evals.append(
                ServiceabilityEvaluation(
                    subsystem_id="INTERNAL_SENSOR_HARNESS",
                    rating=ServiceabilityRating.SERVICEABILITY_CONCERN,
                    access_notes="Routing passes behind structural bracket; requires removing 4 chassis fasteners.",
                    replaceability_notes="Service access is constrained; recommend captive thumbscrews.",
                    concerns=["Tight clearance near chassis bend radius"],
                )
            )
        else:
            evals.append(
                ServiceabilityEvaluation(
                    subsystem_id="CONTAINER_RUNTIME_LOGS",
                    rating=ServiceabilityRating.SERVICEABILITY_ACCEPTABLE,
                    access_notes="Centralized telemetry streaming enabled via standard stdout JSON logs.",
                    replaceability_notes="Seamless rolling update supported without client interruption.",
                    concerns=[],
                )
            )

        return evals
