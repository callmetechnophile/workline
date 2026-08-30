"""
Search query planning and strategy generator for ResearchPaperAgent.
Deconstructs project context into focused, multi-angle academic search queries.
"""

import re
from typing import List, Set
from research_agents.research_paper_agent.schemas import ResearchPaperAgentInput


class QueryPlanner:
    """Generates focused search queries from structured project parameters."""

    STOP_WORDS = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "are", "was", "were", "using",
        "system", "project", "design", "development", "architecture", "overview",
        "based", "via", "towards", "study", "analysis", "paper", "research",
    }

    def plan_queries(self, input_data: ResearchPaperAgentInput, max_queries: int = 5) -> List[str]:
        """
        Generates distinct search queries targeting domain, objectives,
        components, technologies, and constraints.
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

        # 1. Primary Keyword / Concept Queries
        for kw in keywords[:2]:
            add_query(f"{kw} {domain}".strip())

        # 2. Objective-focused Queries
        for obj in objectives[:2]:
            primary_kw = keywords[0] if keywords else title
            add_query(f"{obj} {primary_kw}".strip())

        # 3. Component + Technology Queries
        if components and technologies:
            add_query(f"{technologies[0]} {components[0]} {domain}".strip())
        elif technologies:
            add_query(f"{technologies[0]} {domain}".strip())
        elif components:
            add_query(f"{components[0]} {domain}".strip())

        # 4. Constraint + Technology / Objective Queries
        if constraints and (technologies or objectives):
            tech = technologies[0] if technologies else objectives[0]
            add_query(f"{constraints[0]} {tech}".strip())

        # 5. Core Title Extraction Fallback
        if len(queries) < 2:
            title_keywords = self._extract_key_phrases(title)
            if title_keywords:
                add_query(f"{' '.join(title_keywords)} {domain}".strip())

        # 6. Description Key Concept Fallback
        if len(queries) < max_queries and input_data.project_description:
            desc_keywords = self._extract_key_phrases(input_data.project_description)
            if len(desc_keywords) >= 3:
                add_query(" ".join(desc_keywords[:4]))

        return queries[:max_queries]

    def _clean_query(self, query: str) -> str:
        """Removes punctuation and normalizes query whitespace."""
        query = re.sub(r"[^\w\s-]", " ", query)
        words = [w.strip() for w in query.split() if w.strip()]
        return " ".join(words)

    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extracts informative content words from raw text."""
        cleaned = re.sub(r"[^\w\s]", " ", text)
        words = [
            w.strip()
            for w in cleaned.split()
            if w.strip() and len(w) > 2 and w.lower() not in self.STOP_WORDS
        ]
        return words
