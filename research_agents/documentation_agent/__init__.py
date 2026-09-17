"""
Agent #27 — Technical Documentation & Engineering Publication Agent

Capabilities:
- Create and manage engineering documents (25+ types)
- Lifecycle: DRAFT → IN_REVIEW → APPROVED → PUBLISHED → SUPERSEDED → ARCHIVED
- Self-approval blocked; controlled publication requires ArmorIQ authorization
- Traceability link management (requirements ↔ verification ↔ implementation)
- Quality scoring with structured QualityFlags (never fabricated)
- Contradiction detection (CONFLICT_DETECTED — never auto-resolved)
- Document comparison and version diffing
- Export: JSON, Markdown, PDF/DOCX placeholders
- Zero Fabrication: LLM generates prose only; metadata is deterministic
"""

from research_agents.documentation_agent.agent  import TechDocAgent
from research_agents.documentation_agent.config import TechDocConfig
from research_agents.documentation_agent.schemas import (
    TechDocInput, TechDocOutput, DocumentRecord,
    DocumentStatus, AuthorityLevel, DocumentFreshness, DocumentType,
)

__all__ = [
    "TechDocAgent", "TechDocConfig",
    "TechDocInput", "TechDocOutput", "DocumentRecord",
    "DocumentStatus", "AuthorityLevel", "DocumentFreshness", "DocumentType",
]
