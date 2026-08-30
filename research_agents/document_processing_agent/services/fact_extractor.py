"""
Engineering factual statement extractor with unit normalization and provenance.
Extracts explicit numerical technical claims (operating voltages, current limits, clock frequencies, power).
"""

import re
from typing import List
from research_agents.document_processing_agent.schemas import (
    EngineeringFact,
    ExtractedBlock,
)
from research_agents.document_processing_agent.services.unit_normalizer import UnitNormalizer


class EngineeringFactExtractor:
    """Extracts explicit factual statements from text blocks with unit normalization and provenance."""

    FACT_PATTERNS = [
        # Voltage
        (r"\b([A-Za-z0-9_-]+)?\s*(operates\s*at|supply\s*voltage\s*is|input\s*voltage\s*of|voltage\s*rating\s*is)?\s*(\d+(\.\d+)?\s*(V|mV|kV))\b", "operating_voltage"),
        # Current
        (r"\b([A-Za-z0-9_-]+)?\s*(draws|current\s*consumption\s*of|output\s*current\s*of|peak\s*current\s*is)?\s*(\d+(\.\d+)?\s*(mA|µA|uA|A))\b", "current_draw"),
        # Frequency
        (r"\b([A-Za-z0-9_-]+)?\s*(clock\s*frequency\s*of|operating\s*at|clocked\s*at|frequency\s*is)?\s*(\d+(\.\d+)?\s*(GHz|MHz|kHz|Hz))\b", "clock_frequency"),
        # Power
        (r"\b([A-Za-z0-9_-]+)?\s*(power\s*consumption\s*of|dissipates|rated\s*at)?\s*(\d+(\.\d+)?\s*(kW|mW|W))\b", "power_consumption"),
    ]

    def __init__(self):
        self.normalizer = UnitNormalizer()

    def extract_facts(self, document_id: str, blocks: List[ExtractedBlock]) -> List[EngineeringFact]:
        """
        Extracts verified engineering statements from document blocks with provenance.
        """
        facts: List[EngineeringFact] = []
        seen_statements = set()

        for b in blocks:
            # Split block into sentences
            sentences = re.split(r"(?<=[.!?])\s+", b.text)
            for sentence in sentences:
                sentence_clean = sentence.strip()
                if len(sentence_clean) < 15 or len(sentence_clean) > 220:
                    continue

                for pattern, attribute in self.FACT_PATTERNS:
                    match = re.search(pattern, sentence_clean, re.IGNORECASE)
                    if match:
                        norm_stmt = sentence_clean.lower()
                        if norm_stmt in seen_statements:
                            continue
                        seen_statements.add(norm_stmt)

                        raw_value_match = self.normalizer.UNIT_REGEX.search(sentence_clean)
                        raw_value_str = raw_value_match.group(0) if raw_value_match else None
                        norm_val, norm_unit = (
                            self.normalizer.normalize(raw_value_str)
                            if raw_value_str
                            else (None, None)
                        )

                        entity_candidate = match.group(1).strip() if match.group(1) else None

                        facts.append(
                            EngineeringFact(
                                fact=sentence_clean,
                                entity=entity_candidate,
                                attribute=attribute,
                                value=raw_value_str,
                                normalized_value=norm_val,
                                normalized_unit=norm_unit,
                                source_document=document_id,
                                page=b.page_number,
                                confidence=0.96,
                            )
                        )
                        break

        return facts
