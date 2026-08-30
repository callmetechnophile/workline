"""
Deterministic mock reasoning provider for BOMOptimizationAgent offline testing and CLI demo mode.
"""

from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from research_agents.bom_optimization_agent.providers.base import ReasoningProvider

T = TypeVar("T", bound=BaseModel)


class MockBOMOptimizationProvider(ReasoningProvider):
    """Deterministic offline reasoning provider simulating Bedrock trade-off analysis."""

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        return (
            "The Lowest Landed Cost strategy consolidates 4 orders across Robu.in and Mouser Electronics, "
            "saving ₹3,850 in freight overhead compared to fragmented per-component purchasing."
        )

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        data = {
            "strategy_id": "STRAT-001",
            "name": "Lowest Landed Cost",
            "objective": "minimize_landed_cost",
            "total_product_cost": 70000.0,
            "total_shipping_cost": 450.0,
            "total_known_landed_cost": 70450.0,
            "supplier_count": 2,
            "estimated_delivery_days": 3,
            "constraints_satisfied": True,
            "warnings": [],
        }
        return schema.model_validate(data)
