"""
Deterministic source type classification service for WebResearchAgent.
Categorizes web evidence sources into allowed engineering source types.
"""

from urllib.parse import urlparse
from typing import Tuple
from research_agents.web_research_agent.schemas import RawWebResult, SourceTypeEnum


class SourceClassifier:
    """Classifies web evidence URLs, domains, and titles into verified SourceTypeEnum categories."""

    MANUFACTURER_DOMAINS = {
        "ti.com", "st.com", "analog.com", "espressif.com", "nxp.com", "microchip.com",
        "intel.com", "nvidia.com", "arm.com", "nordicsemi.com", "infineon.com",
        "renesas.com", "qualcomm.com", "xilinx.com", "amd.com", "te.com"
    }

    VENDOR_DOMAINS = {
        "digikey.com", "mouser.com", "element14.com", "farnell.com", "arrow.com",
        "adafruit.com", "sparkfun.com", "seeedstudio.com", "pololu.com", "dfrobot.com"
    }

    FORUM_DOMAINS = {
        "reddit.com", "stackoverflow.com", "eevblog.com", "stackexchange.com",
        "forum.allaboutcircuits.com", "forums.raspberrypi.com", "community.element14.com"
    }

    STANDARDS_DOMAINS = {
        "ieee.org", "iso.org", "ietf.org", "w3.org", "bluetooth.com", "usb.org",
        "can-cia.org", "autosar.org", "sae.org"
    }

    def classify(self, result: RawWebResult) -> Tuple[SourceTypeEnum, str]:
        """
        Determines the source type category and rationale.

        Returns:
            (SourceTypeEnum, domain_string)
        """
        parsed = urlparse(result.url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

        path = parsed.path.lower()
        title_lower = result.title.lower()
        content_lower = (result.snippet or result.content or "").lower()

        # 1. GitHub Repository Check
        if "github.com" in domain:
            parts = [p for p in path.split("/") if p]
            if len(parts) >= 2:
                return "github_repository", domain
            return "engineering_project", domain

        # 2. Datasheet Check
        if path.endswith(".pdf") or "datasheet" in path or "datasheet" in title_lower:
            return "datasheet", domain

        # 3. Application Note Check
        if "appnote" in path or "application-note" in path or "an-" in path or "application note" in title_lower:
            return "application_note", domain

        # 4. Standards Body Check
        if any(std in domain for std in self.STANDARDS_DOMAINS):
            return "standard", domain

        # 5. Manufacturer Check
        if any(mfg in domain for mfg in self.MANUFACTURER_DOMAINS):
            if "doc" in path or "manual" in path or "guide" in path:
                return "official_documentation", domain
            if "product" in path or "part" in path:
                return "product_page", domain
            return "manufacturer", domain

        # 6. Vendor / Distributor Check
        if any(v in domain for v in self.VENDOR_DOMAINS):
            if "product" in path or "item" in path or "p/" in path:
                return "product_page", domain
            return "vendor", domain

        # 7. Documentation Site Check
        if domain.startswith("docs.") or domain.startswith("documentation.") or "/docs" in path or "readthedocs.io" in domain:
            return "official_documentation", domain

        # 8. Forum Check
        if any(f in domain for f in self.FORUM_DOMAINS):
            return "forum", domain

        # 9. Tutorial & Blog Checks
        if "tutorial" in title_lower or "how-to" in path or "tutorial" in path:
            return "tutorial", domain

        if "medium.com" in domain or "dev.to" in domain or "blog" in domain or "/blog" in path:
            return "technical_blog", domain

        if "hackaday.com" in domain or "hackster.io" in domain or "instructables.com" in domain:
            return "engineering_project", domain

        # 10. Technical Article / Generic Documentation Fallback
        if "article" in path or "guide" in path or "technical" in content_lower:
            return "technical_article", domain

        return "other", domain
