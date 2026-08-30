"""
Amazon Bedrock reasoning provider adapter for EngineeringValidationAgent.
Reuses the battle-tested BedrockProvider from deep_research_agent.
"""

from research_agents.deep_research_agent.providers.bedrock import BedrockProvider

__all__ = ["BedrockProvider"]
