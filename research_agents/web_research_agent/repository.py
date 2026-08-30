"""
Repository interface for web research evidence persistence.
Defines abstract persistence methods for future SurrealDB integration with in-memory test fallback.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from research_agents.web_research_agent.schemas import (
    ExtractedEngineeringFact,
    NormalizedWebSource,
    WebResearchAgentOutput,
)


class ResearchEvidenceRepository(ABC):
    """Abstract persistence interface for web sources, facts, and project edges."""

    @abstractmethod
    async def save_source(self, source: NormalizedWebSource) -> str:
        """Persists a normalized web source."""
        pass

    @abstractmethod
    async def save_fact(self, fact: ExtractedEngineeringFact) -> str:
        """Persists an extracted engineering fact with provenance."""
        pass

    @abstractmethod
    async def save_project_source_relationship(
        self,
        project_id: str,
        source_id: str,
        relevance_score: float,
    ) -> bool:
        """Saves a relationship edge between a project and a web source."""
        pass

    @abstractmethod
    async def save_project_fact_relationship(
        self,
        project_id: str,
        source_id: str,
        fact: str,
    ) -> bool:
        """Saves an edge between a project and an extracted fact."""
        pass

    @abstractmethod
    async def get_project_sources(self, project_id: str) -> List[NormalizedWebSource]:
        """Retrieves all web sources linked to a project."""
        pass

    @abstractmethod
    async def get_source_facts(self, source_id: str) -> List[ExtractedEngineeringFact]:
        """Retrieves all facts derived from a specific source."""
        pass


class InMemoryResearchEvidenceRepository(ResearchEvidenceRepository):
    """In-memory repository used for local development and test suites."""

    def __init__(self):
        self._sources: Dict[str, NormalizedWebSource] = {}
        self._facts: List[ExtractedEngineeringFact] = []
        self._project_sources: Dict[str, List[str]] = {}
        self._project_facts: Dict[str, List[ExtractedEngineeringFact]] = {}

    async def save_source(self, source: NormalizedWebSource) -> str:
        self._sources[source.source_id] = source
        return source.source_id

    async def save_fact(self, fact: ExtractedEngineeringFact) -> str:
        self._facts.append(fact)
        return fact.source_id

    async def save_project_source_relationship(
        self,
        project_id: str,
        source_id: str,
        relevance_score: float,
    ) -> bool:
        if project_id not in self._project_sources:
            self._project_sources[project_id] = []
        if source_id not in self._project_sources[project_id]:
            self._project_sources[project_id].append(source_id)
        return True

    async def save_project_fact_relationship(
        self,
        project_id: str,
        source_id: str,
        fact: str,
    ) -> bool:
        if project_id not in self._project_facts:
            self._project_facts[project_id] = []
        matching_fact = next((f for f in self._facts if f.source_id == source_id and f.fact == fact), None)
        if matching_fact and matching_fact not in self._project_facts[project_id]:
            self._project_facts[project_id].append(matching_fact)
        return True

    async def get_project_sources(self, project_id: str) -> List[NormalizedWebSource]:
        source_ids = self._project_sources.get(project_id, [])
        return [self._sources[sid] for sid in source_ids if sid in self._sources]

    async def get_source_facts(self, source_id: str) -> List[ExtractedEngineeringFact]:
        return [f for f in self._facts if f.source_id == source_id]
