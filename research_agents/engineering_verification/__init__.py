"""
EngineeringVerificationAgent package (Agent #18 of WorkflowGuide AI).
"""

from research_agents.engineering_verification.agent import EngineeringVerificationAgent
from research_agents.engineering_verification.config import VerificationConfig, verification_config
from research_agents.engineering_verification.schemas import (
    EvidenceObject,
    EvidenceTypeLiteral,
    MeasurementObject,
    SimulationObject,
    TestObject,
    TestResult,
    TestStatusLiteral,
    TestTypeLiteral,
    VerificationCoverage,
    VerificationInput,
    VerificationMatrixItem,
    VerificationMethodLiteral,
    VerificationOutput,
    VerificationPlan,
    VerificationStatusLiteral,
)

__all__ = [
    "EngineeringVerificationAgent",
    "VerificationConfig",
    "verification_config",
    "VerificationMethodLiteral",
    "VerificationStatusLiteral",
    "TestTypeLiteral",
    "TestStatusLiteral",
    "EvidenceTypeLiteral",
    "TestObject",
    "MeasurementObject",
    "SimulationObject",
    "EvidenceObject",
    "TestResult",
    "VerificationPlan",
    "VerificationMatrixItem",
    "VerificationCoverage",
    "VerificationInput",
    "VerificationOutput",
]
