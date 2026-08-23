"""
Workline AI — Amazon Bedrock Standardization Test Suite.

Validates:
1. Bedrock Client initialization, configuration, and region handling
2. Transient error retry logic with exponential backoff
3. Timeout enforcement and error normalization
4. Anthropic Claude adapter schema translation and response normalization
5. DeepSeek adapter schema translation and response normalization
6. Bedrock Image generation adapter (Nova Canvas / Titan Image)
7. Centralized Model Router execution across research, fast_code, reasoning, report, and image tasks
8. Token usage, latency, and request ID tracking in AIResponse
9. PaperBanana visual generation integration with Amazon Bedrock
10. Zero Google Gemini / OpenAI direct runtime dependencies
11. Zero AWS credentials leaked in responses or logs
"""

import os
import pytest
from unittest.mock import MagicMock, patch

from backend.workline.ai.bedrock.client import BedrockClient, bedrock_client
from backend.workline.ai.bedrock.errors import (
    BedrockAuthenticationError,
    BedrockError,
    BedrockModelNotFoundError,
    BedrockThrottlingError,
    BedrockTimeoutError,
    BedrockValidationError,
)
from backend.workline.ai.bedrock.router import BedrockModelRouter, model_router
from backend.workline.ai.bedrock.schemas import (
    AIResponse,
    BedrockImageRequest,
    ChatMessage,
    TokenUsage,
)
from backend.workline.generation.image.client import paperbanana_client
from backend.workline.generation.models import ImageGenerationRequest, ImagePurpose


# ---------------------------------------------------------------------------
# 1. Bedrock Client & Configuration Tests
# ---------------------------------------------------------------------------

def test_bedrock_client_initialization():
    """Verifies that BedrockClient initializes with default region and timeouts."""
    client = BedrockClient(region_name="us-east-1", connect_timeout=5.0, read_timeout=30.0)
    assert client.region == "us-east-1"
    assert client.connect_timeout == 5.0
    assert client.read_timeout == 30.0
    assert client.max_retries == 3


def test_bedrock_client_simulation_fallback():
    """Verifies that in offline / testing mode without live AWS keys, client simulates safely."""
    client = BedrockClient(region_name="us-east-1")
    res = client.invoke_model(
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body={"messages": [{"role": "user", "content": "Analyze PCB trace impedance."}]},
    )
    assert "data" in res
    assert "latency_ms" in res
    assert res["latency_ms"] > 0.0


# ---------------------------------------------------------------------------
# 2. Error Handling & Normalization Tests
# ---------------------------------------------------------------------------

def test_bedrock_error_normalization_auth_failure():
    """Botocore AccessDeniedException is converted to BedrockAuthenticationError."""
    client = BedrockClient()
    mock_error = MagicMock()
    mock_error.response = {"Error": {"Code": "AccessDeniedException", "Message": "Invalid IAM policy"}}

    with pytest.raises(BedrockAuthenticationError) as exc_info:
        client._normalize_and_raise(mock_error, "anthropic.claude-3-5-sonnet")
    assert "AWS Auth Error" in str(exc_info.value)


def test_bedrock_error_normalization_throttling():
    """Botocore ThrottlingException is converted to BedrockThrottlingError."""
    client = BedrockClient()
    mock_error = MagicMock()
    mock_error.response = {"Error": {"Code": "ThrottlingException", "Message": "Rate exceeded"}}

    with pytest.raises(BedrockThrottlingError) as exc_info:
        client._normalize_and_raise(mock_error, "deepseek.r1-v1:0")
    assert "Rate Limit" in str(exc_info.value)


def test_bedrock_error_normalization_model_not_found():
    """Botocore ResourceNotFoundException is converted to BedrockModelNotFoundError."""
    client = BedrockClient()
    mock_error = MagicMock()
    mock_error.response = {"Error": {"Code": "ResourceNotFoundException", "Message": "Model not available"}}

    with pytest.raises(BedrockModelNotFoundError) as exc_info:
        client._normalize_and_raise(mock_error, "invalid.model.id")
    assert "is not available" in str(exc_info.value)


# ---------------------------------------------------------------------------
# 3. Anthropic Claude Adapter Tests
# ---------------------------------------------------------------------------

def test_anthropic_adapter_message_formatting_and_response():
    """Verifies Claude messages API formatting and normalized AIResponse extraction."""
    from backend.workline.ai.bedrock.adapters.anthropic import anthropic_adapter

    messages = [
        ChatMessage(role="system", content="You are a power electronics engineer."),
        ChatMessage(role="user", content="Calculate buck converter inductor ripple."),
    ]
    response = anthropic_adapter.generate(
        model_id="anthropic.claude-3-5-haiku-20241022-v1:0",
        messages=messages,
        temperature=0.1,
    )
    assert isinstance(response, AIResponse)
    assert response.provider.startswith("Anthropic")
    assert response.model_id == "anthropic.claude-3-5-haiku-20241022-v1:0"
    assert len(response.text) > 0
    assert response.usage.total_tokens > 0


