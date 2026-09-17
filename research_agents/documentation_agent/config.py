"""
Agent #27 — Technical Documentation & Engineering Publication Agent
Configuration constants. All thresholds are policy, not invented engineering truth.
"""

from dataclasses import dataclass, field
from typing import List


AGENT_ID   = "agent.27"
AGENT_NAME = "TechDocAgent"
AGENT_VERSION = "1.0.0"

# Document-ID prefix
DOC_ID_PREFIX = "DOC"

# Revision numbering
REVISION_INITIAL   = "00"
REVISION_SEPARATOR = "."

# Quality thresholds (policy-defined)
MIN_QUALITY_SCORE_FOR_REVIEW   = 0.60
MIN_QUALITY_SCORE_FOR_APPROVAL = 0.75
MIN_QUALITY_SCORE_FOR_PUBLISH  = 0.80

# LLM temperature for prose generation
LLM_TEMPERATURE = 0.1

# Supported export formats
SUPPORTED_FORMATS = ["pdf", "docx", "html", "markdown", "json"]

# Max revision history entries kept in memory
MAX_REVISION_HISTORY = 100


@dataclass
class TechDocConfig:
    agent_id:     str        = AGENT_ID
    agent_name:   str        = AGENT_NAME
    agent_version: str       = AGENT_VERSION
    doc_id_prefix: str       = DOC_ID_PREFIX
    llm_temperature: float   = LLM_TEMPERATURE
    supported_formats: List[str] = field(default_factory=lambda: list(SUPPORTED_FORMATS))
    min_quality_review:   float  = MIN_QUALITY_SCORE_FOR_REVIEW
    min_quality_approval: float  = MIN_QUALITY_SCORE_FOR_APPROVAL
    min_quality_publish:  float  = MIN_QUALITY_SCORE_FOR_PUBLISH
