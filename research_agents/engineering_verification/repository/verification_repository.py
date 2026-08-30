"""
SurrealDB repository for verification plans, tests, results, measurements, and evidence (Sections 63 & 64).
"""

from typing import Any, Dict, List, Optional
from loguru import logger
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.engineering_verification.schemas import (
    EvidenceObject,
    MeasurementObject,
    TestObject,
    TestResult,
    VerificationPlan,
)


class VerificationRepository:
    """SurrealDB graph access repository for engineering verification artifacts."""

    def __init__(self, db_client: Optional[SurrealDBClient] = None):
        self.db = db_client or SurrealDBClient()
        self._memory_plans: Dict[str, VerificationPlan] = {}
        self._memory_tests: Dict[str, TestObject] = {}
        self._memory_results: Dict[str, TestResult] = {}
        self._memory_measurements: Dict[str, MeasurementObject] = {}
        self._memory_evidence: Dict[str, EvidenceObject] = {}

    async def create_plan(self, plan: VerificationPlan) -> VerificationPlan:
        try:
            await self.db.create_node("verification_plan", plan.verification_plan_id, plan.model_dump())
            await self.db.relate_nodes(f"project:{plan.project_id}", "has_verification_plan", f"verification_plan:{plan.verification_plan_id}")
        except Exception as e:
            logger.warning(f"SurrealDB create_plan fallback to memory: {e}")

        self._memory_plans[plan.verification_plan_id] = plan
        return plan

    async def create_test(self, test: TestObject) -> TestObject:
        try:
            await self.db.create_node("test", test.test_id, test.model_dump())
            await self.db.relate_nodes(f"project:{test.project_id}", "has_test", f"test:{test.test_id}")
        except Exception as e:
            logger.warning(f"SurrealDB create_test fallback: {e}")

        self._memory_tests[test.test_id] = test
        return test

    async def create_result(self, result: TestResult) -> TestResult:
        try:
            await self.db.create_node("test_result", result.test_result_id, result.model_dump())
            await self.db.relate_nodes(f"test:{result.test_id}", "produces", f"test_result:{result.test_result_id}")
        except Exception as e:
            logger.warning(f"SurrealDB create_result fallback: {e}")

        self._memory_results[result.test_result_id] = result
        return result

    async def create_measurement(self, measurement: MeasurementObject) -> MeasurementObject:
        try:
            await self.db.create_node("measurement", measurement.measurement_id, measurement.model_dump())
            await self.db.relate_nodes(f"test:{measurement.test_id}", "measures", f"measurement:{measurement.measurement_id}")
        except Exception as e:
            logger.warning(f"SurrealDB create_measurement fallback: {e}")

        self._memory_measurements[measurement.measurement_id] = measurement
        return measurement

    async def create_evidence(self, evidence: EvidenceObject) -> EvidenceObject:
        try:
            await self.db.create_node("evidence", evidence.evidence_id, evidence.model_dump())
        except Exception as e:
            logger.warning(f"SurrealDB create_evidence fallback: {e}")

        self._memory_evidence[evidence.evidence_id] = evidence
        return evidence

    async def invalidate_evidence(self, evidence_id: str) -> Optional[EvidenceObject]:
        if evidence_id in self._memory_evidence:
            self._memory_evidence[evidence_id].status = "INVALIDATED"
            try:
                await self.db.upsert_node("evidence", evidence_id, {"status": "INVALIDATED"})
            except Exception as e:
                logger.warning(f"SurrealDB invalidate evidence fallback: {e}")
            return self._memory_evidence[evidence_id]
        return None

    async def get_tests(self, project_id: str) -> List[TestObject]:
        return [t for t in self._memory_tests.values() if t.project_id == project_id]

    async def get_results(self) -> List[TestResult]:
        return list(self._memory_results.values())

    async def get_evidence(self) -> List[EvidenceObject]:
        return list(self._memory_evidence.values())

    async def get_measurements(self) -> List[MeasurementObject]:
        return list(self._memory_measurements.values())
