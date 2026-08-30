"""
Verification repository interface and in-memory implementation for SurrealDB persistence preparation (Section 71).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from research_agents.verification_qa_agent.schemas import (
    CorrectionReportItem,
    EvidenceObject,
    FinalQAVerdict,
    RequirementVerificationItem,
    TestResultObject,
    VerificationQAAgentOutput,
    VerificationTraceabilityItem,
)


class VerificationRepository(ABC):
    """Abstract repository for persisting QA verification records and evidence."""

    @abstractmethod
    async def save_verification(self, output: VerificationQAAgentOutput) -> str:
        """Persists complete verification run."""
        pass

    @abstractmethod
    async def get_verification(self, verification_id: str) -> Optional[VerificationQAAgentOutput]:
        """Retrieves a stored verification run."""
        pass

    @abstractmethod
    async def save_test_result(self, test_res: TestResultObject, verification_id: str) -> None:
        """Persists individual test result."""
        pass

    @abstractmethod
    async def save_requirement_result(self, req_res: RequirementVerificationItem, verification_id: str) -> None:
        """Persists requirement coverage evaluation."""
        pass

    @abstractmethod
    async def save_failure(self, correction: CorrectionReportItem, verification_id: str) -> None:
        """Persists failure and correction request."""
        pass

    @abstractmethod
    async def save_evidence(self, evidence: EvidenceObject, verification_id: str) -> None:
        """Persists verification evidence."""
        pass

    @abstractmethod
    async def save_traceability(self, trace: VerificationTraceabilityItem, verification_id: str) -> None:
        """Persists requirement-to-evidence traceability."""
        pass

    @abstractmethod
    async def save_qa_verdict(self, verdict: FinalQAVerdict, verification_id: str) -> None:
        """Persists final QA quality gate verdict."""
        pass


class InMemoryVerificationRepository(VerificationRepository):
    """In-memory storage implementation for local test suites."""

    def __init__(self):
        self.verifications: Dict[str, VerificationQAAgentOutput] = {}
        self.tests: Dict[str, List[TestResultObject]] = {}
        self.requirements: Dict[str, List[RequirementVerificationItem]] = {}
        self.failures: Dict[str, List[CorrectionReportItem]] = {}
        self.evidence_items: Dict[str, List[EvidenceObject]] = {}
        self.traceability_items: Dict[str, List[VerificationTraceabilityItem]] = {}
        self.verdicts: Dict[str, FinalQAVerdict] = {}

    async def save_verification(self, output: VerificationQAAgentOutput) -> str:
        self.verifications[output.verification_id] = output
        return output.verification_id

    async def get_verification(self, verification_id: str) -> Optional[VerificationQAAgentOutput]:
        return self.verifications.get(verification_id)

    async def save_test_result(self, test_res: TestResultObject, verification_id: str) -> None:
        if verification_id not in self.tests:
            self.tests[verification_id] = []
        self.tests[verification_id].append(test_res)

    async def save_requirement_result(self, req_res: RequirementVerificationItem, verification_id: str) -> None:
        if verification_id not in self.requirements:
            self.requirements[verification_id] = []
        self.requirements[verification_id].append(req_res)

    async def save_failure(self, correction: CorrectionReportItem, verification_id: str) -> None:
        if verification_id not in self.failures:
            self.failures[verification_id] = []
        self.failures[verification_id].append(correction)

    async def save_evidence(self, evidence: EvidenceObject, verification_id: str) -> None:
        if verification_id not in self.evidence_items:
            self.evidence_items[verification_id] = []
        self.evidence_items[verification_id].append(evidence)

    async def save_traceability(self, trace: VerificationTraceabilityItem, verification_id: str) -> None:
        if verification_id not in self.traceability_items:
            self.traceability_items[verification_id] = []
        self.traceability_items[verification_id].append(trace)

    async def save_qa_verdict(self, verdict: FinalQAVerdict, verification_id: str) -> None:
        self.verdicts[verification_id] = verdict
