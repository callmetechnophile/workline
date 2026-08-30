from abc import ABC, abstractmethod


class ReasoningProvider(ABC):
    @abstractmethod
    async def explain_tradeoff(self, prompt: str, system_prompt: str = "") -> str:
        pass
