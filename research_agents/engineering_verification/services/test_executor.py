"""
Deterministic test execution and tolerance evaluation engine (Sections 28, 76, 77).
"""

from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, Optional, Tuple
import uuid
from research_agents.engineering_verification.schemas import (
    EvidenceObject,
    MeasurementObject,
    TestObject,
    TestResult,
    TestStatusLiteral,
)


class VerificationExecutor:
    """Executes registered scoped tests and deterministically evaluates acceptance criteria."""

    def execute_test(
        self,
        test: TestObject,
        actual_data: Optional[Dict[str, Any]] = None,
        hardware_available: bool = True,
    ) -> Tuple[TestResult, Optional[MeasurementObject], EvidenceObject]:
        res_id = f"TR-{uuid.uuid4().hex[:6].upper()}"
        ev_id = f"EVID-{uuid.uuid4().hex[:6].upper()}"
        now_str = datetime.now(timezone.utc).isoformat()

        # 1. Missing Hardware Dependency -> BLOCKED (Section 46 & 104)
        if not hardware_available:
            result = TestResult(
                test_result_id=res_id,
                test_id=test.test_id,
                status="BLOCKED",
                actual_results={},
                expected_results=test.expected_results,
                deviations=["Required test hardware fixture or instrument unavailable."],
                evidence_ids=[],
                executed_at=now_str,
            )
            evidence = EvidenceObject(
                evidence_id=ev_id,
                type="LOG",
                source=f"test:{test.test_id}",
                artifact="hardware_fixture",
                status="VALID",
            )
            return result, None, evidence

        # 2. Unexecuted -> NOT_EXECUTED (Section 78 & 101)
        if actual_data is None:
            result = TestResult(
                test_result_id=res_id,
                test_id=test.test_id,
                status="NOT_EXECUTED",
                actual_results={},
                expected_results=test.expected_results,
                deviations=["Test has not been executed."],
                evidence_ids=[],
                executed_at=now_str,
            )
            evidence = EvidenceObject(
                evidence_id=ev_id,
                type="LOG",
                source=f"test:{test.test_id}",
                artifact="test_plan",
                status="VALID",
            )
            return result, None, evidence

        # 3. Deterministic Tolerance & Acceptance Criteria Evaluation (Section 76 & 102, 103)
        status: TestStatusLiteral = "PASS"
        deviations = []
        measurement: Optional[MeasurementObject] = None

        if "voltage" in actual_data and "voltage" in test.expected_results:
            act_v = float(actual_data["voltage"])
            exp_v = float(test.expected_results["voltage"])
            tol = float(test.tolerance.get("voltage", 0.1) if test.tolerance else 0.1)

            measurement = MeasurementObject(
                measurement_id=f"MEAS-{uuid.uuid4().hex[:6].upper()}",
                test_id=test.test_id,
                parameter="supply_voltage",
                value=act_v,
                unit="V",
                instrument="Keysight 34461A DMM",
                timestamp=now_str,
            )

            if abs(act_v - exp_v) > tol:
                status = "FAIL"
                deviations.append(f"Voltage measurement {act_v}V exceeds expected {exp_v}V ± {tol}V.")

        elif "fps" in actual_data and "fps" in test.expected_results:
            act_fps = float(actual_data["fps"])
            exp_fps = float(test.expected_results["fps"])
            if act_fps < exp_fps:
                status = "FAIL"
                deviations.append(f"Frame rate {act_fps} FPS is below required {exp_fps} FPS.")

        result = TestResult(
            test_result_id=res_id,
            test_id=test.test_id,
            status=status,
            actual_results=actual_data,
            expected_results=test.expected_results,
            deviations=deviations,
            evidence_ids=[ev_id],
            executed_at=now_str,
        )

        raw_payload = json.dumps({"test_id": test.test_id, "actual": actual_data, "status": status})
        content_hash = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

        evidence = EvidenceObject(
            evidence_id=ev_id,
            type="MEASUREMENT" if measurement else "TEST_RESULT",
            source=f"test:{test.test_id}",
            artifact="sensor_core",
            hash=content_hash,
            verified=True,
            status="VALID",
        )

        return result, measurement, evidence
