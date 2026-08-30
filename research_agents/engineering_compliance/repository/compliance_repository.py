"""
SurrealDB repository for compliance rules, checks, results, and waivers (Sections 12, 13, 65).
"""

from typing import Any, Dict, List, Optional
from loguru import logger
from research_agents.engineering_compliance.schemas import (
    ComplianceException,
    ComplianceResult,
    ComplianceRule,
    ComplianceWaiver,
)
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient


class ComplianceRepository:
    """SurrealDB graph access repository for engineering compliance rules and results."""

    def __init__(self, db_client: Optional[SurrealDBClient] = None):
        self.db = db_client or SurrealDBClient()
        self._memory_rules: Dict[str, ComplianceRule] = {}
        self._memory_results: Dict[str, ComplianceResult] = {}
        self._memory_waivers: Dict[str, ComplianceWaiver] = {}

    async def create_rule(self, rule: ComplianceRule) -> ComplianceRule:
        try:
            await self.db.create_node("compliance_rule", rule.rule_id, rule.model_dump())
            await self.db.relate_nodes(f"project:{rule.project_id}", "has_rule", f"compliance_rule:{rule.rule_id}")
        except Exception as e:
            logger.warning(f"SurrealDB create_rule fallback to memory: {e}")

        self._memory_rules[rule.rule_id] = rule
        return rule

    async def create_result(self, result: ComplianceResult) -> ComplianceResult:
        try:
            await self.db.create_node("compliance_result", result.compliance_id, result.model_dump())
            await self.db.relate_nodes(f"compliance_result:{result.compliance_id}", "evaluates", f"compliance_rule:{result.rule_id}")
            await self.db.relate_nodes(f"compliance_rule:{result.rule_id}", "checks", f"artifact:{result.artifact_id}")
        except Exception as e:
            logger.warning(f"SurrealDB create_result fallback: {e}")

        self._memory_results[result.compliance_id] = result
        return result

    async def create_waiver(self, waiver: ComplianceWaiver) -> ComplianceWaiver:
        try:
            await self.db.create_node("compliance_waiver", waiver.waiver_id, waiver.model_dump())
            await self.db.relate_nodes(f"compliance_rule:{waiver.rule_id}", "has_waiver", f"compliance_waiver:{waiver.waiver_id}")
        except Exception as e:
            logger.warning(f"SurrealDB create_waiver fallback: {e}")

        self._memory_waivers[waiver.waiver_id] = waiver
        return waiver

    async def invalidate_result(self, compliance_id: str) -> Optional[ComplianceResult]:
        if compliance_id in self._memory_results:
            self._memory_results[compliance_id].status = "INVALIDATED"
            try:
                await self.db.upsert_node("compliance_result", compliance_id, {"status": "INVALIDATED"})
            except Exception as e:
                logger.warning(f"SurrealDB invalidate fallback: {e}")
            return self._memory_results[compliance_id]
        return None

    async def get_rules(self, project_id: str) -> List[ComplianceRule]:
        return [r for r in self._memory_rules.values() if r.project_id == project_id]

    async def get_results(self, project_id: str) -> List[ComplianceResult]:
        return [res for res in self._memory_results.values() if res.project_id == project_id]

    async def get_waivers(self, project_id: str) -> List[ComplianceWaiver]:
        return [w for w in self._memory_waivers.values() if w.project_id == project_id]
