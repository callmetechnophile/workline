"""
ArmourIQ Capabilities, Risk Tiers, and Action Models for Google ADK execution governance.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field


class RiskTier(str, Enum):
    """Risk classification tiers for agent and tool actions."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PolicyDecision(str, Enum):
    """ArmourIQ policy evaluation outcome."""
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class AgentCapability(str, Enum):
    """Canonical capabilities governing ADK agents and tools."""
    # Read-only / Low Risk
    READ_RESEARCH = "research.search"
    READ_KNOWLEDGE = "knowledge.query"
    READ_DATASHEET = "datasheet.lookup"
    READ_PROJECT = "project.read"
    LOOKUP_COMPONENT = "component.lookup"
    
    # Medium Risk (Analysis & Simulation)
    ANALYZE_COMPONENT = "component.analyze"
    OPTIMIZE_BOM = "bom.optimize"
    RUN_SIMULATION = "simulation.run"
    VALIDATE_PCB = "pcb.validate"
    ANALYZE_THERMAL = "thermal.analyze"
    ANALYZE_POWER = "power.analyze"
    
    # High Risk (Modifications & External Quotes)
    MODIFY_BOM = "bom.modify"
    MODIFY_PCB = "pcb.modify"
    CREATE_PROCUREMENT_QUOTE = "procurement.quote"
    EXECUTE_EXTERNAL_API = "external.api.execute"
    UPDATE_PROJECT_STATE = "project.update"
    
    # Critical Risk (Financial, Real Orders, Releases)
    EXECUTE_PROCUREMENT = "procurement.order"
    CREATE_RELEASE = "release.create"
    FINANCIAL_TRANSACTION = "financial.transaction"
    SIGN_AUDIT_PACKAGE = "audit.sign_release"


# Mapping from Tool Name / Action to required Capability and default Risk Tier
TOOL_CAPABILITY_MAP: Dict[str, Dict[str, Any]] = {
    # Low Risk
    "search_knowledge_base": {
        "capability": AgentCapability.READ_KNOWLEDGE,
        "risk": RiskTier.LOW,
        "service": "R3_KNOWLEDGE",
    },
    "index_research_document": {
        "capability": AgentCapability.READ_RESEARCH,
        "risk": RiskTier.LOW,
        "service": "R3_KNOWLEDGE",
    },
    "get_project": {
        "capability": AgentCapability.READ_PROJECT,
        "risk": RiskTier.LOW,
        "service": "R1_CORE",
    },
    "get_component": {
        "capability": AgentCapability.LOOKUP_COMPONENT,
        "risk": RiskTier.LOW,
        "service": "R5_PROCUREMENT",
    },
    "search_components": {
        "capability": AgentCapability.LOOKUP_COMPONENT,
        "risk": RiskTier.LOW,
        "service": "R5_PROCUREMENT",
    },
    "query_project_graph": {
        "capability": AgentCapability.READ_KNOWLEDGE,
        "risk": RiskTier.LOW,
        "service": "R3_KNOWLEDGE",
    },
    
    # Medium Risk
    "validate_component": {
        "capability": AgentCapability.ANALYZE_COMPONENT,
        "risk": RiskTier.MEDIUM,
        "service": "R4_ENGINEERING",
    },
    "run_simulation": {
        "capability": AgentCapability.RUN_SIMULATION,
        "risk": RiskTier.MEDIUM,
        "service": "R4_ENGINEERING",
    },
    "validate_pcb": {
        "capability": AgentCapability.VALIDATE_PCB,
        "risk": RiskTier.MEDIUM,
        "service": "R4_ENGINEERING",
    },
    "save_graph_node": {
        "capability": AgentCapability.READ_KNOWLEDGE,
        "risk": RiskTier.MEDIUM,
        "service": "R3_KNOWLEDGE",
    },
    "save_graph_edge": {
        "capability": AgentCapability.READ_KNOWLEDGE,
        "risk": RiskTier.MEDIUM,
        "service": "R3_KNOWLEDGE",
    },
    
    # High Risk
    "save_bom": {
        "capability": AgentCapability.MODIFY_BOM,
        "risk": RiskTier.HIGH,
        "service": "R4_ENGINEERING",
    },
    "update_project_state": {
        "capability": AgentCapability.UPDATE_PROJECT_STATE,
        "risk": RiskTier.HIGH,
        "service": "R1_CORE",
    },
    "create_procurement_quote": {
        "capability": AgentCapability.CREATE_PROCUREMENT_QUOTE,
        "risk": RiskTier.HIGH,
        "service": "R5_PROCUREMENT",
    },
    
    # Critical Risk
    "procurement.order": {
        "capability": AgentCapability.EXECUTE_PROCUREMENT,
        "risk": RiskTier.CRITICAL,
        "service": "R5_PROCUREMENT",
    },
    "execute_procurement_order": {
        "capability": AgentCapability.EXECUTE_PROCUREMENT,
        "risk": RiskTier.CRITICAL,
        "service": "R5_PROCUREMENT",
    },
    "release.create": {
        "capability": AgentCapability.CREATE_RELEASE,
        "risk": RiskTier.CRITICAL,
        "service": "R1_CORE",
    },
    "create_release": {
        "capability": AgentCapability.CREATE_RELEASE,
        "risk": RiskTier.CRITICAL,
        "service": "R1_CORE",
    },
    "financial_transaction": {
        "capability": AgentCapability.FINANCIAL_TRANSACTION,
        "risk": RiskTier.CRITICAL,
        "service": "R5_PROCUREMENT",
    },
}


def get_tool_capability_descriptor(tool_name: str) -> Dict[str, Any]:
    """Retrieve capability, risk tier, and service mapping for a tool."""
    if tool_name in TOOL_CAPABILITY_MAP:
        return TOOL_CAPABILITY_MAP[tool_name]
    
    # Dynamic discovery for parameterized or dot-notation names
    for key, descriptor in TOOL_CAPABILITY_MAP.items():
        if key in tool_name or tool_name.endswith(key):
            return descriptor
            
    # Default conservative posture for unknown tools: HIGH risk
    return {
        "capability": AgentCapability.EXECUTE_EXTERNAL_API,
        "risk": RiskTier.HIGH,
        "service": "UNKNOWN",
    }
