"""
Evidence aggregation, normalization, validation, and classification service for DeepResearchAgent.
Unifies input from ResearchPaperAgent, WebResearchAgent, and DocumentProcessingAgent into EvidenceItem models.
"""

from typing import Any, Dict, List, Tuple
from research_agents.deep_research_agent.schemas import (
    DeepResearchAgentInput,
    EvidenceItem,
    EvidenceSourceTypeLiteral,
)


class EvidenceAggregator:
    """Aggregates and validates upstream research evidence into normalized EvidenceItem objects."""

    VALID_SOURCE_TYPES: List[EvidenceSourceTypeLiteral] = [
        "research_paper",
        "manufacturer_documentation",
        "datasheet",
        "application_note",
        "github_repository",
        "engineering_project",
        "technical_article",
        "tutorial",
        "vendor",
        "standard",
        "other",
    ]

    def aggregate_and_validate(
        self,
        input_data: DeepResearchAgentInput,
    ) -> Tuple[List[EvidenceItem], List[str]]:
        """
        Extracts, normalizes, and validates all evidence items from input arrays.

        Returns:
            (valid_evidence_items, validation_warnings)
        """
        evidence_items: List[EvidenceItem] = []
        warnings: List[str] = []
        counter = 0

        # 1. Ingest Research Papers (Agent #1)
        for idx, paper in enumerate(input_data.research_papers):
            text = paper.get("abstract") or paper.get("summary") or paper.get("text") or ""
            if not text.strip():
                warnings.append(f"Research paper #{idx + 1} ('{paper.get('title')}') has no abstract or text content; skipped.")
                continue

            counter += 1
            paper_id = paper.get("paper_id") or paper.get("doi") or f"paper_{idx + 1}"
            evidence_items.append(
                EvidenceItem(
                    evidence_id=f"ev_p_{counter:03d}",
                    source_id=paper_id,
                    source_type="research_paper",
                    source_url=paper.get("pdf_url") or paper.get("url"),
                    title=paper.get("title"),
                    text=text.strip(),
                    publication_date=paper.get("publication_date") or str(paper.get("year", "")),
                    confidence=float(paper.get("relevance_score", 0.95)),
                )
            )

        # 2. Ingest Web Sources (Agent #2)
        for idx, web in enumerate(input_data.web_sources):
            text = web.get("extracted_content") or web.get("description") or web.get("snippet") or ""
            if not text.strip():
                warnings.append(f"Web source #{idx + 1} ('{web.get('title')}') has no text content; skipped.")
                continue

            src_type = web.get("source_type", "other")
            if src_type not in self.VALID_SOURCE_TYPES:
                src_type = "other"

            counter += 1
            src_id = web.get("source_id") or f"web_{idx + 1}"
            evidence_items.append(
                EvidenceItem(
                    evidence_id=f"ev_w_{counter:03d}",
                    source_id=src_id,
                    source_type=src_type,
                    source_url=web.get("url"),
                    title=web.get("title"),
                    text=text.strip(),
                    publication_date=web.get("published_date"),
                    confidence=float(web.get("relevance_score", 0.90)),
                )
            )

        # 3. Ingest Processed Documents & Chunks (Agent #3)
        for idx, doc in enumerate(input_data.documents):
            doc_id = doc.get("document_id") or f"doc_{idx + 1}"
            doc_meta = doc.get("metadata") or {}
            doc_type = doc_meta.get("document_type") or "other"
            src_type: EvidenceSourceTypeLiteral = "research_paper" if doc_type == "pdf" else "technical_article"

            # Ingest chunks if available
            doc_chunks = doc.get("chunks") or []
            if doc_chunks:
                for c_idx, chunk in enumerate(doc_chunks):
                    c_text = chunk.get("text", "")
                    if not c_text.strip():
                        continue
                    counter += 1
                    evidence_items.append(
                        EvidenceItem(
                            evidence_id=f"ev_c_{counter:03d}",
                            source_id=chunk.get("chunk_id") or f"{doc_id}_c{c_idx + 1}",
                            document_id=doc_id,
                            source_type=src_type,
                            source_url=chunk.get("source_url") or doc_meta.get("url"),
                            title=doc_meta.get("title") or doc.get("title"),
                            text=c_text.strip(),
                            page=chunk.get("page_start"),
                            section=chunk.get("section"),
                            confidence=0.96,
                        )
                    )
            elif doc.get("markdown"):
                counter += 1
                evidence_items.append(
                    EvidenceItem(
                        evidence_id=f"ev_d_{counter:03d}",
                        source_id=doc_id,
                        document_id=doc_id,
                        source_type=src_type,
                        source_url=doc_meta.get("url"),
                        title=doc_meta.get("title"),
                        text=doc["markdown"][:3000].strip(),
                        confidence=0.95,
                    )
                )

        # 4. Ingest Raw Facts
        for idx, fact in enumerate(input_data.facts):
            f_text = fact.get("fact", "")
            if not f_text.strip():
                continue
            counter += 1
            evidence_items.append(
                EvidenceItem(
                    evidence_id=f"ev_f_{counter:03d}",
                    source_id=fact.get("source_document") or fact.get("source_id") or f"fact_{idx + 1}",
                    source_type="datasheet" if "voltage" in f_text.lower() else "other",
                    source_url=fact.get("source_url"),
                    text=f_text.strip(),
                    page=fact.get("page"),
                    confidence=float(fact.get("confidence", 0.95)),
                )
            )

        # 5. Ingest Standalone Chunks
        for idx, chunk in enumerate(input_data.chunks):
            c_text = chunk.get("text", "")
            if not c_text.strip():
                continue
            counter += 1
            evidence_items.append(
                EvidenceItem(
                    evidence_id=f"ev_sc_{counter:03d}",
                    source_id=chunk.get("chunk_id") or f"chunk_{idx + 1}",
                    document_id=chunk.get("document_id"),
                    source_type="research_paper",
                    source_url=chunk.get("source_url"),
                    text=c_text.strip(),
                    page=chunk.get("page_start"),
                    section=chunk.get("section"),
                    confidence=0.95,
                )
            )

        if not evidence_items:
            warnings.append("No valid text evidence found across research papers, web sources, or documents.")

        return evidence_items, warnings
