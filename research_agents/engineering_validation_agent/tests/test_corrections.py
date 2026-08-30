"""
Unit tests for CorrectionGenerator service (Section 49).
"""

from research_agents.engineering_validation_agent.schemas import ValidationItem
from research_agents.engineering_validation_agent.services.correction_generator import CorrectionGenerator


def test_correction_generator_for_blocking_failures():
    generator = CorrectionGenerator()

    failures = [
        ValidationItem(
            validation_id="VAL-001",
            rule_id="RULE-ELEC-001",
            category="electrical",
            status="FAIL",
            severity="CRITICAL",
            title="Logic Voltage Mismatch (5V -> 3.3V)",
            description="Source 5V connects to 3.3V input.",
            affected_components=["SENSOR-5V", "MCU-3V3"],
            affected_subsystems=["SUB-01"],
            recommended_action="Insert a TXS0108E bidirectional level shifter.",
            blocking=True,
        )
    ]

    corrections = generator.generate_corrections(failures)
    assert len(corrections) == 1
    corr = corrections[0]
    assert corr.validation_id == "VAL-001"
    assert corr.blocking is True
    assert "level shifter" in corr.recommended_correction
