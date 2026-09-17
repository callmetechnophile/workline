"""
SurrealDB graph repository and fallback in-memory store for Manufacturing / DFM-DFA entities (Agent #24).
"""

from typing import Any, Dict, List, Optional
from loguru import logger

from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.manufacturing_agent.schemas import (
    CostDriverHandoff,
    DFAFinding,
    DFAModel,
    DFMFinding,
    InspectionItem,
    ManufacturingProcess,
    ManufacturingReadiness,
    ManufacturingRecommendation,
    ProcessSequence,
    ToleranceItem,
    ToolingRequirement,
    VariationData,
)


class ManufacturingRepository:
    """SurrealDB graph access repository for manufacturing and DFM/DFA records."""

    def __init__(self, db_client: Optional[SurrealDBClient] = None):
        self.db = db_client or SurrealDBClient()
        self._memory_processes: Dict[str, ManufacturingProcess] = {}
        self._memory_dfm: Dict[str, DFMFinding] = {}
        self._memory_dfa: Dict[str, DFAFinding] = {}
        self._memory_tolerances: Dict[str, ToleranceItem] = {}
        self._memory_variations: Dict[str, VariationData] = {}
        self._memory_tooling: Dict[str, ToolingRequirement] = {}
        self._memory_sequences: Dict[str, ProcessSequence] = {}
        self._memory_inspections: Dict[str, InspectionItem] = {}
        self._memory_recs: Dict[str, ManufacturingRecommendation] = {}
        self._memory_readiness: Dict[str, ManufacturingReadiness] = {}

    async def save_process(self, proc: ManufacturingProcess) -> ManufacturingProcess:
        try:
            await self.db.create_node("manufacturing_process", proc.process_id, proc.model_dump())
        except Exception as e:
            logger.warning(f"SurrealDB save_process fallback: {e}")
        self._memory_processes[proc.process_id] = proc
        return proc

    async def save_dfm_finding(self, finding: DFMFinding, project_id: str) -> DFMFinding:
        try:
            await self.db.create_node("dfm_finding", finding.finding_id, finding.model_dump())
            await self.db.relate_nodes(f"project:{project_id}", "has_dfm_finding", f"dfm_finding:{finding.finding_id}")
            await self.db.relate_nodes(f"dfm_finding:{finding.finding_id}", "affects_component", f"component:{finding.component_id}")
        except Exception as e:
            logger.warning(f"SurrealDB save_dfm_finding fallback: {e}")
        self._memory_dfm[finding.finding_id] = finding
        return finding

    async def save_dfa_finding(self, finding: DFAFinding, project_id: str) -> DFAFinding:
        try:
            await self.db.create_node("dfa_finding", finding.finding_id, finding.model_dump())
            await self.db.relate_nodes(f"project:{project_id}", "has_dfa_finding", f"dfa_finding:{finding.finding_id}")
        except Exception as e:
            logger.warning(f"SurrealDB save_dfa_finding fallback: {e}")
        self._memory_dfa[finding.finding_id] = finding
        return finding

    async def save_recommendation(self, rec: ManufacturingRecommendation) -> ManufacturingRecommendation:
        try:
            await self.db.create_node("manufacturing_recommendation", rec.recommendation_id, rec.model_dump())
            await self.db.relate_nodes(
                f"dfm_finding:{rec.finding_id}", "recommends_change", f"manufacturing_recommendation:{rec.recommendation_id}"
            )
        except Exception as e:
            logger.warning(f"SurrealDB save_recommendation fallback: {e}")
        self._memory_recs[rec.recommendation_id] = rec
        return rec

    async def save_readiness(self, readiness: ManufacturingReadiness) -> ManufacturingReadiness:
        try:
            await self.db.create_node("manufacturing_readiness", readiness.project_id, readiness.model_dump())
        except Exception as e:
            logger.warning(f"SurrealDB save_readiness fallback: {e}")
        self._memory_readiness[readiness.project_id] = readiness
        return readiness

    async def list_dfm_findings(self) -> List[DFMFinding]:
        return list(self._memory_dfm.values())

    async def list_dfa_findings(self) -> List[DFAFinding]:
        return list(self._memory_dfa.values())

    async def list_recommendations(self) -> List[ManufacturingRecommendation]:
        return list(self._memory_recs.values())
