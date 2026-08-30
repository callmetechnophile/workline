"""
Unit tests for Amazon Bedrock provider adapter and botocore error translation.
"""

from unittest.mock import MagicMock
import pytest
from botocore.exceptions import ClientError, ConnectTimeoutError
from pydantic import BaseModel

from research_agents.deep_research_agent.providers.base import (
    ModelUnavailableError,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)
from research_agents.deep_research_agent.providers.bedrock import BedrockProvider


class SampleStructuredOutput(BaseModel):
    summary: str
    score: float


@pytest.mark.asyncio
async def test_bedrock_generate_success():
    mock_client = MagicMock()
    mock_client.converse.return_value = {
        "output": {
            "message": {
                "content": [{"text": "Synthetic hardware evaluation for Jetson Orin Nano."}]
            }
        }
    }

    provider = BedrockProvider(bedrock_client=mock_client)
    res = await provider.generate("Evaluate Jetson Orin Nano for drone payload.")
    assert "Jetson Orin Nano" in res
    mock_client.converse.assert_called_once()


@pytest.mark.asyncio
async def test_bedrock_generate_structured_success():
    mock_client = MagicMock()
    mock_client.converse.return_value = {
        "output": {
            "message": {
                "content": [{"text": '```json\n{"summary": "Real-time edge inference verified", "score": 0.96}\n```'}]
            }
        }
    }

    provider = BedrockProvider(bedrock_client=mock_client)
    result = await provider.generate_structured(
        prompt="Analyze latency",
        schema=SampleStructuredOutput,
    )
    assert result.summary == "Real-time edge inference verified"
    assert result.score == 0.96


@pytest.mark.asyncio
async def test_bedrock_auth_error_translation():
    mock_client = MagicMock()
    mock_client.converse.side_effect = ClientError(
        {"Error": {"Code": "AccessDeniedException", "Message": "Invalid AWS token"}},
        "converse",
    )

    provider = BedrockProvider(bedrock_client=mock_client)
    with pytest.raises(ProviderAuthenticationError):
        await provider.generate("Test query")


@pytest.mark.asyncio
async def test_bedrock_rate_limit_error_translation():
    mock_client = MagicMock()
    mock_client.converse.side_effect = ClientError(
        {"Error": {"Code": "ThrottlingException", "Message": "Rate limit exceeded"}},
        "converse",
    )

    provider = BedrockProvider(bedrock_client=mock_client)
    with pytest.raises(ProviderRateLimitError) as exc:
        await provider.generate("Test query")
    assert exc.value.retryable is True


@pytest.mark.asyncio
async def test_bedrock_model_unavailable_translation():
    mock_client = MagicMock()
    mock_client.converse.side_effect = ClientError(
        {"Error": {"Code": "ResourceNotFoundException", "Message": "Model not found"}},
        "converse",
    )

    provider = BedrockProvider(bedrock_client=mock_client)
    with pytest.raises(ModelUnavailableError):
        await provider.generate("Test query")
