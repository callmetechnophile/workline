from research_agents.engineering_optimization.providers.base import ReasoningProvider


class MockOptimizationProvider(ReasoningProvider):
    async def explain_tradeoff(self, prompt: str, system_prompt: str = "") -> str:
        return (
            "Pareto-optimal candidate selected: minimum power dissipation within hard thermal "
            "constraint (Tj <= 80 degC) and cost budget (USD 5.00). No hard constraint violations."
        )
