"""
Engineering evidence and structured technical fact extraction service for WebResearchAgent.
Extracts verifiable hardware parameters, specifications, interfaces, and repository details
with strict source provenance tracking.
"""

from datetime import datetime
import re
from typing import List, Optional
from research_agents.web_research_agent.schemas import ExtractedEngineeringFact, NormalizedWebSource


class EvidenceExtractor:
    """Extracts verifiable technical parameters and specifications with strict source provenance."""

    FACT_PATTERNS = [
        (r"\b(\d+(\.\d+)?\s*(V|mV|kV))\s*(operating|supply|input|voltage)?\b", "electrical"),
        (r"\b(ARM|Cortex-[MA]\d+|RISC-V|Xtensa|Dual-core|Quad-core|Octa-core|x86_64)\b", "compute"),
        (r"\b(Wi-Fi\s*6?|Bluetooth\s*(LE|5\.\d)?|CAN\s*(bus|FD)?|SPI|I2C|UART|USB-C|PCIe\s*(Gen\s*\d)?|Gigabit\s*Ethernet)\b", "interface"),
        (r"\b(\d+\s*(MB|GB|KB)\s*(SRAM|Flash|RAM|DDR\d?|LPDDR\d?))\b", "memory"),
        (r"\b(YOLOv\d+|ROS\s*2\s*(Humble|Iron|Jazzy)?|TensorRT|OpenCV|PyTorch|TensorFlow)\b", "software"),
        (r"\b(operating\s*temperature\s*:\s*[-+]?\d+\s*°?C\s*to\s*[-+]?\d+\s*°?C)\b", "environmental"),
    ]

    def extract_facts(
        self,
        source: NormalizedWebSource,
        components_filter: Optional[List[str]] = None,
        max_facts: int = 5,
    ) -> List[ExtractedEngineeringFact]:
        """
        Extracts verified engineering statements from source content and snippet.
        """
        facts: List[ExtractedEngineeringFact] = []
        seen_facts = set()

        text = f"{source.description or ''}\n{source.extracted_content or ''}"
        if not text.strip():
            return []

        retrieved_at = source.accessed_at or datetime.utcnow().isoformat()

        # 1. GitHub Repository Specific Provenance
        if source.source_type == "github_repository" and "github.com" in source.url:
            fact_desc = f"Open-source implementation repository for {source.title.split('-')[0].strip()}"
            if source.description:
                fact_desc += f": {source.description[:120]}"
            facts.append(
                ExtractedEngineeringFact(
                    fact=fact_desc,
                    source_id=source.source_id,
                    source_url=source.url,
                    extraction_method=source.source_tool,
                    confidence=0.95,
                    retrieved_at=retrieved_at,
                    category="software",
                )
            )
            seen_facts.add(fact_desc.lower())

        # 2. Sentences containing component specifications
        sentences = re.split(r"(?<=[.!?])\s+", text)
        for sentence in sentences:
            sentence_clean = sentence.strip()
            if len(sentence_clean) < 20 or len(sentence_clean) > 200:
                continue

            # Check matching patterns
            for pattern, category in self.FACT_PATTERNS:
                if re.search(pattern, sentence_clean, re.IGNORECASE):
                    # Check if sentence aligns with component
                    if components_filter:
                        if not any(c.lower() in sentence_clean.lower() for c in components_filter):
                            continue

                    norm = sentence_clean.lower()
                    if norm not in seen_facts:
                        seen_facts.add(norm)
                        facts.append(
                            ExtractedEngineeringFact(
                                fact=sentence_clean,
                                source_id=source.source_id,
                                source_url=source.url,
                                extraction_method=source.source_tool,
                                confidence=0.90,
                                retrieved_at=retrieved_at,
                                category=category,
                            )
                        )
                        if len(facts) >= max_facts:
                            return facts

        return facts
