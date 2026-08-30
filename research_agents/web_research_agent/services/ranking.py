"""
Relevance ranking and scoring engine for WebResearchAgent.
Scores candidate web sources against project domain, objectives, components,
technologies, and constraints without hallucinating unsupported claims.
"""

import re
from typing import List, Set, Tuple
from research_agents.web_research_agent.schemas import RawWebResult, WebResearchAgentInput


class WebRelevanceScorer:
    """Computes multi-factor relevance scores in [0.0, 1.0] and verified reasons."""

    @staticmethod
    def _tokenize(text: str) -> Set[str]:
        if not text:
            return set()
        clean = re.sub(r"[^\w\s]", " ", text.lower())
        return {w for w in clean.split() if len(w) > 2}

    def score_source(
        self,
        result: RawWebResult,
        input_data: WebResearchAgentInput,
    ) -> Tuple[float, List[str]]:
        """
        Computes composite relevance score and returns list of verified reasons.

        Returns:
            (relevance_score, [relevance_reasons])
        """
        title_tokens = self._tokenize(result.title)
        body_tokens = self._tokenize(result.content or result.snippet or "")
        combined_tokens = title_tokens.union(body_tokens)
        source_text = f"{result.title} {result.content or ''} {result.snippet or ''}".lower()

        reasons: List[str] = []
        score = 0.0

        # 1. Title Keyword & Objective Alignment (weight 0.30)
        title_matches: List[str] = []
        for kw in input_data.keywords:
            if kw.lower() in result.title.lower():
                title_matches.append(kw)
        if not title_matches:
            for obj in input_data.research_objectives:
                if any(t in result.title.lower() for t in obj.lower().split() if len(t) > 3):
                    title_matches.append(obj)

        if title_matches:
            score += 0.30
            reasons.append(f"Title directly addresses: {', '.join(title_matches[:2])}")
        else:
            proj_title_tokens = self._tokenize(input_data.project_title)
            overlap = proj_title_tokens.intersection(title_tokens)
            if overlap:
                contrib = min(0.20, len(overlap) * 0.07)
                score += contrib
                reasons.append(f"Title contains project keywords: {', '.join(list(overlap)[:3])}")

        # 2. Components Match (weight 0.25)
        comp_matches: List[str] = []
        for comp in input_data.components:
            if comp.lower() in source_text:
                comp_matches.append(comp)
        if comp_matches:
            comp_contrib = min(0.25, len(comp_matches) * 0.13)
            score += comp_contrib
            reasons.append(f"Documents matching component: {', '.join(comp_matches[:2])}")

        # 3. Technologies Match (weight 0.20)
        tech_matches: List[str] = []
        for tech in input_data.technologies:
            if tech.lower() in source_text:
                tech_matches.append(tech)
        if tech_matches:
            tech_contrib = min(0.20, len(tech_matches) * 0.10)
            score += tech_contrib
            reasons.append(f"Implements matching technology: {', '.join(tech_matches[:2])}")

        # 4. Objectives & Constraints Alignment (weight 0.15)
        obj_matches: List[str] = []
        for obj in input_data.research_objectives:
            if obj.lower() in source_text:
                obj_matches.append(obj)
        for constr in input_data.constraints:
            if constr.lower() in source_text:
                obj_matches.append(constr)

        if obj_matches:
            obj_contrib = min(0.15, len(obj_matches) * 0.08)
            score += obj_contrib
            reasons.append(f"Addresses project objective/constraint: {', '.join(obj_matches[:2])}")

        # 5. Engineering Domain Match (weight 0.10)
        if input_data.engineering_domain:
            dom_words = self._tokenize(input_data.engineering_domain)
            if dom_words.intersection(combined_tokens):
                score += 0.10
                reasons.append(f"Aligns with engineering domain: {input_data.engineering_domain}")

        # Clamp score to [0.0, 1.0] and round
        final_score = round(max(0.0, min(1.0, score)), 2)

        if final_score > 0 and not reasons:
            reasons.append("Contains relevant technical terms matching project queries")

        return final_score, reasons