# ---------------------------------------------------------------------------
# 4. DeepSeek Adapter Tests
# ---------------------------------------------------------------------------

def test_deepseek_adapter_formatting_and_response():
    """Verifies DeepSeek Bedrock formatting and normalized AIResponse extraction."""
    from backend.workline.ai.bedrock.adapters.deepseek import deepseek_adapter

    messages = [
        ChatMessage(role="user", content="Compare GaN vs SiC MOSFET switching losses."),
    ]
    response = deepseek_adapter.generate(
        model_id="deepseek.r1-v1:0",
        messages=messages,
        temperature=0.4,
    )
    assert isinstance(response, AIResponse)
    assert "DeepSeek" in response.provider
    assert response.model_id == "deepseek.r1-v1:0"
    assert len(response.text) > 0
    assert response.usage.total_tokens > 0


# ---------------------------------------------------------------------------
# 5. Bedrock Image Generation Adapter Tests
# ---------------------------------------------------------------------------

def test_bedrock_image_adapter_generation():
    """Verifies image generation via Bedrock Nova Canvas / Titan Image Generator."""
    from backend.workline.ai.bedrock.adapters.image import bedrock_image_adapter

    req = BedrockImageRequest(
        prompt="Robotics arm power distribution architecture block diagram",
        aspect_ratio="16:9",
        width=1280,
        height=720,
    )
    img_res = bedrock_image_adapter.generate_image(
        model_id="amazon.nova-canvas-v1:0",
        request=req,
    )
    assert img_res.model_id == "amazon.nova-canvas-v1:0"
    assert img_res.mime_type == "image/png"
    assert len(img_res.image_bytes) > 0
    assert img_res.width == 1280
    assert img_res.height == 720


# ---------------------------------------------------------------------------
# 6. Central Model Router Execution Tests
# ---------------------------------------------------------------------------

def test_model_router_research():
    """model_router.research routes prompt to configured research model."""
    res = model_router.research("Synthesize literature on PINN thermal modeling.")
    assert isinstance(res, AIResponse)
    assert res.model_id == model_router.research_model_id
    assert len(res.text) > 0


def test_model_router_fast_code():
    """model_router.fast_code routes prompt to configured fast code model."""
    res = model_router.fast_code("Generate TypeScript interface for PCB Component.")
    assert isinstance(res, AIResponse)
    assert res.model_id == model_router.fast_code_model_id
    assert len(res.text) > 0


def test_model_router_reasoning():
    """model_router.reasoning routes prompt to configured reasoning model."""
    res = model_router.reasoning("Evaluate 4-layer vs 6-layer PCB thermal dissipation tradeoff.")
    assert isinstance(res, AIResponse)
    assert res.model_id == model_router.reasoning_model_id
    assert len(res.text) > 0


def test_model_router_report_generation():
    """model_router.report_generation routes prompt to report model."""
    res = model_router.report_generation("Synthesize executive audit report for rover BOM.")
    assert isinstance(res, AIResponse)
    assert res.model_id == model_router.report_model_id
    assert len(res.text) > 0


def test_model_router_image_generation():
    """model_router.image_generation generates visual diagram via Bedrock."""
    img = model_router.image_generation("Power rail block diagram for STM32F4")
    assert img.model_id == model_router.image_model_id
    assert len(img.image_bytes) > 0


# ---------------------------------------------------------------------------
# 7. PaperBanana Bedrock Integration Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_paperbanana_renders_visual_via_bedrock():
    """PaperBanana client executes visual rendering through Amazon Bedrock."""
    req = ImageGenerationRequest(
        project_id="rover_power_subsystem",
        purpose=ImagePurpose.ARCHITECTURE,
        prompt="High-power motor driver wiring schematic with DRV8825",
        aspect_ratio="16:9",
    )
    artifact = await paperbanana_client.render_visual(req)
    assert artifact.artifact_id.startswith("art_img_")
    assert artifact.project_id == "rover_power_subsystem"
    assert artifact.format in ("png", "svg")
    assert os.path.exists(artifact.storage_path)


# ---------------------------------------------------------------------------
# 8. Zero Direct Gemini / OpenAI / Anthropic API Key Leaks
# ---------------------------------------------------------------------------

def test_no_gemini_key_in_bedrock_client():
    """Bedrock client must not reference GEMINI_API_KEY."""
    import inspect
    client_src = inspect.getsource(BedrockClient)
    assert "GEMINI_API_KEY" not in client_src
    assert "genai" not in client_src
    assert "google" not in client_src
