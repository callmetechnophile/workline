"""
WORKLINE AI Agent Runtime.
Connects agent reasoning, domain tools, and local Moss retrieval.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from cli.workline.agent.query import ProjectAnswer, ask_project_question
from cli.workline.config.config import WorklineCLIConfig
from cli.workline.retrieval.record import EngineeringRecord
from cli.workline.retrieval.retriever import ProjectRetriever


class WorklineAgent:
    """
    Local WORKLINE Agent.
    Operates over local .wl project filesystem using ProjectRetriever and Local Moss.
    """

    def __init__(
        self,
        project_root: Path,
        retriever: Optional[ProjectRetriever] = None,
        config: Optional[WorklineCLIConfig] = None,
    ):
        self.project_root = project_root.resolve()
        self.retriever = retriever or ProjectRetriever(self.project_root)
        self.config = config or WorklineCLIConfig.load(self.project_root)

    def ask(self, question: str) -> ProjectAnswer:
        """Answer a natural language engineering question using local project context."""
        return ask_project_question(self.retriever, question, self.config)

    def get_project_summary(self) -> Dict[str, Any]:
        """Retrieve authoritative project summary from README.wl and manifest."""
        records = self.retriever.retrieve("project summary identity", top_k=2, resource_types=["project"])
        return {
            "root": str(self.project_root),
            "record": records[0].to_dict() if records else None,
        }

    def get_components(self, subsystem: Optional[str] = None) -> List[EngineeringRecord]:
        """Retrieve all components, optionally filtered by subsystem."""
        filters = {"subsystem": subsystem} if subsystem else None
        return self.retriever.retrieve(
            query=f"component {subsystem or ''}",
            top_k=50,
            resource_types=["component", "bom"],
            filters=filters,
        )

    def get_requirements(self, category: Optional[str] = None) -> List[EngineeringRecord]:
        """Retrieve requirements, optionally filtered by category."""
        filters = {"category": category} if category else None
        return self.retriever.retrieve(
            query=f"requirement {category or ''}",
            top_k=50,
            resource_types=["requirement"],
            filters=filters,
        )

    def get_active_tasks(self, assignee: Optional[str] = None) -> List[EngineeringRecord]:
        """Retrieve active tasks."""
        return self.retriever.lookup_tasks(status="open", assignee=assignee)

    def get_decisions(self) -> List[EngineeringRecord]:
        """Retrieve architectural decisions."""
        return self.retriever.retrieve(
            query="architectural decision record trade-off",
            top_k=30,
            resource_types=["decision"],
        )
