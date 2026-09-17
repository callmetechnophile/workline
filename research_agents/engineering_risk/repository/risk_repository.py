"""
SurrealDB graph repository and fallback in-memory store for Risk and FMEA entities (Agent #21).
"""

from typing import Any, Dict, List, Optional
from loguru import logger

from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.engineering_risk.schemas import (
    FailureMode,
    FMEARecord,
    RatingProfile,
    RiskMatrixProfile,
    RiskMitigation,
    RiskObject,
)


class RiskRepository:
    """SurrealDB graph repository for Risk, FailureMode, FMEA, Mitigation, and Rating profiles."""

    def __init__(self, db_client: Optional[SurrealDBClient] = None):
        self.db = db_client or SurrealDBClient()
        self._memory_risks: Dict[str, RiskObject] = {}
        self._memory_failure_modes: Dict[str, FailureMode] = {}
        self._memory_fmea: Dict[str, FMEARecord] = {}
        self._memory_mitigations: Dict[str, RiskMitigation] = {}
        self._memory_rating_profiles: Dict[str, RatingProfile] = {}
        self._memory_risk_matrices: Dict[str, RiskMatrixProfile] = {}

    async def save_risk(self, risk: RiskObject) -> RiskObject:
        try:
            await self.db.create_node("risk", risk.risk_id, risk.model_dump())
            await self.db.relate_nodes(f"project:{risk.project_id}", "has_risk", f"risk:{risk.risk_id}")
            for req_id in risk.requirement_ids:
                await self.db.relate_nodes(f"risk:{risk.risk_id}", "affects", f"requirement:{req_id}")
            for art_id in risk.artifact_ids:
                await self.db.relate_nodes(f"risk:{risk.risk_id}", "affects", f"artifact:{art_id}")
        except Exception as e:
            logger.warning(f"SurrealDB save_risk fallback: {e}")
        self._memory_risks[risk.risk_id] = risk
        return risk

    async def save_failure_mode(self, fm: FailureMode) -> FailureMode:
        try:
            await self.db.create_node("failure_mode", fm.failure_mode_id, fm.model_dump())
            if fm.risk_id:
                await self.db.relate_nodes(f"risk:{fm.risk_id}", "has_failure_mode", f"failure_mode:{fm.failure_mode_id}")
            if fm.component_id:
                await self.db.relate_nodes(f"failure_mode:{fm.failure_mode_id}", "associated_with", f"component:{fm.component_id}")
            if fm.subsystem_id:
                await self.db.relate_nodes(f"failure_mode:{fm.failure_mode_id}", "propagates_to", f"subsystem:{fm.subsystem_id}")
        except Exception as e:
            logger.warning(f"SurrealDB save_failure_mode fallback: {e}")
        self._memory_failure_modes[fm.failure_mode_id] = fm
        return fm

    async def save_fmea(self, fmea: FMEARecord) -> FMEARecord:
        try:
            await self.db.create_node("fmea_record", fmea.fmea_id, fmea.model_dump())
            await self.db.relate_nodes(
                f"failure_mode:{fmea.failure_mode_id}", "has_fmea", f"fmea_record:{fmea.fmea_id}"
            )
        except Exception as e:
            logger.warning(f"SurrealDB save_fmea fallback: {e}")
        self._memory_fmea[fmea.fmea_id] = fmea
        return fmea

    async def save_mitigation(self, mit: RiskMitigation) -> RiskMitigation:
        try:
            await self.db.create_node("mitigation", mit.mitigation_id, mit.model_dump())
            await self.db.relate_nodes(f"risk:{mit.risk_id}", "has_mitigation", f"mitigation:{mit.mitigation_id}")
        except Exception as e:
            logger.warning(f"SurrealDB save_mitigation fallback: {e}")
        self._memory_mitigations[mit.mitigation_id] = mit
        return mit

    async def get_risk(self, risk_id: str) -> Optional[RiskObject]:
        return self._memory_risks.get(risk_id)

    async def list_risks_for_project(self, project_id: str) -> List[RiskObject]:
        return [r for r in self._memory_risks.values() if r.project_id == project_id]

    async def get_failure_mode(self, fm_id: str) -> Optional[FailureMode]:
        return self._memory_failure_modes.get(fm_id)

    async def list_failure_modes_for_project(self, project_id: str) -> List[FailureMode]:
        return list(self._memory_failure_modes.values())

    async def get_fmea(self, fmea_id: str) -> Optional[FMEARecord]:
        return self._memory_fmea.get(fmea_id)

    async def list_fmea_records(self, project_id: str) -> List[FMEARecord]:
        return [f for f in self._memory_fmea.values() if f.project_id == project_id]

    async def get_mitigation(self, mit_id: str) -> Optional[RiskMitigation]:
        return self._memory_mitigations.get(mit_id)

    async def list_mitigations_for_risk(self, risk_id: str) -> List[RiskMitigation]:
        return [m for m in self._memory_mitigations.values() if m.risk_id == risk_id]
