"""
Agent #27 — Technical Documentation & Engineering Publication Agent
Domain schemas: enums, domain models, Input/Output contracts.

Zero-Fabrication invariant: all authority levels and freshness states are
represented by deterministic enums. LLM generates prose only; all metadata,
IDs, revision numbers, and traceability links are set by deterministic code.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ── Status & Lifecycle ─────────────────────────────────────────────────────

class DocumentStatus(str, Enum):
    DRAFT                   = "DRAFT"
    IN_REVIEW               = "IN_REVIEW"
    REVIEW_CHANGES_REQUIRED = "REVIEW_CHANGES_REQUIRED"
    APPROVED                = "APPROVED"
    PUBLISHED               = "PUBLISHED"
    SUPERSEDED              = "SUPERSEDED"
    WITHDRAWN               = "WITHDRAWN"
    ARCHIVED                = "ARCHIVED"


class AuthorityLevel(str, Enum):
    AUTHORITATIVE = "AUTHORITATIVE"
    VERIFIED      = "VERIFIED"
    APPROVED      = "APPROVED"
    REFERENCE     = "REFERENCE"
    UNVERIFIED    = "UNVERIFIED"
    ASSUMPTION    = "ASSUMPTION"
    DRAFT         = "DRAFT"
    UNKNOWN       = "UNKNOWN"


class DocumentFreshness(str, Enum):
    CURRENT                = "CURRENT"
    STALE                  = "STALE"
    REASSESSMENT_REQUIRED  = "REASSESSMENT_REQUIRED"
    SUPERSEDED             = "SUPERSEDED"
    UNKNOWN                = "UNKNOWN"


class DocumentType(str, Enum):
    # Engineering
    SYSTEM_REQUIREMENTS_SPEC       = "SYSTEM_REQUIREMENTS_SPEC"
    INTERFACE_CONTROL_DOCUMENT     = "INTERFACE_CONTROL_DOCUMENT"
    DESIGN_DESCRIPTION             = "DESIGN_DESCRIPTION"
    ARCHITECTURE_DOCUMENT          = "ARCHITECTURE_DOCUMENT"
    TRADE_STUDY_REPORT             = "TRADE_STUDY_REPORT"
    ENGINEERING_CHANGE_NOTICE      = "ENGINEERING_CHANGE_NOTICE"
    DRAWING_PACKAGE                = "DRAWING_PACKAGE"
    # V&V
    TEST_PLAN                      = "TEST_PLAN"
    TEST_REPORT                    = "TEST_REPORT"
    VERIFICATION_CROSS_REF_MATRIX  = "VERIFICATION_CROSS_REF_MATRIX"
    VALIDATION_REPORT              = "VALIDATION_REPORT"
    # Manufacturing
    MANUFACTURING_PLAN             = "MANUFACTURING_PLAN"
    ASSEMBLY_PROCEDURE             = "ASSEMBLY_PROCEDURE"
    QUALITY_CONTROL_PLAN           = "QUALITY_CONTROL_PLAN"
    # Reliability/Risk
    FMEA_REPORT                    = "FMEA_REPORT"
    FAULT_TREE_ANALYSIS            = "FAULT_TREE_ANALYSIS"
    RELIABILITY_PREDICTION_REPORT  = "RELIABILITY_PREDICTION_REPORT"
    HAZARD_ANALYSIS_REPORT         = "HAZARD_ANALYSIS_REPORT"
    # Security
    THREAT_MODEL_DOCUMENT          = "THREAT_MODEL_DOCUMENT"
    SECURITY_ASSESSMENT_REPORT     = "SECURITY_ASSESSMENT_REPORT"
    # Operations
    OPERATIONS_MANUAL              = "OPERATIONS_MANUAL"
    MAINTENANCE_PROCEDURE          = "MAINTENANCE_PROCEDURE"
    DEPLOYMENT_GUIDE               = "DEPLOYMENT_GUIDE"
    # Project
    PROJECT_PLAN                   = "PROJECT_PLAN"
    LESSONS_LEARNED_REPORT         = "LESSONS_LEARNED_REPORT"


class ConflictSeverity(str, Enum):
    BLOCKING  = "BLOCKING"
    MAJOR     = "MAJOR"
    MINOR     = "MINOR"
    INFO      = "INFO"


class PublicationChannel(str, Enum):
    INTERNAL_REVIEW  = "INTERNAL_REVIEW"
    CONTROLLED_VAULT = "CONTROLLED_VAULT"
    EXTERNAL_RELEASE = "EXTERNAL_RELEASE"
    REGULATORY_SUBMISSION = "REGULATORY_SUBMISSION"


# ── Domain Models ──────────────────────────────────────────────────────────

@dataclass
class TraceabilityLink:
    source_id:   str
    target_id:   str
    link_type:   str           # e.g. "satisfies", "verifies", "derives_from"
    authority:   AuthorityLevel = AuthorityLevel.UNKNOWN


@dataclass
class RevisionEntry:
    revision_number: str
    author:          str
    timestamp:       str
    change_summary:  str
    status:          DocumentStatus


@dataclass
class ConflictRecord:
    conflict_id:    str
    field:          str
    doc_a_id:       str
    doc_b_id:       str
    description:    str
    severity:       ConflictSeverity
    resolution:     str = "CONFLICT_DETECTED"   # Never auto-resolved


@dataclass
class QualityFlag:
    flag_id:     str
    category:    str   # e.g. "missing_data", "unverified_claim", "stale_reference"
    description: str
    blocking:    bool = False


@dataclass
class DocumentRecord:
    doc_id:          str
    project_id:      str
    document_type:   DocumentType
    title:           str
    status:          DocumentStatus          = DocumentStatus.DRAFT
    authority:       AuthorityLevel         = AuthorityLevel.UNKNOWN
    freshness:       DocumentFreshness      = DocumentFreshness.UNKNOWN
    revision:        str                    = "00"
    author:          str                    = "UNKNOWN"
    approver:        Optional[str]          = None       # Cannot be same as author
    content_sections: Dict[str, str]        = field(default_factory=dict)
    traceability:    List[TraceabilityLink] = field(default_factory=list)
    revision_history: List[RevisionEntry]  = field(default_factory=list)
    quality_flags:   List[QualityFlag]     = field(default_factory=list)
    conflicts:       List[ConflictRecord]  = field(default_factory=list)
    metadata:        Dict[str, Any]        = field(default_factory=dict)
    export_formats:  List[str]             = field(default_factory=list)


# ── Input / Output Contracts ───────────────────────────────────────────────

@dataclass
class TechDocInput:
    project_id:      str
    operation:       str   # "create_document" | "review_document" | "publish_document" |
                           # "check_traceability" | "detect_conflicts" | "compare_documents" |
                           # "list_documents" | "get_document" | "export_document"
    user_id:         str   = "UNKNOWN"
    document_type:   Optional[str] = None
    title:           Optional[str] = None
    content_inputs:  Dict[str, Any] = field(default_factory=dict)
    doc_id:          Optional[str] = None
    doc_id_b:        Optional[str] = None   # For compare_documents
    export_format:   Optional[str] = None
    authority_claim: Optional[str] = None   # Must be validated; never auto-elevated
    metadata:        Dict[str, Any] = field(default_factory=dict)


@dataclass
class TechDocOutput:
    status:          str    # "ok" | "error" | "conflict_detected" | "access_denied"
    project_id:      str
    operation:       str
    document:        Optional[DocumentRecord]  = None
    documents:       List[DocumentRecord]      = field(default_factory=list)
    conflicts:       List[ConflictRecord]      = field(default_factory=list)
    quality_flags:   List[QualityFlag]         = field(default_factory=list)
    quality_score:   Optional[float]           = None
    export_payload:  Optional[Dict[str, Any]]  = None
    summary:         str                       = ""
    warnings:        List[str]                 = field(default_factory=list)
    errors:          List[str]                 = field(default_factory=list)
    agent_id:        str                       = "agent.27"

    def _as_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dict (enums → values, nested dataclasses → dicts)."""
        from dataclasses import fields as dc_fields
        from enum import Enum

        def _conv(obj):
            from dataclasses import is_dataclass
            if is_dataclass(obj) and not isinstance(obj, type):
                return {f.name: _conv(getattr(obj, f.name)) for f in dc_fields(obj)}
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, list):
                return [_conv(i) for i in obj]
            if isinstance(obj, dict):
                return {k: _conv(v) for k, v in obj.items()}
            return obj

        return {f.name: _conv(getattr(self, f.name)) for f in dc_fields(self)}

