"""Component candidate structural validator."""

from typing import List, Tuple
from backend.workline.scraping.models import ComponentCandidate


class ComponentStructuralValidator:
    """Validates structural integrity and non-emptiness of ComponentCandidate models."""

    def validate_candidate(self, candidate: ComponentCandidate) -> Tuple[bool, List[str]]:
        issues = []
        if not candidate.manufacturer or candidate.manufacturer == "Generic":
            issues.append("Manufacturer is unspecified or generic.")

        if not candidate.manufacturer_part_number:
            issues.append("Manufacturer Part Number (MPN) is missing.")

        if not candidate.listings:
            issues.append("No active vendor listings associated with component.")

        return len(issues) == 0, issues
