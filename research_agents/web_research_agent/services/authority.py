"""
Heuristic source authority evaluation service for WebResearchAgent.
Assigns verifiable authority scores between 0.0 and 1.0 with transparent rationales.
"""

from typing import List, Tuple
from research_agents.web_research_agent.schemas import SourceTypeEnum


class AuthorityEvaluator:
    """Computes heuristic authority scores based on source classification and domain trust."""

    AUTHORITY_TIERS = {
        "official_documentation": (0.95, "Official authoritative technical documentation"),
        "manufacturer": (0.95, "Primary hardware manufacturer / component vendor"),
        "datasheet": (0.95, "Authoritative component datasheet / engineering specifications"),
        "standard": (0.98, "Official standards organization / protocol specification"),
        "application_note": (0.92, "Manufacturer application note with verified reference designs"),
        "github_repository": (0.90, "Public engineering source code repository"),
        "engineering_project": (0.85, "Documented open-source engineering build / project"),
        "product_page": (0.85, "Primary vendor product specifications page"),
        "technical_article": (0.80, "Established engineering publication / technical guide"),
        "tutorial": (0.75, "Step-by-step technical implementation tutorial"),
        "vendor": (0.70, "Authorized electronic component distributor"),
        "technical_blog": (0.60, "Technical blog / practitioner writeup"),
        "documentation": (0.85, "Technical reference documentation"),
        "forum": (0.40, "Community discussion / developer forum thread"),
        "other": (0.30, "General web reference"),
    }

    def evaluate_authority(self, source_type: SourceTypeEnum, domain: str) -> Tuple[float, List[str]]:
        """
        Calculates authority score and returns explanatory reasons.

        Returns:
            (authority_score, [authority_reasons])
        """
        base_score, reason = self.AUTHORITY_TIERS.get(
            source_type, (0.30, "General web reference")
        )
        reasons: List[str] = [reason]

        # Domain-specific heuristic boosts
        if domain.endswith(".edu") or domain.endswith(".ac.uk"):
            base_score = max(base_score, 0.90)
            reasons.append(f"Academic institution domain ({domain})")
        elif domain.endswith(".gov") or domain.endswith(".mil"):
            base_score = max(base_score, 0.96)
            reasons.append(f"Government / regulatory agency domain ({domain})")
        elif "github.com" in domain:
            reasons.append("Verifiable Git revision control and open source history")
        elif any(d in domain for d in ("ti.com", "st.com", "analog.com", "nvidia.com", "espressif.com")):
            reasons.append(f"Primary semiconductor / platform vendor ({domain})")

        final_score = round(max(0.0, min(1.0, base_score)), 2)
        return final_score, reasons
