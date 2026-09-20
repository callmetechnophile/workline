"""
Agent #27 — Technical Documentation & Engineering Publication Agent
Orchestrator: dispatches operations to service layer, enforces invariants.

Invariants:
- LLM generates prose ONLY; deterministic code controls all metadata
- Agent #27 cannot self-approve documents
- Controlled publication requires ArmorIQ authorization
- Authority levels are never silently elevated
- Contradictions are returned as CONFLICT_DETECTED (never auto-resolved)
- Missing data → UNKNOWN or DATA_REQUIRED (never fabricated)
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from research_agents.documentation_agent.config import TechDocConfig
from research_agents.documentation_agent.schemas import (
    AuthorityLevel, DocumentFreshness, DocumentStatus, DocumentType,
    PublicationChannel, TechDocInput, TechDocOutput,
)
from research_agents.documentation_agent.providers.mock_provider import MockDocProvider
from research_agents.documentation_agent.repository.doc_repository import DocRepository
from research_agents.documentation_agent.services import (
    DocumentEngine, TemplateEngine, TraceabilityEngine, RevisionEngine,
    QualityValidator, ContradictionDetector, ComparisonEngine,
    PublicationWorkflow, ReportGenerator, FileExporter,
)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _serialize(obj):
    """Recursively convert dataclasses / enums to plain dicts/lists/scalars."""
    from dataclasses import asdict, fields, is_dataclass
    from enum import Enum
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: _serialize(getattr(obj, f.name)) for f in fields(obj)}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, list):
        return [_serialize(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    return obj


class TechDocAgent:
    """Agent #27 — Technical Documentation & Engineering Publication Agent."""

    AGENT_ID = "agent.27"
    AGENT_NAME = "TechDocAgent"

    def __init__(self, config: TechDocConfig | None = None, provider=None):
        self._config     = config or TechDocConfig()
        self._provider   = provider or MockDocProvider()
        self._repo       = DocRepository()
        self._doc_engine = DocumentEngine(self._provider)
        self._template   = TemplateEngine()
        self._trace      = TraceabilityEngine()
        self._revision   = RevisionEngine()
        self._quality    = QualityValidator()
        self._conflict   = ContradictionDetector()
        self._compare    = ComparisonEngine()
        self._publication = PublicationWorkflow()
        self._reporter   = ReportGenerator()
        self._exporter   = FileExporter()

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point. Accepts a dict payload or TechDocInput."""
        # Multi-tenant boundary

        if payload.get("unauthorized_project_access") is True:
            return TechDocOutput(
                status="access_denied",
                project_id=payload.get("project_id", "UNKNOWN"),
                operation=payload.get("operation", "UNKNOWN"),
                errors=["PROJECT_ACCESS_DENIED: Multi-tenant boundary violation."],
            )._as_dict()

        inp = TechDocInput(
            project_id      = payload.get("project_id", "UNKNOWN"),
            operation       = payload.get("operation", "list_documents"),
            user_id         = payload.get("user_id", "UNKNOWN"),
            document_type   = payload.get("document_type"),
            title           = payload.get("title"),
            content_inputs  = payload.get("content_inputs", {}),
            doc_id          = payload.get("doc_id"),
            doc_id_b        = payload.get("doc_id_b"),
            export_format   = payload.get("export_format"),
            authority_claim = payload.get("authority_claim"),
            metadata        = payload.get("metadata", {}),
        )

        op = inp.operation

        if op == "create_document":
            return self._create_document(inp)
        elif op == "get_document":
            return self._get_document(inp)
        elif op == "list_documents":
            return self._list_documents(inp)
        elif op == "review_document":
            return self._review_document(inp)
        elif op == "approve_document":
            return self._approve_document(inp)
        elif op == "publish_document":
            return self._publish_document(inp)
        elif op == "check_traceability":
            return self._check_traceability(inp)
        elif op == "detect_conflicts":
            return self._detect_conflicts(inp)
        elif op == "compare_documents":
            return self._compare_documents(inp)
        elif op == "export_document":
            return self._export_document(inp)
        elif op == "quality_check":
            return self._quality_check(inp)
        else:
            return TechDocOutput(
                status="error",
                project_id=inp.project_id,
                operation=op,
                errors=[f"UNKNOWN_OPERATION: {op}"],
            )._as_dict()

    # ── Operations ────────────────────────────────────────────────────────────

    def _create_document(self, inp: TechDocInput) -> Dict[str, Any]:
        try:
            doc_type = DocumentType(inp.document_type or "DESIGN_DESCRIPTION")
        except ValueError:
            doc_type = DocumentType.DESIGN_DESCRIPTION

        # Build section_inputs from template if not provided
        section_inputs = inp.content_inputs or {}
        if not section_inputs:
            for section in self._template.get_sections(doc_type.value):
                section_inputs[section] = {}

        doc = self._doc_engine.create(
            project_id=inp.project_id,
            document_type=doc_type,
            title=inp.title or "Untitled Document",
            author=inp.user_id,
            section_inputs=section_inputs,
            authority_claim=inp.authority_claim,
        )
        self._repo.save(doc)
        score, flags = self._quality.validate(doc)
        doc.quality_flags = flags
        self._repo.save(doc)
        return TechDocOutput(
            status="ok",
            project_id=inp.project_id,
            operation="create_document",
            document=doc,
            quality_score=score,
            quality_flags=flags,
            summary=f"Created {doc.document_type.value} document {doc.doc_id} (rev {doc.revision}).",
        )._as_dict()


    def _get_document(self, inp: TechDocInput) -> Dict[str, Any]:
        doc = self._repo.get(inp.doc_id or "")
        if not doc:
            return TechDocOutput(
                status="error",
                project_id=inp.project_id,
                operation="get_document",
                errors=[f"DOCUMENT_NOT_FOUND: {inp.doc_id}"],
            )._as_dict()

        score, flags = self._quality.validate(doc)
        return TechDocOutput(
            status="ok",
            project_id=inp.project_id,
            operation="get_document",
            document=doc,
            quality_score=score,
            summary=f"Retrieved {doc.doc_id}.",
        )._as_dict()


    def _list_documents(self, inp: TechDocInput) -> Dict[str, Any]:
        docs = self._repo.list_by_project(inp.project_id)
        report = self._reporter.project_doc_summary(docs)
        return TechDocOutput(
            status="ok",
            project_id=inp.project_id,
            operation="list_documents",
            documents=docs,
            summary=f"{len(docs)} documents found.",
            export_payload=report,
        )._as_dict()


    def _review_document(self, inp: TechDocInput) -> Dict[str, Any]:
        doc = self._repo.get(inp.doc_id or "")
        if not doc:
            return TechDocOutput(
                status="error", project_id=inp.project_id, operation="review_document",
                errors=[f"DOCUMENT_NOT_FOUND: {inp.doc_id}"],
            )._as_dict()

        doc, err = self._publication.submit_for_review(doc, inp.user_id)
        if err:
            return TechDocOutput(
                status="error", project_id=inp.project_id, operation="review_document",
                errors=[err],
            )._as_dict()

        self._repo.save(doc)
        return TechDocOutput(
            status="ok", project_id=inp.project_id, operation="review_document",
            document=doc, summary=f"{doc.doc_id} submitted for review.",
        )._as_dict()


    def _approve_document(self, inp: TechDocInput) -> Dict[str, Any]:
        doc = self._repo.get(inp.doc_id or "")
        if not doc:
            return TechDocOutput(
                status="error", project_id=inp.project_id, operation="approve_document",
                errors=[f"DOCUMENT_NOT_FOUND: {inp.doc_id}"],
            )._as_dict()

        doc, err = self._publication.approve(doc, approver=inp.user_id)
        if err:
            return TechDocOutput(
                status="error", project_id=inp.project_id, operation="approve_document",
                errors=[err],
            )._as_dict()

        self._repo.save(doc)
        return TechDocOutput(
            status="ok", project_id=inp.project_id, operation="approve_document",
            document=doc, summary=f"{doc.doc_id} approved by {inp.user_id}.",
        )._as_dict()


    def _publish_document(self, inp: TechDocInput) -> Dict[str, Any]:
        doc = self._repo.get(inp.doc_id or "")
        if not doc:
            return TechDocOutput(
                status="error", project_id=inp.project_id, operation="publish_document",
                errors=[f"DOCUMENT_NOT_FOUND: {inp.doc_id}"],
            )._as_dict()

        channel_str = inp.metadata.get("channel", "INTERNAL_REVIEW")
        try:
            channel = PublicationChannel(channel_str)
        except ValueError:
            channel = PublicationChannel.INTERNAL_REVIEW
        armoriq_authorized = bool(inp.metadata.get("armoriq_authorized", False))
        doc, err = self._publication.publish(doc, inp.user_id, channel, armoriq_authorized)
        if err:
            return TechDocOutput(
                status="error", project_id=inp.project_id, operation="publish_document",
                errors=[err],
            )._as_dict()

        self._repo.save(doc)
        return TechDocOutput(
            status="ok", project_id=inp.project_id, operation="publish_document",
            document=doc, summary=f"{doc.doc_id} published to {channel.value}.",
        )._as_dict()


    def _check_traceability(self, inp: TechDocInput) -> Dict[str, Any]:
        docs = self._repo.list_by_project(inp.project_id)
        report = self._trace.coverage_report(docs)
        if inp.doc_id:
            doc = self._repo.get(inp.doc_id)
            if doc:
                return TechDocOutput(
                    status="ok", project_id=inp.project_id, operation="check_traceability",
                    document=doc, export_payload={"links": [l.__dict__ for l in doc.traceability]},
                    summary=f"{len(doc.traceability)} links on {doc.doc_id}.",
                )._as_dict()

        return TechDocOutput(
            status="ok", project_id=inp.project_id, operation="check_traceability",
            export_payload=report,
            summary=f"Traceability coverage: {report['coverage_pct']:.1f}%.",
        )._as_dict()


    def _detect_conflicts(self, inp: TechDocInput) -> Dict[str, Any]:
        doc_a = self._repo.get(inp.doc_id or "")
        doc_b = self._repo.get(inp.doc_id_b or "")
        if not doc_a or not doc_b:
            return TechDocOutput(
                status="error", project_id=inp.project_id, operation="detect_conflicts",
                errors=["DOCUMENT_NOT_FOUND: one or both documents missing."],
            )._as_dict()

        conflicts = self._conflict.detect(doc_a, doc_b)
        status = "conflict_detected" if conflicts else "ok"
        return TechDocOutput(
            status=status, project_id=inp.project_id, operation="detect_conflicts",
            conflicts=conflicts,
            summary=f"{len(conflicts)} conflict(s) detected between {doc_a.doc_id} and {doc_b.doc_id}.",
        )._as_dict()


    def _compare_documents(self, inp: TechDocInput) -> Dict[str, Any]:
        doc_a = self._repo.get(inp.doc_id or "")
        doc_b = self._repo.get(inp.doc_id_b or "")
        if not doc_a or not doc_b:
            return TechDocOutput(
                status="error", project_id=inp.project_id, operation="compare_documents",
                errors=["DOCUMENT_NOT_FOUND: one or both documents missing."],
            )._as_dict()

        diff = self._compare.compare(doc_a, doc_b)
        return TechDocOutput(
            status="ok", project_id=inp.project_id, operation="compare_documents",
            export_payload=diff,
            summary=f"Compared {doc_a.doc_id} (rev {doc_a.revision}) vs {doc_b.doc_id} (rev {doc_b.revision}).",
        )._as_dict()


    def _export_document(self, inp: TechDocInput) -> Dict[str, Any]:
        doc = self._repo.get(inp.doc_id or "")
        if not doc:
            return TechDocOutput(
                status="error", project_id=inp.project_id, operation="export_document",
                errors=[f"DOCUMENT_NOT_FOUND: {inp.doc_id}"],
            )._as_dict()

        fmt = inp.export_format or "json"
        payload = self._exporter.export(doc, fmt)
        return TechDocOutput(
            status="ok", project_id=inp.project_id, operation="export_document",
            export_payload=payload, summary=f"{doc.doc_id} exported as {fmt}.",
        )._as_dict()


    def _quality_check(self, inp: TechDocInput) -> Dict[str, Any]:
        doc = self._repo.get(inp.doc_id or "")
        if not doc:
            return TechDocOutput(
                status="error", project_id=inp.project_id, operation="quality_check",
                errors=[f"DOCUMENT_NOT_FOUND: {inp.doc_id}"],
            )._as_dict()

        score, flags = self._quality.validate(doc)
        doc.quality_flags = flags
        self._repo.save(doc)
        return TechDocOutput(
            status="ok", project_id=inp.project_id, operation="quality_check",
            document=doc, quality_score=score, quality_flags=flags,
            summary=f"Quality score: {score:.3f}. {len(flags)} flag(s).",
        )._as_dict()

