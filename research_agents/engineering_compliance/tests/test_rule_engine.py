"""
Unit tests for DesignRuleEngine evaluations across domains (Sections 15–30).
"""

from research_agents.engineering_compliance.schemas import ComplianceRule
from research_agents.engineering_compliance.services.rule_engine import DesignRuleEngine


def test_rule_engine_electrical_and_thermal_evaluations():
    engine = DesignRuleEngine()

    # 1. Electrical Rule PASS
    r_elec = ComplianceRule(
        rule_id="R_ELEC_01",
        project_id="p1",
        name="Voltage Limit",
        description="Voltage check",
        domain="ELECTRICAL",
        severity="CRITICAL",
        expression="v <= max_v",
    )
    res_pass = engine.evaluate_rule(r_elec, {"supply_voltage": 3.3, "max_rated_voltage": 3.3}, "p1")
    assert res_pass.status == "PASS"

    # 2. Electrical Rule FAIL (Over-rating)
    res_fail = engine.evaluate_rule(r_elec, {"supply_voltage": 5.0, "max_rated_voltage": 3.3}, "p1")
    assert res_fail.status == "FAIL"
    assert res_fail.severity == "CRITICAL"

    # 3. Thermal Rule UNKNOWN (Missing limit, Section 19)
    r_therm = ComplianceRule(
        rule_id="R_THERM_01",
        project_id="p1",
        name="Thermal Envelope",
        description="Thermal check",
        domain="THERMAL",
        severity="HIGH",
        expression="t <= max_t",
    )
    res_unk = engine.evaluate_rule(r_therm, {}, "p1")
    assert res_unk.status == "UNKNOWN"

    # 4. Conflicting Specifications REVIEW (Section 37)
    res_rev = engine.evaluate_rule(r_elec, {"has_conflicting_specs": True}, "p1")
    assert res_rev.status == "REVIEW"
