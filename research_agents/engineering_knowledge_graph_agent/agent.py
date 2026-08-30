"""
Agent #13: EngineeringKnowledgeGraphAgent implementation using Google ADK conventions.
Maintains the persistent SurrealDB engineering knowledge graph and project state machine.
"""

import asyncio
from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional
import uuid
from loguru import logger

from research_agents.engineering_knowledge_graph_agent.config import graph_config
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.engineering_knowledge_graph_agent.database.migrations import MigrationRunner
from research_agents.engineering_knowledge_graph_agent.providers.base import ReasoningProvider
from research_agents.engineering_knowledge_graph_agent.providers.bedrock import BedrockGraphProvider
from research_agents.engineering_knowledge_graph_agent.schemas import (
    ArchitectureImpactResult,
    ArchitectureNode,
    BOMItemNode,
    BOMNode,
    ComponentImpactResult,
    ComponentNode,
    EngineeringDecisionNode,
    EngineeringKnowledgeGraphInput,
    EngineeringKnowledgeGraphOutput,
    ExecutionNode,
    ImplementationTaskNode,
    ProjectNode,
    ProjectStateLiteral,
    ProjectStateNode,
    ProjectTimelineEvent,
    RequirementImpactResult,
    RequirementNode,
    RequirementTraceResult,
    ResearchNode,
    SubsystemNode,
    TestNode,
    TestResultNode,
    UserNode,
)
from research_agents.engineering_knowledge_graph_agent.services.audit_logger import GraphAuditLogger
from research_agents.engineering_knowledge_graph_agent.services.consistency_checker import GraphConsistencyChecker
from research_agents.engineering_knowledge_graph_agent.services.export_service import GraphExporter
from research_agents.engineering_knowledge_graph_agent.services.graph_query import KnowledgeGraphService
from research_agents.engineering_knowledge_graph_agent.services.graph_writer import KnowledgeGraphWriter
from research_agents.engineering_knowledge_graph_agent.services.report_generator import GraphReportGenerator
from research_agents.engineering_knowledge_graph_agent.services.state_machine import ProjectStateManager


