"""Agent capabilities, risk levels, and schemas for Workline External Agent Interoperability."""

from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Risk levels associated with agent capabilities."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CapabilityType(str, Enum):
    """Standardized capability classification for internal and external agents."""
    RESEARCH = "RESEARCH"
    CODE_GENERATION = "CODE_GENERATION"
    CODE_REVIEW = "CODE_REVIEW"
    DOCUMENT_ANALYSIS = "DOCUMENT_ANALYSIS"
    DATA_ANALYSIS = "DATA_ANALYSIS"
    SIMULATION = "SIMULATION"
    THERMAL_ANALYSIS = "THERMAL_ANALYSIS"
    PCB_ANALYSIS = "PCB_ANALYSIS"
    SIGNAL_ANALYSIS = "SIGNAL_ANALYSIS"
    OPTIMIZATION = "OPTIMIZATION"
    IMAGE_GENERATION = "IMAGE_GENERATION"
    SPEECH = "SPEECH"
    PLANNING = "PLANNING"


class AgentStatus(str, Enum):
    """Current availability status of an agent."""
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"
    UNKNOWN = "UNKNOWN"
    DISABLED = "DISABLED"


class AgentCapability(BaseModel):
    """Descriptor of a single capability provided by an agent."""
    capability_id: str = Field(..., description="Unique identifier for the capability (e.g. 'thermal_simulation')")
    agent_id: str = Field(..., description="Identifier of the agent providing this capability")
    name: str = Field(..., description="Human-readable capability name")
    description: str = Field(..., description="Detailed description of what the capability performs")
    capability_type: CapabilityType = Field(default=CapabilityType.RESEARCH, description="High-level category")
    input_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for input parameters")
    output_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for expected output result")
    risk_level: RiskLevel = Field(default=RiskLevel.LOW, description="Risk level requiring appropriate authorization")
    estimated_cost: float = Field(default=0.0, description="Estimated cost in USD / micro-payments")
    availability: bool = Field(default=True, description="Whether capability is currently available")
    version: str = Field(default="1.0.0", description="Capability version")
