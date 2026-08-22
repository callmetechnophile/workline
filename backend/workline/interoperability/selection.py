"""Agent selection and ranking service."""

from typing import List, Optional, Tuple
from backend.workline.interoperability.capabilities import AgentStatus
from backend.workline.interoperability.registry import ExternalAgent, agent_registry


class AgentSelectionService:
    """Ranks and selects candidate agents based on capabilities, trust, reliability, and cost."""

    @classmethod
    def select_agent_for_capability(
        cls,
        capability_id: str,
        prefer_local: bool = True,
        max_cost: Optional[float] = None,
    ) -> Optional[Tuple[ExternalAgent, float]]:
        """Find best matching agent for a capability, returning (agent, ranking_score)."""
        candidates = agent_registry.discover_agents(capability_type=capability_id)
        if not candidates:
            return None

        ranked: List[Tuple[ExternalAgent, float]] = []

        for agent in candidates:
            if agent.status != AgentStatus.AVAILABLE:
                continue

            # Find matching capability
            matching_cap = next((c for c in agent.capabilities if c.capability_id == capability_id), None)
            if not matching_cap or not matching_cap.availability:
                continue

            if max_cost is not None and matching_cap.estimated_cost > max_cost:
                continue

            trust = agent_registry.get_trust_record(agent.agent_id)
            trust_score = trust.trust_score

            # Ranking score formula (0 - 100)
            score = trust_score * 50.0  # Up to 50 pts for trust

            # Local preference
            if prefer_local and "local" in (agent.endpoint or "").lower():
                score += 30.0

            # Cost penalty (lower cost preferred)
            cost_penalty = min(20.0, matching_cap.estimated_cost * 10.0)
            score += (20.0 - cost_penalty)

            ranked.append((agent, score))

        if not ranked:
            return None

        # Sort descending by score
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked[0]
