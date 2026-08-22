"""Deterministic technical validator: Hard programmatic verification for electrical, interface, and package fit."""

from typing import List, Tuple
from backend.workline.procurement.models import (
    CheckStatus,
    ComponentCandidate,
    ComponentRequirement,
    DeterministicValidationReport,
    ValidationCheck,
)


class TechnicalValidator:
    """Programmatic validator verifying candidate component specifications against engineering requirements."""

    def validate(
        self,
        candidate: ComponentCandidate,
        requirement: ComponentRequirement,
    ) -> DeterministicValidationReport:
        checks: List[ValidationCheck] = []
        warnings: List[str] = []
        is_compatible = True

        # 1. Voltage Range Check
        if requirement.nominal_voltage is not None:
            c_nom = candidate.electrical.nominal_voltage
            c_min = candidate.electrical.voltage_min
            c_max = candidate.electrical.voltage_max

            if c_nom is not None:
                if abs(c_nom - requirement.nominal_voltage) > 0.3:
                    checks.append(
                        ValidationCheck(
                            check_name="Nominal Voltage",
                            status=CheckStatus.FAIL,
                            expected=f"{requirement.nominal_voltage}V",
                            actual=f"{c_nom}V",
                            explanation=f"Nominal output/operating voltage {c_nom}V does not match requirement {requirement.nominal_voltage}V.",
                        )
                    )
                    is_compatible = False
                else:
                    checks.append(
                        ValidationCheck(
                            check_name="Nominal Voltage",
                            status=CheckStatus.PASS,
                            expected=f"{requirement.nominal_voltage}V",
                            actual=f"{c_nom}V",
                            explanation="Nominal voltage matches within tolerance.",
                        )
                    )
            elif c_min is not None and c_max is not None:
                if not (c_min <= requirement.nominal_voltage <= c_max):
                    checks.append(
                        ValidationCheck(
                            check_name="Voltage Operating Range",
                            status=CheckStatus.FAIL,
                            expected=f"{requirement.nominal_voltage}V within [{c_min}V - {c_max}V]",
                            actual=f"[{c_min}V - {c_max}V]",
                            explanation="Required voltage falls outside candidate operating range.",
                        )
                    )
                    is_compatible = False
                else:
                    checks.append(
                        ValidationCheck(
                            check_name="Voltage Operating Range",
                            status=CheckStatus.PASS,
                            expected=f"{requirement.nominal_voltage}V within [{c_min}V - {c_max}V]",
                            actual=f"[{c_min}V - {c_max}V]",
                            explanation="Operating voltage is well within candidate range.",
                        )
                    )
            else:
                checks.append(
                    ValidationCheck(
                        check_name="Voltage Check",
                        status=CheckStatus.UNKNOWN,
                        expected=f"{requirement.nominal_voltage}V",
                        actual="UNKNOWN",
                        explanation="Datasheet voltage range could not be definitively extracted.",
                    )
                )
                warnings.append("Datasheet voltage limits unknown; manual review recommended.")

        # 2. Current Capacity Check
        if requirement.required_current_min_a is not None:
            c_cur = candidate.electrical.current_max or candidate.electrical.current
            if c_cur is not None:
                if c_cur < requirement.required_current_min_a:
                    checks.append(
                        ValidationCheck(
                            check_name="Current Capacity",
                            status=CheckStatus.FAIL,
                            expected=f">= {requirement.required_current_min_a}A",
                            actual=f"{c_cur}A",
                            explanation=f"Candidate maximum current {c_cur}A is below required {requirement.required_current_min_a}A.",
                        )
                    )
                    is_compatible = False
                else:
                    checks.append(
                        ValidationCheck(
                            check_name="Current Capacity",
                            status=CheckStatus.PASS,
                            expected=f">= {requirement.required_current_min_a}A",
                            actual=f"{c_cur}A",
                            explanation=f"Candidate current capacity {c_cur}A satisfies requirement.",
                        )
                    )
            else:
                checks.append(
                    ValidationCheck(
                        check_name="Current Capacity",
                        status=CheckStatus.UNKNOWN,
                        expected=f">= {requirement.required_current_min_a}A",
                        actual="UNKNOWN",
                        explanation="Max output current not specified in extracted summary.",
                    )
                )
                warnings.append("Current capacity unknown.")

        # 3. Interface Compatibility Check
        for req_if in requirement.required_interfaces:
            if_clean = req_if.lower()
            supported = False
            if if_clean == "i2c" and candidate.interfaces.i2c:
                supported = True
            elif if_clean == "spi" and candidate.interfaces.spi:
                supported = True
            elif if_clean == "uart" and candidate.interfaces.uart:
                supported = True
            elif if_clean == "can" and candidate.interfaces.can:
                supported = True
            elif if_clean == "usb" and candidate.interfaces.usb:
                supported = True
            elif if_clean in ("pwm", "motor") and (candidate.interfaces.pwm_channels or "pwm" in str(candidate.description).lower()):
                supported = True
            elif if_clean in ("adc", "analog") and (candidate.interfaces.adc_channels or "analog" in str(candidate.description).lower()):
                supported = True

            if supported:
                checks.append(
                    ValidationCheck(
                        check_name=f"Interface: {req_if.upper()}",
                        status=CheckStatus.PASS,
                        expected=req_if.upper(),
                        actual=req_if.upper(),
                        explanation=f"Candidate natively supports {req_if.upper()} interface.",
                    )
                )
            else:
                checks.append(
                    ValidationCheck(
                        check_name=f"Interface: {req_if.upper()}",
                        status=CheckStatus.FAIL,
                        expected=req_if.upper(),
                        actual="Not Supported / Undetected",
                        explanation=f"Candidate does not support mandatory interface {req_if.upper()}.",
                    )
                )
                is_compatible = False

        # Overall Status
        if not is_compatible or any(c.status == CheckStatus.FAIL for c in checks):
            overall = CheckStatus.FAIL
        elif any(c.status == CheckStatus.WARN for c in checks):
            overall = CheckStatus.WARN
        elif any(c.status == CheckStatus.UNKNOWN for c in checks) and not any(c.status == CheckStatus.PASS for c in checks):
            overall = CheckStatus.UNKNOWN
        else:
            overall = CheckStatus.PASS

        return DeterministicValidationReport(
            overall_status=overall,
            is_compatible=is_compatible,
            checks=checks,
            warnings=warnings,
            evidence={
                "component_id": candidate.component_id,
                "mpn": candidate.manufacturer_part_number,
                "extracted_electrical": candidate.electrical.model_dump(),
                "extracted_interfaces": candidate.interfaces.model_dump(),
            },
        )
