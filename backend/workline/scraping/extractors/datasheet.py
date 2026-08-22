"""Datasheet metadata and text extractor."""

import re
from typing import List, Optional
from backend.workline.scraping.models import DatasheetMetadata, DatasheetStatus


class DatasheetExtractor:
    """Extracts and verifies datasheet metadata from raw URLs."""

    def extract_datasheet(
        self,
        url: Optional[str],
        manufacturer: Optional[str] = None,
        mpn: Optional[str] = None,
    ) -> Optional[DatasheetMetadata]:
        if not url or not url.strip():
            return None

        clean_url = url.strip()
        doc_type = "Datasheet"
        if "manual" in clean_url.lower() or "guide" in clean_url.lower():
            doc_type = "User Manual"
        elif "app" in clean_url.lower() or "note" in clean_url.lower():
            doc_type = "Application Note"

        # Generate unique datasheet ID based on MPN or URL hash
        safe_mpn = (mpn or "unknown").lower().replace("/", "_").replace("-", "_")
        ds_id = f"datasheet:{safe_mpn}"

        return DatasheetMetadata(
            datasheet_id=ds_id,
            url=clean_url,
            manufacturer=manufacturer,
            mpn=mpn,
            title=f"{manufacturer or ''} {mpn or ''} {doc_type}".strip(),
            document_type=doc_type,
            verification_status=DatasheetStatus.UNVERIFIED,
        )

    def chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Splits document text into semantic chunks for Qdrant embedding."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunks.append(" ".join(words[i : i + chunk_size]))
        return chunks
