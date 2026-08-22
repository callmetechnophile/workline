"""Corsair integrations package."""

from backend.workline.interoperability.corsair.adapter import CorsairAdapter
from backend.workline.interoperability.corsair.client import CorsairClient
from backend.workline.interoperability.corsair.registry import CorsairRegistry
from backend.workline.interoperability.corsair.tools import CorsairTool, CorsairToolRegistry

__all__ = [
    "CorsairAdapter",
    "CorsairClient",
    "CorsairRegistry",
    "CorsairTool",
    "CorsairToolRegistry",
]
