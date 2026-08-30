"""
Agent #16: EngineeringChangeControlAgent implementation using Google ADK conventions.
Controls engineering changes, versioning, impact analysis, approvals, and stale artifact propagation.
"""

import asyncio
from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid
from loguru import logger

from research_agents.engineering_change_control.config import change_control_config
from research_agents.engineering_change_control.providers.base import ReasoningProvider
from research_agents.engineering_change_control.providers.bedrock import BedrockChangeControlProvider
from research_agents.engineering_change_control.repository.change_repository import ChangeControlRepository
from research_agents.engineering_change_control.schemas import (
    ApprovalObject,
    ArtifactVersion,
    ChangeControlInput,
    ChangeControlOutput,
    ChangePlan,
    ChangeRequest,
    ChangeSeverityLiteral,
    ChangeTypeLiteral,
    ImpactObject,
    RiskObject,
    RollbackObject,
)
from research_agents.engineering_change_control.services.approval_engine import ChangeApprovalEngine
from research_agents.engineering_change_control.services.conflict_detector import ConflictDetector
from research_agents.engineering_change_control.services.file_exporter import ChangeFileExporter
from research_agents.engineering_change_control.services.impact_engine import ChangeImpactEngine
from research_agents.engineering_change_control.services.report_generator import ChangeReportGenerator
from research_agents.engineering_change_control.services.revalidation_engine import ChangeRevalidationEngine
from research_agents.engineering_change_control.services.risk_analyzer import ChangeRiskAnalyzer
from research_agents.engineering_change_control.services.rollback_manager import RollbackManager
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.engineering_knowledge_graph_agent.services.graph_query import KnowledgeGraphService


