"""
SurrealDB graph repository and fallback in-memory store for Security Assets, Threats, and Controls (Agent #22).
"""

from typing import Any, Dict, List, Optional
from loguru import logger

from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.security_threat.schemas import (
    AssetObject,
    AttackPath,
    AttackSurfaceEntry,
    SecurityControl,
    SecurityFinding,
    SecurityTestCase,
    ThreatActor,
    ThreatMitigation,
    ThreatObject,
    TrustBoundary,
)


class SecurityRepository:
    """SurrealDB graph access repository for threat modeling data."""

    def __init__(self, db_client: Optional[SurrealDBClient] = None):
        self.db = db_client or SurrealDBClient()
        self._memory_assets: Dict[str, AssetObject] = {}
        self._memory_actors: Dict[str, ThreatActor] = {}
        self._memory_boundaries: Dict[str, TrustBoundary] = {}
        self._memory_surface: Dict[str, AttackSurfaceEntry] = {}
        self._memory_threats: Dict[str, ThreatObject] = {}
        self._memory_paths: Dict[str, AttackPath] = {}
        self._memory_controls: Dict[str, SecurityControl] = {}
        self._memory_mitigations: Dict[str, ThreatMitigation] = {}
        self._memory_tests: Dict[str, SecurityTestCase] = {}
        self._memory_findings: Dict[str, SecurityFinding] = {}

    async def save_asset(self, asset: AssetObject) -> AssetObject:
        try:
            await self.db.create_node("security_asset", asset.asset_id, asset.model_dump())
            await self.db.relate_nodes(f"project:{asset.project_id}", "has_asset", f"security_asset:{asset.asset_id}")
        except Exception as e:
            logger.warning(f"SurrealDB save_asset fallback: {e}")
        self._memory_assets[asset.asset_id] = asset
        return asset

    async def save_threat(self, threat: ThreatObject) -> ThreatObject:
        try:
            await self.db.create_node("security_threat", threat.threat_id, threat.model_dump())
            await self.db.relate_nodes(f"project:{threat.project_id}", "has_threat", f"security_threat:{threat.threat_id}")
            for a_id in threat.asset_ids:
                await self.db.relate_nodes(f"security_threat:{threat.threat_id}", "targets", f"security_asset:{a_id}")
            for e_id in threat.entry_point_ids:
                await self.db.relate_nodes(f"security_threat:{threat.threat_id}", "uses", f"attack_surface:{e_id}")
        except Exception as e:
            logger.warning(f"SurrealDB save_threat fallback: {e}")
        self._memory_threats[threat.threat_id] = threat
        return threat

    async def save_control(self, ctrl: SecurityControl) -> SecurityControl:
        try:
            await self.db.create_node("security_control", ctrl.control_id, ctrl.model_dump())
        except Exception as e:
            logger.warning(f"SurrealDB save_control fallback: {e}")
        self._memory_controls[ctrl.control_id] = ctrl
        return ctrl

    async def save_mitigation(self, mit: ThreatMitigation) -> ThreatMitigation:
        try:
            await self.db.create_node("security_mitigation", mit.mitigation_id, mit.model_dump())
            await self.db.relate_nodes(
                f"security_threat:{mit.threat_id}", "has_security_mitigation", f"security_mitigation:{mit.mitigation_id}"
            )
        except Exception as e:
            logger.warning(f"SurrealDB save_mitigation fallback: {e}")
        self._memory_mitigations[mit.mitigation_id] = mit
        return mit

    async def save_attack_path(self, path: AttackPath) -> AttackPath:
        try:
            await self.db.create_node("attack_path", path.attack_path_id, path.model_dump())
            await self.db.relate_nodes(
                f"security_threat:{path.threat_id}", "has_attack_path", f"attack_path:{path.attack_path_id}"
            )
        except Exception as e:
            logger.warning(f"SurrealDB save_attack_path fallback: {e}")
        self._memory_paths[path.attack_path_id] = path
        return path

    async def save_test(self, test: SecurityTestCase) -> SecurityTestCase:
        try:
            await self.db.create_node("security_test", test.security_test_id, test.model_dump())
            await self.db.relate_nodes(
                f"security_threat:{test.threat_id}", "has_security_test", f"security_test:{test.security_test_id}"
            )
        except Exception as e:
            logger.warning(f"SurrealDB save_test fallback: {e}")
        self._memory_tests[test.security_test_id] = test
        return test

    async def get_threat(self, threat_id: str) -> Optional[ThreatObject]:
        return self._memory_threats.get(threat_id)

    async def list_threats_for_project(self, project_id: str) -> List[ThreatObject]:
        return [t for t in self._memory_threats.values() if t.project_id == project_id]

    async def list_assets_for_project(self, project_id: str) -> List[AssetObject]:
        return [a for a in self._memory_assets.values() if a.project_id == project_id]

    async def list_controls(self) -> List[SecurityControl]:
        return list(self._memory_controls.values())

    async def list_mitigations_for_threat(self, threat_id: str) -> List[ThreatMitigation]:
        return [m for m in self._memory_mitigations.values() if m.threat_id == threat_id]
