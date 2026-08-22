"""spaCy NLP linguistic enrichment and engineering entity extraction."""

import re
import time
from typing import List, Tuple
from backend.workline.documents.models import (
    DocumentRecord,
    EngineeringEntity,
    EngineeringEntityType,
)
from backend.workline.documents.spacy.normalizer import EntityNormalizer


class SpacyEnricher:
    """Enriches structured documents with sentence boundaries and domain-specific NER."""

    @classmethod
    def enrich(cls, document: DocumentRecord) -> List[EngineeringEntity]:
        entities: List[EngineeringEntity] = []
        counter = 1

        for sec in document.sections:
            for p in sec.paragraphs:
                # 1. Sentence splitting
                sentences = re.split(r"(?<=[.?!])\s+", p)

                for sent in sentences:
                    # Detect Voltage
                    for m in re.finditer(r"\b(\d+(?:\.\d+)?\s*(?:V|mV|kV)|\d+V\d+)\b", sent, re.IGNORECASE):
                        raw = m.group(0)
                        norm_val, unit = EntityNormalizer.normalize_voltage(raw)
                        entities.append(
                            EngineeringEntity(
                                entity_id=f"{document.document_id}_ent_{counter}",
                                project_id=document.project_id,
                                document_id=document.document_id,
                                entity_type=EngineeringEntityType.VOLTAGE,
                                original_text=raw,
                                normalized_value=norm_val,
                                unit=unit,
                                page_number=sec.page_number,
                                section=sec.heading,
                                confidence=0.95,
                                source_span=sent,
                                created_at=time.time(),
                            )
                        )
                        counter += 1

                    # Detect Current
                    for m in re.finditer(r"\b(\d+(?:\.\d+)?\s*(?:A|mA|uA|µA))\b", sent, re.IGNORECASE):
                        raw = m.group(0)
                        norm_val, unit = EntityNormalizer.normalize_current(raw)
                        entities.append(
                            EngineeringEntity(
                                entity_id=f"{document.document_id}_ent_{counter}",
                                project_id=document.project_id,
                                document_id=document.document_id,
                                entity_type=EngineeringEntityType.CURRENT,
                                original_text=raw,
                                normalized_value=norm_val,
                                unit=unit,
                                page_number=sec.page_number,
                                section=sec.heading,
                                confidence=0.92,
                                source_span=sent,
                                created_at=time.time(),
                            )
                        )
                        counter += 1

                    # Detect Part Numbers / ICs (e.g. TPS62130, STM32F401, LM2596, ESP32-WROOM)
                    for m in re.finditer(r"\b([A-Z]{2,}[0-9]+[A-Z0-9_-]*)\b", sent):
                        raw = m.group(0)
                        entities.append(
                            EngineeringEntity(
                                entity_id=f"{document.document_id}_ent_{counter}",
                                project_id=document.project_id,
                                document_id=document.document_id,
                                entity_type=EngineeringEntityType.COMPONENT,
                                original_text=raw,
                                normalized_value=raw.upper(),
                                page_number=sec.page_number,
                                section=sec.heading,
                                confidence=0.96,
                                source_span=sent,
                                created_at=time.time(),
                            )
                        )
                        counter += 1

        return entities
