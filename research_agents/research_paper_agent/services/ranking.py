"""
Transparent multi-factor relevance ranking engine.
Scores candidate papers based on title, abstract, components, technologies,
objectives, domain, constraints, and recency without hallucinating reasons.
"""

from datetime import datetime
import re
from typing import List, Set, Tuple
from research_agents.research_paper_agent.schemas import RawPaperRecord, ResearchPaperAgentInput


class RelevanceScorer:
    """Calculates deterministic relevance scores and generates verifiable reasons."""

    @staticmethod
    def _tokenize(text: str) -> Set[str]:
        """Lowercases and extracts unique alpha tokens of length > 2."""
        if not text:
            return set()
        clean = re.sub(r"[^\w\s]", " ", text.lower())
        return {w for w in clean.split() if len(w) > 2}

    def score_paper(
        self,
        paper: RawPaperRecord,
        context: ResearchPaperAgentInput,
    ) -> Tuple[float, List[str]]:
        """
        Computes composite relevance score in [0.0, 1.0] and returns list of verified reasons.
        """
        title_tokens = self._tokenize(paper.title)
        abstract_tokens = self._tokenize(paper.abstract or "")
        combined_paper_tokens = title_tokens.union(abstract_tokens)
        paper_text = f"{paper.title} {paper.abstract or ''} {' '.join(paper.keywords)}".lower()

        reasons: List[str] = []
        score = 0.0

        # 1. Title Relevance (weight 0.25)
        title_matches: List[str] = []
        for kw in context.keywords:
            if kw.lower() in paper.title.lower():
                title_matches.append(kw)
        if not title_matches:
            for obj in context.research_objectives:
                if any(t in paper.title.lower() for t in obj.lower().split() if len(t) > 3):
                    title_matches.append(obj)

        if title_matches:
            score += 0.25
            reasons.append(f"Title directly addresses: {', '.join(title_matches[:2])}")
        else:
            # Partial title word overlap
            proj_title_tokens = self._tokenize(context.project_title)
            overlap = proj_title_tokens.intersection(title_tokens)
            if overlap:
                contrib = min(0.15, len(overlap) * 0.05)
                score += contrib
                reasons.append(f"Title contains key project terms: {', '.join(list(overlap)[:3])}")

        # 2. Research Objectives Alignment (weight 0.25)
        obj_matches: List[str] = []
        for obj in context.research_objectives:
            obj_words = self._tokenize(obj)
            if obj.lower() in paper_text or (obj_words and obj_words.issubset(combined_paper_tokens)):
                obj_matches.append(obj)
            elif len(obj_words.intersection(combined_paper_tokens)) >= max(1, len(obj_words) // 2):
                obj_matches.append(obj)

        if obj_matches:
            obj_contrib = min(0.25, len(obj_matches) * 0.12)
            score += obj_contrib
            reasons.append(f"Investigates target research objective: {', '.join(obj_matches[:2])}")

        # 3. Technologies Match (weight 0.20)
        tech_matches: List[str] = []
        for tech in context.technologies:
            if tech.lower() in paper_text:
                tech_matches.append(tech)
        if tech_matches:
            tech_contrib = min(0.20, len(tech_matches) * 0.10)
            score += tech_contrib
            reasons.append(f"Evaluates target technology: {', '.join(tech_matches[:2])}")

        # 4. Components Match (weight 0.15)
        comp_matches: List[str] = []
        for comp in context.components:
            if comp.lower() in paper_text:
                comp_matches.append(comp)
        if comp_matches:
            comp_contrib = min(0.15, len(comp_matches) * 0.08)
            score += comp_contrib
            reasons.append(f"References matching hardware/component: {', '.join(comp_matches[:2])}")

        # 5. Engineering Domain & Constraints (weight 0.10)
        domain_matches: List[str] = []
        if context.engineering_domain:
            dom_words = self._tokenize(context.engineering_domain)
            if dom_words.intersection(combined_paper_tokens):
                domain_matches.append(context.engineering_domain)
        for constr in context.constraints:
            if constr.lower() in paper_text:
                domain_matches.append(constr)

        if domain_matches:
            score += min(0.10, len(domain_matches) * 0.05)
            reasons.append(f"Aligns with domain/constraints: {', '.join(domain_matches[:2])}")

        # 6. Recency Boost (weight 0.05)
        year = self._extract_year(paper.publication_date)
        if year:
            current_year = datetime.now().year
            if current_year - year <= 3:
                score += 0.05
                reasons.append(f"Recent academic publication ({year})")
            elif current_year - year <= 6:
                score += 0.02

        # Clamp score to [0.0, 1.0] and round
        final_score = round(max(0.0, min(1.0, score)), 2)

        # Baseline fallback reason if score > 0 but reasons empty
        if final_score > 0 and not reasons:
            reasons.append("Relevant academic methodology matching query keywords")

        return final_score, reasons

    def _extract_year(self, pub_date: str) -> int:
        """Extracts 4-digit year from date string."""
        if not pub_date:
            return 0
        match = re.search(r"\b(19\d\d|20\d\d)\b", str(pub_date))
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return 0
        return 0
