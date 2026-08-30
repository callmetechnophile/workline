"""
Deterministic mock reasoning provider for EngineeringValidationAgent offline testing and CLI demo mode.
"""

from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from research_agents.engineering_validation_agent.providers.base import ReasoningProvider

T = TypeVar("T", bound=BaseModel)


class MockEngineeringValidationProvider(ReasoningProvider):
    """Deterministic offline reasoning provider simulating Bedrock engineering explanations."""

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        return (
            "The engineering design satisfies all electrical voltage rails, power budget constraints, "
            "and communication protocols. All critical subsystems maintain valid BOM components."
        )

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        data = {
            "verdict": "READY",
            "critical_failures": 0,
            "high_failures": 0,
            "medium_failures": 0,
            "warnings": 0,
            "unknowns": 0,
            "requirements_passed": 12,
            "requirements_failed": 0,
            "requirements_unknown": 0,
            "recommendation": "Design satisfies all engineering rules and is ready for execution.",
        }
        return schema.model_validate(data)