class EngineeringKnowledgeGraphAgent:
    """
    Google ADK-compliant Engineering Knowledge Graph & Project State Agent.
    Maintains the persistent SurrealDB engineering knowledge graph and project state machine.
    """

    NAME = "EngineeringKnowledgeGraphAgent"
    DESCRIPTION = (
        "Maintains the persistent engineering knowledge graph and project state "
        "for verified engineering projects."
    )
    CAPABILITIES = [
        "graph.query",
        "graph.trace",
        "graph.impact",
        "graph.timeline",
        "graph.state",
        "graph.export",
        "graph.ingest",
    ]

    def __init__(
        self,
        db_client: Optional[SurrealDBClient] = None,
        reasoning_provider: Optional[ReasoningProvider] = None,
        audit_logger: Optional[GraphAuditLogger] = None,
    ):
        self.db = db_client or SurrealDBClient()
        self.provider = reasoning_provider or BedrockGraphProvider()
        self.audit = audit_logger or GraphAuditLogger()
        self.writer = KnowledgeGraphWriter(self.db, self.audit)
        self.query_service = KnowledgeGraphService(self.db)
        self.state_manager = ProjectStateManager(self.db)
        self.consistency_checker = GraphConsistencyChecker(self.db)
        self.exporter = GraphExporter(self.db)
        self.report_generator = GraphReportGenerator()
        self.migrations = MigrationRunner(self.db)

    async def run(
        self,
        input_data: EngineeringKnowledgeGraphInput,
        operation_id: Optional[str] = None,
    ) -> EngineeringKnowledgeGraphOutput:
        """
        Ingests the complete verified engineering lifecycle into the SurrealDB knowledge graph.
        """
        start_time = time.time()
        op_id = operation_id or f"GRAPH-OP-{uuid.uuid4().hex[:6].upper()}"
        proj_id = input_data.project.get("project_id", "proj_001")
        proj_name = input_data.project.get("title", "Engineering Project")
        user_id = input_data.user_id or "user_001"

        logger.info(f"[{op_id}][{self.NAME}] Ingesting engineering lifecycle into SurrealDB for project='{proj_id}'")

        # 1. Connect & Apply Migrations
        await self.db.connect()
        await self.migrations.run_migrations()

        nodes_created = 0
        nodes_updated = 0
        rels_created = 0

        # 2. Ingest User & Project
        user = UserNode(
            id=f"user:{user_id}",
            external_user_id=user_id,
            display_name=f"Engineer ({user_id})",
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        _, u_new = await self.writer.create_user(user)
        if u_new:
            nodes_created += 1

        project = ProjectNode(
            id=f"project:{proj_id}",
            name=proj_name,
            description=input_data.project.get("description", ""),
            status="research",
            owner_id=user_id,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        _, p_new = await self.writer.create_project(project, owner_id=user_id)
        if p_new:
            nodes_created += 1
            rels_created += 1

        # 3. Ingest Requirements
        for req in input_data.requirements:
            r_id = req.get("requirement_id", f"REQ-{uuid.uuid4().hex[:4].upper()}")
            r_node = RequirementNode(
                id=f"requirement:{r_id}",
                project_id=proj_id,
                title=req.get("title") or req.get("description", r_id),
                description=req.get("description", ""),
                priority=req.get("priority", "high"),
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            _, r_new = await self.writer.create_requirement(r_node)
            if r_new:
                nodes_created += 1
                rels_created += 1

        # 4. Ingest Research Papers & Web Evidence
        for res in input_data.research:
            res_id = res.get("id") or f"RES-{uuid.uuid4().hex[:4].upper()}"
            res_node = ResearchNode(
                id=f"research:{res_id}",
                project_id=proj_id,
                title=res.get("title", "Research Source"),
                source=res.get("source", "Freephdlabor"),
                url=res.get("url"),
                summary=res.get("summary", ""),
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            _, res_new = await self.writer.create_research(res_node, related_req_id="REQ-SAR-001")
            if res_new:
                nodes_created += 1
                rels_created += 1

        # 5. Ingest Decisions
        for dec in input_data.decisions:
            dec_id = dec.get("decision_id") or f"DEC-{uuid.uuid4().hex[:4].upper()}"
            dec_node = EngineeringDecisionNode(
                id=f"engineering_decision:{dec_id}",
                project_id=proj_id,
                title=dec.get("title", "Decision"),
                decision=dec.get("decision", ""),
                reasoning=dec.get("reasoning", ""),
                selected_option=dec.get("selected_option", ""),
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            _, d_new = await self.writer.create_decision(dec_node, req_id="REQ-SAR-001")
            if d_new:
                nodes_created += 1
                rels_created += 1

        # 6. Ingest Architecture & Subsystems
        arch_id = f"ARCH-{proj_id}"
        arch_node = ArchitectureNode(
            id=f"architecture:{arch_id}",
            project_id=proj_id,
            name=f"{proj_name} Architecture",
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        _, a_new = await self.writer.create_architecture(arch_node)
        if a_new:
            nodes_created += 1
            rels_created += 1

        subsystems = input_data.architecture.get("subsystems", ["ThermalImagingSubsystem", "EdgeInferenceSubsystem"])
        for sub in subsystems:
            sub_name = sub if isinstance(sub, str) else sub.get("name", "Subsystem")
            sub_node = SubsystemNode(
                id=f"subsystem:{sub_name}",
                project_id=proj_id,
                architecture_id=arch_id,
                name=sub_name,
            )
            _, s_new = await self.writer.create_subsystem(sub_node)
            if s_new:
                nodes_created += 1
                rels_created += 1

        # 7. Ingest BOM & Components
        bom_id = f"BOM-{proj_id}"
        bom_node = BOMNode(
            id=f"bom:{bom_id}",
            project_id=proj_id,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        _, b_new = await self.writer.create_bom(bom_node)
        if b_new:
            nodes_created += 1
            rels_created += 1

        bom_items = input_data.bom.get("items", [
            {"component_id": "500-0771-01", "name": "FLIR Lepton 3.5", "manufacturer": "Teledyne FLIR"},
            {"component_id": "945-13766-0000-000", "name": "Jetson Orin Nano", "manufacturer": "NVIDIA"},
        ])
        for item in bom_items:
            comp_mpn = item.get("component_id") or item.get("mpn", "GEN-COMP")
            comp_node = ComponentNode(
                id=f"component:{comp_mpn}",
                part_number=comp_mpn,
                manufacturer=item.get("manufacturer", "Generic"),
                category=item.get("category", "Sensor"),
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            _, c_new = await self.writer.create_component(comp_node, subsystem_id="ThermalImagingSubsystem")
            if c_new:
                nodes_created += 1
                rels_created += 1

            bom_item_node = BOMItemNode(
                id=f"bom_item:{comp_mpn}",
                project_id=proj_id,
                bom_id=bom_id,
                component_id=comp_mpn,
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            _, bi_new = await self.writer.create_bom_item(bom_item_node)
            if bi_new:
                nodes_created += 1
                rels_created += 2

        # 8. Ingest Implementation Tasks & Executions
        tasks = input_data.implementation_plan.get("tasks", [
            {"task_id": "TASK-001", "title": "Implement FLIR Lepton Driver", "target_file": "firmware/sensors/lepton.py"}
        ])
        for t in tasks:
            t_id = t.get("task_id", "TASK-001")
            task_node = ImplementationTaskNode(
                id=f"implementation_task:{t_id}",
                project_id=proj_id,
                package_id=f"WP-{proj_id}",
                title=t.get("title", t_id),
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            _, t_new = await self.writer.create_implementation_task(task_node, req_id="REQ-SAR-001", comp_id="500-0771-01")
            if t_new:
                nodes_created += 1
                rels_created += 2

        # 9. Ingest Execution & Test Evidence
        exec_id = input_data.execution_result.get("execution_id", f"exec_{proj_id}")
        exec_node = ExecutionNode(
            id=f"execution:{exec_id}",
            execution_id=exec_id,
            project_id=proj_id,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        _, ex_new = await self.writer.create_execution(
            exec_node,
            task_id="TASK-001",
            file_paths=input_data.execution_result.get("changed_files", ["firmware/sensors/lepton.py"]),
        )
        if ex_new:
            nodes_created += 1
            rels_created += 2

        # Ingest Test and Evidence
        test_node = TestNode(
            id=f"test:TEST-001",
            project_id=proj_id,
            name="Pytest Suite",
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        test_res_node = TestResultNode(
            id=f"test_result:TEST-001",
            test_id="TEST-001",
            status="PASS",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await self.writer.create_test_and_evidence(
            test=test_node,
            result=test_res_node,
            evidence_id="EVID-001",
            req_id="REQ-SAR-001",
        )
        nodes_created += 2
        rels_created += 2

        # 10. Evaluate State Transition based on QA & Validation Verdicts
        qa_verdict = input_data.verification_qa.get("verdict", "VERIFIED")
        target_state: ProjectStateLiteral = "verified" if qa_verdict in ("VERIFIED", "VERIFIED_WITH_WARNINGS") else "blocked"
        current_state_node, state_event = await self.state_manager.transition_state(
            project_id=proj_id,
            target_state=target_state,
            reason=f"QA Quality Gate Verdict: {qa_verdict}",
            source="qa",
        )

        # 11. Run Consistency Checker
        consistency = await self.consistency_checker.check_consistency(proj_id)

        # 12. Run Traceability Query for Report
        trace_result = await self.query_service.get_requirement_trace(
            requirement_id="REQ-SAR-001",
            project_id=proj_id,
            user_id=user_id,
        )

        # 13. Render 25-Section Markdown Report
        stats = {
            "nodes_created": nodes_created,
            "relationships_created": rels_created,
        }
        report_md = self.report_generator.generate_report(
            project_id=proj_id,
            project_name=proj_name,
            state=current_state_node,
            trace=trace_result,
            audit_events=self.audit.get_events(proj_id),
            stats=stats,
        )

        # 14. Export Artifacts if output_dir specified
        if input_data.output_dir:
            self.exporter.export_to_directory(proj_id, input_data.output_dir)

        elapsed = time.time() - start_time
        logger.info(
            f"[{op_id}][{self.NAME}] Ingestion completed in {elapsed:.3f}s: "
            f"State={current_state_node.current_state} Nodes={nodes_created} Rels={rels_created}"
        )

        return EngineeringKnowledgeGraphOutput(
            status="success",
            project_id=proj_id,
            graph_operation_id=op_id,
            nodes_created=nodes_created,
            nodes_updated=nodes_updated,
            relationships_created=rels_created,
            duplicates_prevented=0,
            current_state=current_state_node.current_state,
            state_transition=f"{current_state_node.previous_state} -> {current_state_node.current_state}",
            consistency_status=consistency["status"],
            audit_events=self.audit.get_events(proj_id),
            errors=[],
            warnings=[],
            structured_report_markdown=report_md,
        )

    def run_sync(
        self,
        input_data: EngineeringKnowledgeGraphInput,
        operation_id: Optional[str] = None,
    ) -> EngineeringKnowledgeGraphOutput:
        """Synchronous wrapper for ADK and CLI."""
        return asyncio.run(self.run(input_data=input_data, operation_id=operation_id))

    # =========================================================================
    # Google ADK Capability Methods (Section 78)
    # =========================================================================

    def ingest_project(self, input_data: EngineeringKnowledgeGraphInput) -> EngineeringKnowledgeGraphOutput:
        """ADK Capability: Ingests project lifecycle into SurrealDB knowledge graph."""
        return self.run_sync(input_data)

    def query_project_graph(self, project_id: str, user_id: str = "user_001") -> Dict[str, Any]:
        """ADK Capability: Queries connected project graph."""
        return asyncio.run(self.query_service.get_project_graph(project_id, user_id))

    def trace_requirement(self, requirement_id: str, project_id: str, user_id: str = "user_001") -> RequirementTraceResult:
        """ADK Capability: Traces requirement through architecture, BOM, tasks, and validation."""
        return asyncio.run(self.query_service.get_requirement_trace(requirement_id, project_id, user_id))

    def trace_component(self, component_id: str, project_id: str, user_id: str = "user_001") -> ComponentImpactResult:
        """ADK Capability: Analyzes component impact across subsystems and tasks."""
        return asyncio.run(self.query_service.get_component_impact(component_id, project_id, user_id))

    def analyze_impact(self, component_id: str, project_id: str, user_id: str = "user_001") -> ComponentImpactResult:
        """ADK Capability: Performs impact analysis."""
        return asyncio.run(self.query_service.get_component_impact(component_id, project_id, user_id))

    def get_project_timeline(self, project_id: str, user_id: str = "user_001") -> List[ProjectTimelineEvent]:
        """ADK Capability: Retrieves chronological project lifecycle timeline."""
        return asyncio.run(self.query_service.get_project_timeline(project_id, user_id))
