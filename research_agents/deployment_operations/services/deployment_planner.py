"""
Sequenced deployment plan generator for physical and software/AI systems.
"""

from typing import List, Optional
from research_agents.deployment_operations.schemas import (
    DeploymentPlan,
    DeploymentStep,
    SystemType,
)


class DeploymentPlanner:
    """Generates ordered deployment plans with verification gates and rollback actions."""

    def create_deployment_plan(
        self,
        project_id: str,
        system_id: str,
        system_type: SystemType,
        target_environment: str = "production",
        is_blocked: bool = False,
    ) -> DeploymentPlan:
        steps: List[DeploymentStep] = []

        # Step 1: Pre-deployment Environment Validation
        steps.append(
            DeploymentStep(
                step_number=1,
                title="Validate Environment & Prerequisites",
                prerequisites=["Environment baseline provisioned", "Access credentials verified"],
                action="Execute automated environment audit and port/power verification.",
                responsible_role="SITE_RELIABILITY_ENGINEER",
                required_tools=["Diagnostic probe / Health CLI"],
                expected_result="All target environmental conditions match approved specification.",
                verification_method="Automated environment validator check",
                rollback_action="Halt deployment; log environmental deficiency",
                requires_authorization=False,
            )
        )

        if system_type in [SystemType.PHYSICAL, SystemType.CYBER_PHYSICAL, SystemType.HYBRID]:
            # Step 2: Physical Mounting & Installation
            steps.append(
                DeploymentStep(
                    step_number=2,
                    title="Physical Assembly, Mounting & Enclosure Alignment",
                    prerequisites=["Step 1 passed", "Clearance and structural foundation inspected"],
                    action="Mount physical chassis to rack/foundation and torque all fasteners to specification.",
                    responsible_role="FIELD_HARDWARE_TECHNICIAN",
                    required_tools=["Calibrated torque wrench", "Level gauge", "Alignment pins"],
                    expected_result="Chassis securely fastened within allowable alignment tolerances.",
                    verification_method="Mechanical inspection against CAD mounting envelope",
                    rollback_action="Disassemble mechanical fixtures; return to staging",
                    requires_authorization=False,
                )
            )
            # Step 3: Power & Wiring Connections
            steps.append(
                DeploymentStep(
                    step_number=3,
                    title="Electrical Power & Signal Interconnect",
                    prerequisites=["Step 2 passed", "Lockout/Tagout (LOTO) active"],
                    action="Connect primary and redundant power feeds; connect differential signal lines.",
                    responsible_role="LICENSED_ELECTRICIAN_OR_TECH",
                    required_tools=["Digital multimeter", "ESD ground strap"],
                    expected_result="Input bus voltage within nominal range; zero short circuits.",
                    verification_method="Cold resistance check before energization",
                    rollback_action="Disconnect power harnesses; re-apply isolation lock",
                    requires_authorization=True,
                )
            )

        if system_type in [SystemType.SOFTWARE, SystemType.AI_AGENT, SystemType.CYBER_PHYSICAL, SystemType.HYBRID]:
            # Step 4: Software / Agent Runtime Deployment
            steps.append(
                DeploymentStep(
                    step_number=len(steps) + 1,
                    title="Deploy Application & Agent Control Fabric Artifacts",
                    prerequisites=["Step 1 passed", "Artifact signatures validated"],
                    action="Apply container manifests and register agent descriptor in Unified Control Fabric.",
                    responsible_role="DEVOPS_ENGINEER",
                    required_tools=["Control Fabric CLI / Orchestration Runner"],
                    expected_result="All agent pods and service nodes report healthy state.",
                    verification_method="Health endpoint probe and A2A handshake",
                    rollback_action="Revert to previous container image tag and unregister new agent version",
                    requires_authorization=True,
                )
            )

        # Commissioning & Baseline Step
        steps.append(
            DeploymentStep(
                step_number=len(steps) + 1,
                title="Execute Commissioning Verification Suite",
                prerequisites=["Installation steps complete"],
                action="Run formal end-to-end commissioning tests across all functional modes.",
                responsible_role="COMMISSIONING_LEAD",
                required_tools=["Automated test harness"],
                expected_result="100% of required commissioning tests achieve PASS state.",
                verification_method="Agent #18 verification evidence capture",
                rollback_action="Isolate system to DIAGNOSTIC mode; prevent production traffic",
                requires_authorization=True,
            )
        )

        return DeploymentPlan(
            plan_id=f"DEP-PLAN-{system_id}",
            project_id=project_id,
            system_id=system_id,
            system_type=system_type,
            target_environment=target_environment,
            steps=steps,
            estimated_duration_minutes=45.0 if system_type == SystemType.SOFTWARE else 180.0,
            blockers=["Deployment readiness is BLOCKED: see readiness report"] if is_blocked else [],
        )
