"""Detects qualitative, ambiguous requirement terms."""

from typing import Dict, List


class AmbiguityDetector:
    VAGUE_TERMS = [
        "low power",
        "ultra low power",
        "compact",
        "small form factor",
        "fast",
        "high speed",
        "efficient",
        "cheap",
        "low cost",
        "heavy duty",
        "rugged",
        "lightweight",
    ]

    @classmethod
    def check_ambiguity(cls, text: str) -> Dict[str, any]:
        lower = text.lower()
        detected = [term for term in cls.VAGUE_TERMS if term in lower]
        return {
            "is_ambiguous": len(detected) > 0,
            "isAmbiguous": len(detected) > 0,
            "detected_terms": detected,
            "detectedTerms": detected,
        }

    @classmethod
    def checkAmbiguity(cls, text: str) -> Dict[str, any]:
        return cls.check_ambiguity(text)
