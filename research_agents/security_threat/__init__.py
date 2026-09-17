"""
SecurityThreatModelingAgent (Agent #22).
Cybersecurity Threat Modeling, Attack Surface Discovery, Trust Boundary Analysis,
Security Control Mapping, and Test Generation Engine for WorkflowGuide AI.
"""

from research_agents.security_threat.agent import SecurityThreatModelingAgent
from research_agents.security_threat.schemas import (
    AssetCategoryLiteral,
    AssetClassificationLiteral,
    AssetObject,
    AttackPath,
    AttackSurfaceEntry,
    SecurityControl,
    SecurityDashboardData,
    SecurityDataFlow,
    SecurityGateLiteral,
    SecurityRiskProfile,
    SecurityTestCase,
    ThreatActor,
    ThreatCategoryLiteral,
    ThreatMitigation,
    ThreatObject,
    TrustBoundary,
)

__all__ = [
    "SecurityThreatModelingAgent",
    "AssetObject",
    "ThreatActor",
    "TrustBoundary",
    "AttackSurfaceEntry",
    "SecurityDataFlow",
    "ThreatObject",
    "AttackPath",
    "SecurityControl",
    "ThreatMitigation",
    "SecurityTestCase",
    "SecurityDashboardData",
    "SecurityRiskProfile",
    "AssetCategoryLiteral",
    "AssetClassificationLiteral",
    "ThreatCategoryLiteral",
    "SecurityGateLiteral",
]
