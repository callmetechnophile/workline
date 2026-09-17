"""
Deterministic Mock reasoning provider for EngineeringRiskAgent (Agent #21).
"""

from typing import Any, Dict, List
from research_agents.engineering_risk.providers.base import ReasoningProvider
from research_agents.engineering_risk.schemas import (
    CauseObject,
    ControlObject,
    EffectObject,
    FailureMode,
    RiskMitigation,
    RiskObject,
)


class MockRiskProvider(ReasoningProvider):
    """Deterministic mock reasoning provider for testing and offline execution."""

    async def extract_failure_modes(
        self,
        project_context: Dict[str, Any],
        architecture: Dict[str, Any],
        bom: Dict[str, Any],
        interfaces: List[Dict[str, Any]],
    ) -> List[FailureMode]:
        title = project_context.get("title", "Robotics Edge System")

        # Failure Mode 1: Thermal Throttling / Overheating
        fm1 = FailureMode(
            failure_mode_id="FM-THERMAL-001",
            component_id="COMP-JETSON-01",
            subsystem_id="SUBSYS-COMPUTE",
            description=f"Thermal saturation under peak AI inference in {title}",
            failure_type="PERFORMANCE_DEGRADATION",
            local_effect="SoC junction temperature exceeds 85C; clock throttling occurs",
            system_effect="Vision pipeline frame rate drops below real-time requirement (15 FPS -> 4 FPS)",
            end_effect="Autonomous obstacle avoidance fails to detect obstacles at high velocity",
            effects=EffectObject(
                local_effect="SoC junction temp > 85C",
                subsystem_effect="Compute throughput halved",
                system_effect="Vision FPS drops below 15 FPS",
                end_effect="Collision hazard during high-speed navigation",
            ),
            causes=[
                CauseObject(
                    description="Insufficient heatsink dissipation area under continuous 25W load",
                    category="DESIGN",
                    evidence_status="SUPPORTED",
                    evidence_source="Thermal simulation model SIM-TH-01",
                ),
                CauseObject(
                    description="Ambient operating temperature exceeds 45C in direct sunlight",
                    category="ENVIRONMENT",
                    evidence_status="HYPOTHESIS",
                ),
            ],
            controls=[
                ControlObject(
                    description="Internal SoC dynamic thermal management (DTM) throttling",
                    control_type="DETECTION",
                    implemented=True,
                )
            ],
            detection_methods=["Internal thermal sensor telemetry via I2C bus"],
            is_single_point_failure=True,
            redundancy_present=False,
        )

        # Failure Mode 2: Power Rail Brownout / Voltage Sag
        fm2 = FailureMode(
            failure_mode_id="FM-POWER-001",
            component_id="COMP-PMIC-01",
            subsystem_id="SUBSYS-POWER",
            description="Voltage sag on 5V logic rail during transient motor acceleration",
            failure_type="ELECTRICAL_FAULT",
            local_effect="5V logic bus drops below 4.65V for > 15ms",
            system_effect="Microcontroller resets unexpectedly during flight maneuver",
            end_effect="Loss of attitude control and drone crash",
            effects=EffectObject(
                local_effect="5V bus sags to 4.5V",
                subsystem_effect="MCU brownout reset",
                system_effect="Loss of flight stability",
                end_effect="Catastrophic hull loss",
            ),
            causes=[
                CauseObject(
                    description="High motor startup surge current exceeds battery discharge capability",
                    category="COMPONENT",
                    evidence_status="CONFIRMED",
                    evidence_source="Bench electrical transient test TR-04",
                )
            ],
            controls=[
                ControlObject(
                    description="MCU hardware brownout reset detector",
                    control_type="DETECTION",
                    implemented=True,
                )
            ],
            detection_methods=["Power telemetry and MCU reset reason register flag"],
            is_single_point_failure=True,
            redundancy_present=False,
        )

        return [fm1, fm2]

    async def suggest_mitigations(
        self,
        risk: RiskObject,
        failure_mode: FailureMode,
    ) -> List[RiskMitigation]:
        if "THERMAL" in failure_mode.failure_mode_id:
            return [
                RiskMitigation(
                    mitigation_id="MIT-TH-001",
                    risk_id=risk.risk_id,
                    action="Upgrade to copper-core active heatsink with PWM blower fan",
                    type="PREVENTIVE",
                    priority="HIGH",
                    owner="Hardware Engineering Team",
                    status="PROPOSED",
                    target_reduction={"occurrence": 3, "severity": 0, "detection": 1},
                ),
                RiskMitigation(
                    mitigation_id="MIT-TH-002",
                    risk_id=risk.risk_id,
                    action="Implement software graceful frame-skipping when temperature exceeds 75C",
                    type="COMPENSATING",
                    priority="MEDIUM",
                    owner="Firmware Team",
                    status="PROPOSED",
                    target_reduction={"occurrence": 0, "severity": 2, "detection": 0},
                ),
            ]
        else:
            return [
                RiskMitigation(
                    mitigation_id="MIT-PWR-001",
                    risk_id=risk.risk_id,
                    action="Add 1000uF low-ESR bulk decoupling capacitor bank on 5V logic bus",
                    type="PREVENTIVE",
                    priority="CRITICAL",
                    owner="Electrical Engineering Team",
                    status="PROPOSED",
                    target_reduction={"occurrence": 5, "severity": 0, "detection": 2},
                )
            ]
