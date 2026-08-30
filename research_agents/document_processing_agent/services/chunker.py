"""
Semantic hierarchical chunker for DocumentProcessingAgent.
Partitions sections and paragraph groups into coherent chunks with page bounds and token estimation.
"""

from typing import List, Optional
from research_agents.document_processing_agent.config import doc_config
from research_agents.document_processing_agent.schemas import (
    DocumentChunk,
    ExtractedSection,
)


class SemanticChunker:
    """Chunks documents hierarchically by Section -> Paragraph Group."""

    def __init__(self, max_tokens: Optional[int] = None):
        self.max_tokens = max_tokens or doc_config.max_chunk_tokens

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Rough token estimation (~4 chars per token)."""
        return max(1, len(text) // 4)

    def chunk_document(
        self,
        document_id: str,
        sections: List[ExtractedSection],
        source_url: Optional[str] = None,
    ) -> List[DocumentChunk]:
        """
        Creates semantic chunks respecting section boundaries and token limits.
        """
        chunks: List[DocumentChunk] = []
        chunk_idx = 0

        for section in sections:
            if not section.text.strip():
                continue

            section_tokens = self.estimate_tokens(section.text)

            # If section fits within maximum token size, keep as a single semantic unit
            if section_tokens <= self.max_tokens:
                chunk_idx += 1
                c_start = section.blocks[0].character_start if section.blocks else 0
                c_end = section.blocks[-1].character_end if section.blocks else len(section.text)
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{document_id}_chunk_{chunk_idx}",
                        document_id=document_id,
                        text=section.text,
                        section=section.section_title,
                        page_start=section.page_start,
                        page_end=section.page_end,
                        source_url=source_url,
                        character_start=c_start,
                        character_end=c_end,
                        token_estimate=section_tokens,
                    )
                )
            else:
                # Subdivide section by blocks or paragraph groups
                current_paragraphs: List[str] = []
                current_tokens = 0
                p_start = section.page_start
                p_end = section.page_start
                first_block_start = 0
                last_block_end = 0

                for b in section.blocks:
                    b_tokens = self.estimate_tokens(b.text)
                    if current_tokens + b_tokens > self.max_tokens and current_paragraphs:
                        # Flush chunk
                        chunk_idx += 1
                        chunk_text = "\n\n".join(current_paragraphs)
                        chunks.append(
                            DocumentChunk(
                                chunk_id=f"{document_id}_chunk_{chunk_idx}",
                                document_id=document_id,
                                text=chunk_text,
                                section=section.section_title,
                                page_start=p_start,
                                page_end=p_end,
                                source_url=source_url,
                                character_start=first_block_start,
                                character_end=last_block_end,
                                token_estimate=current_tokens,
                            )
                        )
                        current_paragraphs = [b.text]
                        current_tokens = b_tokens
                        p_start = b.page_number
                        p_end = b.page_number
                        first_block_start = b.character_start
                        last_block_end = b.character_end
                    else:
                        if not current_paragraphs:
                            first_block_start = b.character_start
                            p_start = b.page_number
                        current_paragraphs.append(b.text)
                        current_tokens += b_tokens
                        p_end = b.page_number
                        last_block_end = b.character_end

                if current_paragraphs:
                    chunk_idx += 1
                    chunk_text = "\n\n".join(current_paragraphs)
                    chunks.append(
                        DocumentChunk(
                            chunk_id=f"{document_id}_chunk_{chunk_idx}",
                            document_id=document_id,
                            text=chunk_text,
                            section=section.section_title,
                            page_start=p_start,
                            page_end=p_end,
                            source_url=source_url,
                            character_start=first_block_start,
                            character_end=last_block_end,
                            token_estimate=current_tokens,
                        )
                    )

        return chunks