class EngineeringChangeControlAgent:
    """
    Google ADK-compliant Engineering Change Control Agent (Agent #16).
    Controls engineering modifications, version propagation, approvals, and graph consistency.
    """

    NAME = "EngineeringChangeControlAgent"
    DESCRIPTION = (
        "Create, analyze, approve, version, propagate, and track controlled "
        "engineering changes across the project knowledge graph."
    )
    CAPABILITIES = [
        "change.create",
        "change.analyze",
        "change.version",
        "change.propagate",
        "change.approve",
        "change.revalidate",
        "graph.read",
        "graph.insert",
        "graph.update",
    ]

    def __init__(
        self,
        db_client: Optional[SurrealDBClient] = None,
        reasoning_provider: Optional[ReasoningProvider] = None,
    ):
        self.db = db_client or SurrealDBClient()
        self.provider = reasoning_provider or BedrockChangeControlProvider()
        self.repo = ChangeControlRepository(self.db)
        self.graph_service = KnowledgeGraphService(self.db)
        self.impact_engine = ChangeImpactEngine()
        self.revalidation_engine = ChangeRevalidationEngine()
        self.risk_analyzer = ChangeRiskAnalyzer()
        self.approval_engine = ChangeApprovalEngine()
        self.conflict_detector = ConflictDetector()
        self.rollback_mgr = RollbackManager()
        self.report_gen = ChangeReportGenerator()
        self.exporter = ChangeFileExporter()

    async def process_change_request(self, input_data: ChangeControlInput) -> ChangeControlOutput:
        """
        Executes the formal change control cycle:
        REQUEST -> CLASSIFY -> IMPACT -> RISK -> APPROVAL -> VERSION -> PLAN -> REPORT
        """
        start_time = time.time()
        chg_id = f"CHANGE-{uuid.uuid4().hex[:6].upper()}"
        proj_id = input_data.project_id
        user_id = input_data.user_id

        # 1. Multi-User Project Isolation (Section 75)
        if not await self.graph_service.verify_project_access(proj_id, user_id):
            raise PermissionError(f"ACCESS_DENIED: User '{user_id}' lacks write permission for project '{proj_id}'.")

        logger.info(f"[{chg_id}][{self.NAME}] Initiating change request for project '{proj_id}': '{input_data.title}'")

        # 2. Determine Change Severity
        severity: ChangeSeverityLiteral = "MEDIUM"
        if input_data.change_type in ("DOCUMENTATION_CHANGE", "PROJECT_METADATA_CHANGE"):
            severity = "LOW"
        elif input_data.change_type in ("ARCHITECTURE_CHANGE", "INTERFACE_CHANGE", "COMPONENT_CHANGE"):
            severity = "HIGH"
        elif "safety" in input_data.description.lower() or "critical" in input_data.title.lower():
            severity = "CRITICAL"

        # 3. Create ChangeRequest Object
        change_req = ChangeRequest(
            change_id=chg_id,
            project_id=proj_id,
            change_type=input_data.change_type,
            title=input_data.title,
            description=input_data.description,
            requested_by=user_id,
            target_artifact=input_data.target_artifact,
            severity=severity,
            status="ANALYZING",
        )

        # 4. Check for Concurrent Change Conflicts (Section 65)
        active_changes = await self.repo.get_changes(proj_id)
        conflict = self.conflict_detector.detect_conflicts(active_changes, change_req)
        if conflict:
            logger.warning(f"Change conflict detected: {conflict.description}")
            change_req.status = "BLOCKED"

        await self.repo.create_change(change_req)

        # 5. Impact Analysis (Direct & Indirect)
        impact = self.impact_engine.analyze_change(change_req)

        # 6. Risk Evaluation
        risks = self.risk_analyzer.evaluate_risks(change_req)

        # 7. Revalidation & Execution Plan
        plan = self.revalidation_engine.create_revalidation_plan(change_req, impact)

        # 8. Approval Workflow
        approval = self.approval_engine.create_approval_request(change_req)
        if approval:
            await self.repo.create_approval(approval)
            change_req.status = "PENDING_APPROVAL"
        elif change_req.status == "ANALYZING":
            change_req.status = "APPROVED"

        # 9. Generate 20-Section Change Report
        report_md = self.report_gen.generate_report(
            change=change_req,
            impact=impact,
            risks=risks,
            approval=approval,
            plan=plan,
        )

        # 10. Assemble Output & Export Files
        output = ChangeControlOutput(
            change_request=change_req,
            impact=impact,
            risks=risks,
            approval=approval,
            change_plan=plan,
            report_markdown=report_md,
        )

        if input_data.output_dir:
            exported = self.exporter.export_artifacts(
                output_dir=input_data.output_dir,
                change=change_req,
                impact=impact,
                risks=risks,
                plan=plan,
                approval=approval,
                report_markdown=report_md,
            )
            output.exported_files = exported

        elapsed = time.time() - start_time
        logger.info(f"[{chg_id}][{self.NAME}] Change processing completed in {elapsed:.3f}s (Status={change_req.status})")

        return output

    def process_change_request_sync(self, input_data: ChangeControlInput) -> ChangeControlOutput:
        """Synchronous wrapper for ADK and CLI."""
        return asyncio.run(self.process_change_request(input_data))

    # =========================================================================
    # Google ADK Capability Methods (Section 58)
    # =========================================================================

    def create_change(
        self,
        project_id: str,
        change_type: ChangeTypeLiteral,
        title: str,
        description: str,
        target_artifact: Optional[str] = None,
        user_id: str = "user_001",
    ) -> ChangeControlOutput:
        """ADK Capability: Creates and analyzes a controlled change request."""
        return self.process_change_request_sync(
            ChangeControlInput(
                project_id=project_id,
                change_type=change_type,
                title=title,
                description=description,
                target_artifact=target_artifact,
                user_id=user_id,
            )
        )

    def approve_change(self, change_id: str, approver_id: str) -> ApprovalObject:
        """ADK Capability: Approves a pending change request with self-approval checks."""
        change = asyncio.run(self.repo.get_change(change_id))
        if not change:
            raise ValueError(f"Change '{change_id}' not found.")

        approval = self.approval_engine.create_approval_request(change)
        approved = self.approval_engine.approve_change(approval, change, approver_id)
        asyncio.run(self.repo.update_change_status(change_id, "APPROVED"))
        return approved

    def execute_rollback(
        self,
        artifact_id: str,
        target_version: str,
        current_version: str,
        approved_by: str,
    ) -> Tuple[RollbackObject, ArtifactVersion]:
        """ADK Capability: Executes history-preserving forward rollback."""
        rollback, new_ver = self.rollback_mgr.execute_rollback(
            artifact_id=artifact_id,
            target_version=target_version,
            current_version=current_version,
            approved_by=approved_by,
        )
        asyncio.run(self.repo.create_version(new_ver))
        return rollback, new_ver
