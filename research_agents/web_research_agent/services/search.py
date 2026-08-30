"""
Web query generation service for WebResearchAgent.
Generates focused engineering web queries for GitHub repos, manufacturer docs, datasheets, and implementations.
"""

import re
from typing import List, Set
from research_agents.web_research_agent.schemas import WebResearchAgentInput


class WebQueryPlanner:
    """Generates focused web search queries across engineering angles."""

    STOP_WORDS = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "are", "was", "were", "using",
        "system", "project", "design", "development", "architecture", "overview",
        "towards", "study", "analysis", "web", "research",
    }

    def plan_queries(self, input_data: WebResearchAgentInput, max_queries: int = 6) -> List[str]:
        """
        Generates distinct search queries targeting GitHub repos, datasheets,
        component integrations, and technology implementations.
        """
        queries: List[str] = []
        seen: Set[str] = set()

        def add_query(q: str):
            cleaned = self._clean_query(q)
            norm = cleaned.lower()
            if cleaned and len(cleaned.split()) >= 2 and norm not in seen:
                seen.add(norm)
                queries.append(cleaned)

        title = input_data.project_title
        domain = input_data.engineering_domain or ""
        objectives = input_data.research_objectives or []
        components = input_data.components or []
        technologies = input_data.technologies or []
        constraints = input_data.constraints or []
        keywords = input_data.keywords or []
        target_sources = [s.lower() for s in input_data.target_sources]

        # 1. GitHub Open Source Project Query
        if "github" in target_sources or any("github" in k.lower() for k in keywords) or True:
            core_tech = technologies[0] if technologies else (components[0] if components else domain)
            add_query(f"GitHub {title} {core_tech}".strip())

        # 2. Manufacturer & Datasheet Queries
        for comp in components[:2]:
            add_query(f"{comp} datasheet manufacturer documentation".strip())
            if technologies:
                add_query(f"{comp} {technologies[0]} implementation example".strip())

        # 3. Technology / Framework Integration Queries
        for tech in technologies[:2]:
            if objectives:
                add_query(f"{tech} {objectives[0]} tutorial".strip())
            elif domain:
                add_query(f"{tech} {domain} engineering documentation".strip())

        # 4. Constraint + Component Operational Query
        if constraints and components:
            add_query(f"{components[0]} {constraints[0]} benchmark".strip())

        # 5. Keyword Concept Queries
        for kw in keywords[:2]:
            add_query(f"{kw} {domain}".strip())

        # 6. Fallback from Project Title
        if len(queries) < 3:
            title_words = [
                w for w in re.sub(r"[^\w\s]", " ", title).split()
                if w.lower() not in self.STOP_WORDS and len(w) > 2
            ]
            if title_words:
                add_query(f"{' '.join(title_words)} engineering implementation")

        return queries[:max_queries]

    def _clean_query(self, query: str) -> str:
        """Removes punctuation and normalizes query whitespace."""
        query = re.sub(r"[^\w\s-]", " ", query)
        words = [w.strip() for w in query.split() if w.strip()]
        return " ".join(words)
