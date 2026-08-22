"""Configurable embedding provider abstraction for Workline vector retrieval."""

import hashlib
import math
import os
from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    """Abstract interface for text embedding generation."""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for text string."""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Return embedding vector dimension."""
        pass


class LocalEmbeddingProvider(EmbeddingProvider):
    """
    Deterministic lightweight local embedding provider.
    Ensures zero external API dependency and fast execution.
    """

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        """Generate a normalized pseudo-semantic embedding vector from input text."""
        if not text:
            return [0.0] * self.dimension

        # Generate deterministic vector using token hash distributions
        vector = [0.0] * self.dimension
        words = text.lower().split()
        for idx, word in enumerate(words):
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            pos = h % self.dimension
            val = ((h >> 8) % 1000) / 1000.0 - 0.5
            vector[pos] += val * (1.0 / (math.log(idx + 2)))

        # Normalize vector to unit length
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]

        return vector

    def get_dimension(self) -> int:
        return self.dimension


class APIEmbeddingProvider(EmbeddingProvider):
    """Remote API embedding provider stub."""

    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self.fallback = LocalEmbeddingProvider(dimension=dimension)

    def embed_text(self, text: str) -> List[float]:
        # Gracefully fall back to local provider if API is not configured
        return self.fallback.embed_text(text)

    def get_dimension(self) -> int:
        return self.dimension


def get_embedding_provider() -> EmbeddingProvider:
    """Factory returning configured embedding provider."""
    provider_type = os.environ.get("WORKLINE_EMBEDDING_PROVIDER", "local").lower()
    if provider_type == "api":
        return APIEmbeddingProvider()
    return LocalEmbeddingProvider(dimension=384)
