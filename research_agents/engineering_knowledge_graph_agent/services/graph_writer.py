"""
Knowledge graph write service for EngineeringKnowledgeGraphAgent (Section 62).
Provides atomic node and relation creation, idempotency, duplicate prevention, and audit logging.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from loguru import logger
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.engineering_knowledge_graph_agent.schemas import (
    ArchitectureNode,
    BOMItemNode,
    BOMNode,
    ComponentNode,
    EngineeringDecisionNode,
    ExecutionNode,
    ImplementationPlanNode,
    ImplementationTaskNode,
    ProjectFileNode,
    ProjectNode,
    RequirementNode,
    ResearchNode,
    SubsystemNode,
    SupplierNode,
    SupplierOfferNode,
    TestNode,
    TestResultNode,
    UserNode,
    ValidationNode,
)
from research_agents.engineering_knowledge_graph_agent.services.audit_logger import GraphAuditLogger


class KnowledgeGraphWriter:
    """Creates typed graph nodes and semantic edges with idempotency and audit logs."""

    def __init__(self, db_client: SurrealDBClient, audit_logger: GraphAuditLogger):
        self.db = db_client
        self.audit = audit_logger

    async def create_user(self, user: UserNode) -> Tuple[Dict[str, Any], bool]:
        data, is_new = await self.db.upsert_node("user", user.id.split(":")[-1], user.model_dump())
        self.audit.record_mutation(
            project_id="GLOBAL",
            operation="upsert",
            object_type="user",
            object_id=user.id,
        )
        return data, is_new

    async def create_project(self, project: ProjectNode, owner_id: str) -> Tuple[Dict[str, Any], bool]:
        proj_clean = project.id.split(":")[-1]
        data, is_new = await self.db.upsert_node("project", proj_clean, project.model_dump())
        await self.db.relate_nodes(f"user:{owner_id}", "OWNS", f"project:{proj_clean}")
        self.audit.record_mutation(
            project_id=proj_clean,
            operation="upsert",
            object_type="project",
            object_id=f"project:{proj_clean}",
        )
        return data, is_new

    async def create_requirement(self, req: RequirementNode) -> Tuple[Dict[str, Any], bool]:
        req_clean = req.id.split(":")[-1]
        data, is_new = await self.db.upsert_node("requirement", req_clean, req.model_dump())
        await self.db.relate_nodes(f"project:{req.project_id}", "HAS_REQUIREMENT", f"requirement:{req_clean}")
        self.audit.record_mutation(
            project_id=req.project_id,
            operation="upsert",
            object_type="requirement",
            object_id=f"requirement:{req_clean}",
        )
        return data, is_new

    async def create_research(self, res: ResearchNode, related_req_id: Optional[str] = None) -> Tuple[Dict[str, Any], bool]:
        res_clean = res.id.split(":")[-1]
        data, is_new = await self.db.upsert_node("research", res_clean, res.model_dump())
        if related_req_id:
            await self.db.relate_nodes(f"research:{res_clean}", "SUPPORTS", f"requirement:{related_req_id}")
        self.audit.record_mutation(
            project_id=res.project_id,
            operation="upsert",
            object_type="research",
            object_id=f"research:{res_clean}",
        )
        return data, is_new

    async def create_decision(self, dec: EngineeringDecisionNode, req_id: Optional[str] = None) -> Tuple[Dict[str, Any], bool]:
        dec_clean = dec.id.split(":")[-1]
        data, is_new = await self.db.upsert_node("engineering_decision", dec_clean, dec.model_dump())
        if req_id:
            await self.db.relate_nodes(f"requirement:{req_id}", "DRIVES", f"engineering_decision:{dec_clean}")
        if dec.supersedes:
            await self.db.relate_nodes(f"engineering_decision:{dec.supersedes}", "SUPERSEDES", f"engineering_decision:{dec_clean}")
        self.audit.record_mutation(
            project_id=dec.project_id,
            operation="upsert",
            object_type="engineering_decision",
            object_id=f"engineering_decision:{dec_clean}",
        )
        return data, is_new

    async def create_architecture(self, arch: ArchitectureNode) -> Tuple[Dict[str, Any], bool]:
        arch_clean = arch.id.split(":")[-1]
        data, is_new = await self.db.upsert_node("architecture", arch_clean, arch.model_dump())
        await self.db.relate_nodes(f"project:{arch.project_id}", "CONTAINS", f"architecture:{arch_clean}")
        self.audit.record_mutation(
            project_id=arch.project_id,
            operation="upsert",
            object_type="architecture",
            object_id=f"architecture:{arch_clean}",
        )
        return data, is_new

    async def create_subsystem(self, sub: SubsystemNode) -> Tuple[Dict[str, Any], bool]:
        sub_clean = sub.id.split(":")[-1]
        data, is_new = await self.db.upsert_node("subsystem", sub_clean, sub.model_dump())
        await self.db.relate_nodes(f"architecture:{sub.architecture_id}", "CONTAINS", f"subsystem:{sub_clean}")
        self.audit.record_mutation(
            project_id=sub.project_id,
            operation="upsert",
            object_type="subsystem",
            object_id=f"subsystem:{sub_clean}",
        )
        return data, is_new

    async def create_component(self, comp: ComponentNode, subsystem_id: Optional[str] = None) -> Tuple[Dict[str, Any], bool]:
        comp_clean = comp.id.split(":")[-1]
        data, is_new = await self.db.upsert_node("component", comp_clean, comp.model_dump())
        if subsystem_id:
            await self.db.relate_nodes(f"subsystem:{subsystem_id}", "USES", f"component:{comp_clean}")
        self.audit.record_mutation(
            project_id="GLOBAL",
            operation="upsert",
            object_type="component",
            object_id=f"component:{comp_clean}",
        )
        return data, is_new

    async def create_bom(self, bom: BOMNode) -> Tuple[Dict[str, Any], bool]:
        bom_clean = bom.id.split(":")[-1]
        data, is_new = await self.db.upsert_node("bom", bom_clean, bom.model_dump())
        await self.db.relate_nodes(f"project:{bom.project_id}", "HAS_BOM", f"bom:{bom_clean}")
        self.audit.record_mutation(
            project_id=bom.project_id,
            operation="upsert",
            object_type="bom",
            object_id=f"bom:{bom_clean}",
        )
        return data, is_new

    async def create_bom_item(self, item: BOMItemNode) -> Tuple[Dict[str, Any], bool]:
        item_clean = item.id.split(":")[-1]
        data, is_new = await self.db.upsert_node("bom_item", item_clean, item.model_dump())
        await self.db.relate_nodes(f"bom:{item.bom_id}", "CONTAINS", f"bom_item:{item_clean}")
        await self.db.relate_nodes(f"bom_item:{item_clean}", "USES_COMPONENT", f"component:{item.component_id}")
        self.audit.record_mutation(
            project_id=item.project_id,
            operation="upsert",
            object_type="bom_item",
            object_id=f"bom_item:{item_clean}",
        )
        return data, is_new

    async def create_implementation_task(self, task: ImplementationTaskNode, req_id: Optional[str] = None, comp_id: Optional[str] = None) -> Tuple[Dict[str, Any], bool]:
        task_clean = task.id.split(":")[-1]
        data, is_new = await self.db.upsert_node("implementation_task", task_clean, task.model_dump())
        if req_id:
            await self.db.relate_nodes(f"implementation_task:{task_clean}", "IMPLEMENTS", f"requirement:{req_id}")
        if comp_id:
            await self.db.relate_nodes(f"implementation_task:{task_clean}", "USES_COMPONENT", f"component:{comp_id}")
        self.audit.record_mutation(
            project_id=task.project_id,
            operation="upsert",
            object_type="implementation_task",
            object_id=f"implementation_task:{task_clean}",
        )
        return data, is_new

    async def create_execution(self, exec_node: ExecutionNode, task_id: Optional[str] = None, file_paths: Optional[List[str]] = None) -> Tuple[Dict[str, Any], bool]:
        exec_clean = exec_node.id.split(":")[-1]
        data, is_new = await self.db.upsert_node("execution", exec_clean, exec_node.model_dump())
        if task_id:
            await self.db.relate_nodes(f"implementation_task:{task_id}", "EXECUTED_AS", f"execution:{exec_clean}")
        if file_paths:
            for fp in file_paths:
                file_id = f"file_{fp.replace('/', '_').replace('.', '_')}"
                await self.db.upsert_node("project_file", file_id, {"path": fp, "project_id": exec_node.project_id})
                await self.db.relate_nodes(f"execution:{exec_clean}", "MODIFIED", f"project_file:{file_id}")
        self.audit.record_mutation(
            project_id=exec_node.project_id,
            operation="upsert",
            object_type="execution",
            object_id=f"execution:{exec_clean}",
        )
        return data, is_new

    async def create_test_and_evidence(
        self,
        test: TestNode,
        result: TestResultNode,
        evidence_id: str,
        req_id: Optional[str] = None,
    ) -> None:
        t_clean = test.id.split(":")[-1]
        await self.db.upsert_node("test", t_clean, test.model_dump())
        await self.db.upsert_node("test_result", result.id.split(":")[-1], result.model_dump())
        await self.db.relate_nodes(f"test:{t_clean}", "HAS_RESULT", f"test_result:{result.id.split(':')[-1]}")
        if req_id:
            await self.db.relate_nodes(f"requirement:{req_id}", "VERIFIED_BY", f"test:{t_clean}")
        self.audit.record_mutation(
            project_id=test.project_id,
            operation="upsert",
            object_type="test",
            object_id=f"test:{t_clean}",
        )
