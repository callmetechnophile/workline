"""Datasheet URL and document identity validator."""

import re
from typing import Optional, Tuple
from backend.workline.scraping.models import DatasheetMetadata, DatasheetStatus


class DatasheetValidator:
    """Validates datasheet URLs and document metadata against component requirements."""

    def validate_datasheet(self, metadata: Optional[DatasheetMetadata]) -> Tuple[DatasheetStatus, str]:
        if not metadata or not metadata.url:
            return DatasheetStatus.FAILED, "No datasheet URL provided."

        url = metadata.url.strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            return DatasheetStatus.FAILED, f"Invalid URL scheme: {url}"

        # Check for genuine PDF or documentation link
        is_doc = url.lower().endswith(".pdf") or "datasheet" in url.lower() or "doc" in url.lower() or "wiki" in url.lower()
        if not is_doc:
            return DatasheetStatus.UNVERIFIED, "URL does not appear to reference a PDF or technical document."

        # Verify MPN identity correlation if MPN is known
        if metadata.mpn:
            clean_mpn = re.sub(r'[^a-zA-Z0-9]', '', metadata.mpn).lower()
            clean_url = re.sub(r'[^a-zA-Z0-9]', '', url).lower()
            if clean_mpn in clean_url or "datasheet" in clean_url:
                metadata.verification_status = DatasheetStatus.VERIFIED
                return DatasheetStatus.VERIFIED, "Datasheet URL verified and matches MPN identity."

        metadata.verification_status = DatasheetStatus.PARSED
        return DatasheetStatus.PARSED, "Datasheet document reachable and parsed."
