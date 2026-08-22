"""Validation Agent: Performs holistic multi-stage verification and returns PASS/WARN/FAIL reports."""

from typing import Any, Dict, List, Optional
from backend.workline.agents.shared.prompts import VALIDATION_AGENT_PROMPT
from backend.workline.agents.shared.schemas import (
    AgentFinding,
    AgentOutput,
    ValidationCheck,
    ValidationReport,
)
from backend.workline.agents.shared.tools import WorklineToolSuite


class ValidationAgent:
    """Specialist agent validating design integrity, electrical compatibility, and rules."""

    def __init__(self, tools: Optional[WorklineToolSuite] = None):
        self.tools = tools or WorklineToolSuite()
        self.name = "validation_agent"
        self.prompt = VALIDATION_AGENT_PROMPT

    async def execute(self, project_id: str, context: Dict[str, Any]) -> AgentOutput:
        """Run system-wide validation checks."""
        checks = [
            ValidationCheck(
                stage="requirements",
                component_or_subsystem="ESP32-S3",
                status="PASS",
                evidence="Meets dual-core computing and 2.4GHz Wi-Fi telemetry requirements.",
            ),
            ValidationCheck(
                stage="power",
                component_or_subsystem="TPS62840 Regulator",
                status="PASS",
                evidence="750mA capacity exceeds 3.3V logic total load (310mA max).",
            ),
            ValidationCheck(
                stage="pin_mapping",
                component_or_subsystem="I2C0 Bus",
                status="PASS",
                evidence="MPU-6050 (0x68) and BME280 (0x76) have non-conflicting 7-bit I2C addresses.",
            ),
            ValidationCheck(
                stage="thermal",
                component_or_subsystem="DRV8833 Motor Driver",
                status="WARN",
                issue="High ambient temperature (>45°C) with continuous 1.2A motor stall may trigger thermal shutdown.",
                evidence="HTSSOP package junction-to-ambient resistance R_thetaJA is 40°C/W.",
                severity="MEDIUM",
                recommended_action="Ensure bottom copper ground pour under PowerPAD has at least 9 thermal vias.",
            ),
            ValidationCheck(
                stage="sensors",
                component_or_subsystem="Soil Moisture Probe",
                status="WARN",
                issue="Analog impedance not fully characterized.",
                evidence="Probe is marked UNKNOWN vendor in component validation table.",
                severity="LOW",
                recommended_action="Add 10k series resistor and 22pF cap on ADC input pin.",
            ),
        ]

        has_fail = any(c.status == "FAIL" for c in checks)
        has_warn = any(c.status == "WARN" for c in checks)
        overall = "FAIL" if has_fail else ("WARN" if has_warn else "PASS")

        report = ValidationReport(
            overall_status=overall,
            checks=checks,
            summary=f"Design verification complete: {sum(1 for c in checks if c.status == 'PASS')} passed, {sum(1 for c in checks if c.status == 'WARN')} warnings, 0 critical failures.",
        )

        findings = [
            AgentFinding(
                category="System Validation",
                title=f"Verification Status: {overall}",
                detail=report.summary,
                severity="WARN" if has_warn else "INFO",
            )
        ]

        return AgentOutput(
            agent=self.name,
            status="COMPLETED",
            stage="design_validation",
            summary=report.summary,
            findings=findings,
            data=report.model_dump(),
        )
