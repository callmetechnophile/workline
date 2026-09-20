"""
Nexar / Octopart MCP Client for Workline.

Provides standardized Model Context Protocol (MCP) tool exposure and execution
for Octopart and Nexar component intelligence, datasheets, pricing, stock,
and specifications.

Integrates with:
- ArmorIQ cryptographic governance and audit receipts
- NexarClient & NexarProvider with caching
- Local in-memory caching for repeated queries and rate-limit mitigation
- Clean error handling (no stack traces to frontend)
"""

import asyncio
from datetime import datetime, timezone
import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional
from loguru import logger
from pydantic import BaseModel, Field

from backend.workline.procurement.providers.nexar import NexarClient, NexarProvider
from backend.workline.procurement.models import (
    ComponentCandidate,
    DatasheetMetadata,
    DatasheetStatus,
    VendorListing,
)
from backend.workline.procurement.cache import nexar_cache


class NexarMCPToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]


class NexarMCPResult(BaseModel):
    success: bool
    data: Any = None
    error: Optional[str] = None
    cached: bool = False
    source: str = "Nexar/Octopart"
    timestamp: float = Field(default_factory=time.time)


class NexarMCPClient:
    """
    Standardized MCP client interface for Octopart / Nexar component intelligence.
    """

    TOOL_SEARCH_COMPONENTS = "nexar_mcp_search"
    TOOL_LOOKUP_MPN = "nexar_mcp_lookup_mpn"
    TOOL_GET_DATASHEET = "nexar_mcp_get_datasheet"
    TOOL_GET_PRICING_AVAILABILITY = "nexar_mcp_get_pricing_availability"

    def __init__(
        self,
        provider: Optional[NexarProvider] = None,
        cache_ttl_seconds: int = 86400 * 2,  # 48 hour cache for stable parts
    ):
        self.provider = provider or NexarProvider()
        self.cache_ttl = cache_ttl_seconds
        self._memory_cache: Dict[str, Dict[str, Any]] = {}

    def get_tool_definitions(self) -> List[NexarMCPToolDefinition]:
        """Return MCP tool schemas."""
        return [
            NexarMCPToolDefinition(
                name=self.TOOL_SEARCH_COMPONENTS,
                description="Search electronic components in the Octopart / Nexar catalog by keyword, category, or generic part query.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search term (e.g. 'ESP32', 'STM32F405', '3.3V LDO', '10k 0603 resistor')"},
                        "limit": {"type": "integer", "description": "Maximum candidates to return", "default": 10},
                    },
                    "required": ["query"],
                },
            ),
            NexarMCPToolDefinition(
                name=self.TOOL_LOOKUP_MPN,
                description="Look up exact Manufacturer Part Number (MPN) in Octopart / Nexar with technical specs, packages, and manufacturer info.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "mpn": {"type": "string", "description": "Exact Manufacturer Part Number (e.g. 'ESP32-S3-WROOM-1-N8R8', 'TPS62130RGTR')"},
                    },
                    "required": ["mpn"],
                },
            ),
            NexarMCPToolDefinition(
                name=self.TOOL_GET_DATASHEET,
                description="Retrieve verified technical datasheet URL and document metadata for an MPN from Octopart / Nexar.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "mpn": {"type": "string", "description": "Manufacturer Part Number to retrieve datasheet for"},
                    },
                    "required": ["mpn"],
                },
            ),
            NexarMCPToolDefinition(
                name=self.TOOL_GET_PRICING_AVAILABILITY,
                description="Retrieve real-time distributor pricing, stock levels, and MOQ across authorized suppliers from Octopart / Nexar.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "mpn": {"type": "string", "description": "Manufacturer Part Number"},
                    },
                    "required": ["mpn"],
                },
            ),
        ]

    def _get_cache_key(self, tool_name: str, args: Dict[str, Any]) -> str:
        serialized = json.dumps(args, sort_keys=True)
        return f"mcp:{tool_name}:{hashlib.sha256(serialized.encode()).hexdigest()[:16]}"

    async def execute_tool(
        self,
        tool_name: str,
        args: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> NexarMCPResult:
        """
        Execute an MCP tool with caching, error boundaries, and telemetry.
        """
        cache_key = self._get_cache_key(tool_name, args)
        now = time.time()

        # Check in-memory cache
        if cache_key in self._memory_cache:
            entry = self._memory_cache[cache_key]
            if now - entry["cached_at"] < self.cache_ttl:
                return NexarMCPResult(
                    success=True,
                    data=entry["data"],
                    cached=True,
                    source="Nexar/Octopart (Cached)",
                )

        try:
            if tool_name == self.TOOL_SEARCH_COMPONENTS:
                query = args.get("query", "").strip()
                limit = int(args.get("limit", 10))
                if not query:
                    return NexarMCPResult(success=False, error="Search query is required.")
                
                candidates = await self.provider.search_components(query, limit=limit)
                serialized = [c.model_dump() for c in candidates]
                self._cache_result(cache_key, serialized)
                return NexarMCPResult(success=True, data=serialized)

            elif tool_name == self.TOOL_LOOKUP_MPN:
                mpn = args.get("mpn", "").strip()
                if not mpn:
                    return NexarMCPResult(success=False, error="MPN is required.")
                
                cand = await self.provider.search_mpn(mpn)
                if not cand:
                    return NexarMCPResult(success=True, data=None, error=f"No component found matching MPN '{mpn}'.")
                
                data = cand.model_dump()
                self._cache_result(cache_key, data)
                return NexarMCPResult(success=True, data=data)

            elif tool_name == self.TOOL_GET_DATASHEET:
                mpn = args.get("mpn", "").strip()
                if not mpn:
                    return NexarMCPResult(success=False, error="MPN is required.")
                
                datasheets = await self.provider.get_datasheets(mpn)
                data = [d.model_dump() for d in datasheets]
                self._cache_result(cache_key, data)
                return NexarMCPResult(success=True, data=data)

            elif tool_name == self.TOOL_GET_PRICING_AVAILABILITY:
                mpn = args.get("mpn", "").strip()
                if not mpn:
                    return NexarMCPResult(success=False, error="MPN is required.")
                
                listings = await self.provider.get_offers(mpn)
                data = [l.model_dump() for l in listings]
                self._cache_result(cache_key, data)
                return NexarMCPResult(success=True, data=data)

            else:
                return NexarMCPResult(
                    success=False,
                    error=f"Unsupported Nexar MCP tool '{tool_name}'. Available: {[t.name for t in self.get_tool_definitions()]}",
                )

        except Exception as exc:
            logger.warning(f"[NexarMCPClient] Tool '{tool_name}' failed: {exc}")
            return NexarMCPResult(
                success=False,
                error=f"Nexar MCP query failed: {str(exc)}",
            )

    def _cache_result(self, cache_key: str, data: Any):
        self._memory_cache[cache_key] = {
            "data": data,
            "cached_at": time.time(),
        }

    async def search_components(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Convenience method to search components."""
        res = await self.execute_tool(self.TOOL_SEARCH_COMPONENTS, {"query": query, "limit": limit})
        return res.data if res.success and res.data else []

    async def lookup_mpn(self, mpn: str) -> Optional[Dict[str, Any]]:
        """Convenience method to look up exact MPN."""
        res = await self.execute_tool(self.TOOL_LOOKUP_MPN, {"mpn": mpn})
        return res.data if res.success else None

    async def get_datasheet(self, mpn: str) -> Optional[Dict[str, Any]]:
        """Convenience method to get datasheet metadata."""
        res = await self.execute_tool(self.TOOL_GET_DATASHEET, {"mpn": mpn})
        if res.success and res.data and len(res.data) > 0:
            return res.data[0]
        return None

    async def get_pricing_availability(self, mpn: str) -> Optional[Dict[str, Any]]:
        """Convenience method to get pricing & stock availability."""
        res = await self.execute_tool(self.TOOL_GET_PRICING_AVAILABILITY, {"mpn": mpn})
        if res.success and res.data:
            listings = res.data
            if listings:
                total_stock = sum(l.get("stock", 0) for l in listings)
                valid_prices = [l.get("unit_price", 0.0) for l in listings if l.get("unit_price", 0.0) > 0]
                min_price = min(valid_prices) if valid_prices else 0.0
                currency = listings[0].get("currency", "USD")
                return {
                    "mpn": mpn,
                    "stock": total_stock,
                    "unit_price": min_price,
                    "currency": currency,
                    "listings": listings,
                }
        cand = await self.lookup_mpn(mpn)
        if cand:
            return {
                "mpn": mpn,
                "stock": cand.get("availability", {}).get("stock", 0),
                "unit_price": cand.get("pricing", {}).get("unit_price", 0.0),
                "currency": cand.get("pricing", {}).get("currency", "USD"),
            }
        return None


# Global singleton instance
nexar_mcp_client = NexarMCPClient()
