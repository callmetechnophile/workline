"""
Repository interface for research paper persistence.
Defines abstract boundary for future SurrealDB / database storage with in-memory test fallback.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from research_agents.research_paper_agent.schemas import NormalizedPaper, ResearchPaperAgentOutput


class ResearchRepository(ABC):
    """Abstract persistence interface for papers, runs, and project linkages."""

    @abstractmethod
    async def save_paper(self, paper: NormalizedPaper) -> str:
        """Persists a normalized research paper record."""
        pass

    @abstractmethod
    async def save_project_paper_relationship(
        self,
        project_id: str,
        paper_id: str,
        relevance_score: float,
        relevance_reasons: List[str],
    ) -> bool:
        """Saves a relationship edge between a project and a candidate paper."""
        pass

    @abstractmethod
    async def save_research_run(
        self,
        project_id: str,
        output: ResearchPaperAgentOutput,
        execution_id: Optional[str] = None,
    ) -> str:
        """Records an execution run and associated queries."""
        pass

    @abstractmethod
    async def get_paper(self, paper_id: str) -> Optional[NormalizedPaper]:
        """Retrieves a paper by its unique identifier."""
        pass

    @abstractmethod
    async def get_project_papers(self, project_id: str) -> List[NormalizedPaper]:
        """Retrieves all papers associated with a project."""
        pass


class InMemoryResearchRepository(ResearchRepository):
    """In-memory implementation used for local development and test suites."""

    def __init__(self):
        self._papers: Dict[str, NormalizedPaper] = {}
        self._project_papers: Dict[str, List[str]] = {}
        self._runs: Dict[str, Dict[str, Any]] = {}

    async def save_paper(self, paper: NormalizedPaper) -> str:
        self._papers[paper.paper_id] = paper
        return paper.paper_id

    async def save_project_paper_relationship(
        self,
        project_id: str,
        paper_id: str,
        relevance_score: float,
        relevance_reasons: List[str],
    ) -> bool:
        if project_id not in self._project_papers:
            self._project_papers[project_id] = []
        if paper_id not in self._project_papers[project_id]:
            self._project_papers[project_id].append(paper_id)
        return True

    async def save_research_run(
        self,
        project_id: str,
        output: ResearchPaperAgentOutput,
        execution_id: Optional[str] = None,
    ) -> str:
        run_id = execution_id or f"run_{len(self._runs) + 1}"
        self._runs[run_id] = {
            "project_id": project_id,
            "queries": output.queries_used,
            "paper_ids": [p.paper_id for p in output.papers],
            "status": output.status,
        }
        for paper in output.papers:
            await self.save_paper(paper)
            await self.save_project_paper_relationship(
                project_id=project_id,
                paper_id=paper.paper_id,
                relevance_score=paper.relevance_score,
                relevance_reasons=paper.relevance_reasons,
            )
        return run_id

    async def get_paper(self, paper_id: str) -> Optional[NormalizedPaper]:
        return self._papers.get(paper_id)

    async def get_project_papers(self, project_id: str) -> List[NormalizedPaper]:
        paper_ids = self._project_papers.get(project_id, [])
        return [self._papers[pid] for pid in paper_ids if pid in self._papers]
