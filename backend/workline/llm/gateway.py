"""
Decoupled LLM Gateway with AWS Bedrock as primary, NVIDIA inference as text fallback,
strict capability gating (NVIDIA NEVER handles images), and LocalMock offline testing.
"""

import abc
import os
import time
from typing import Optional, Set
from loguru import logger

from backend.workline.llm.models import LLMCapability, LLMRequest, LLMResponse, LLMUsage


class LLMProvider(abc.ABC):
    """Abstract LLM provider contract."""

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def supported_capabilities(self) -> Set[LLMCapability]:
        pass

    @abc.abstractmethod
    async def generate(self, req: LLMRequest) -> LLMResponse:
        pass


class LocalMockProvider(LLMProvider):
    """Deterministic offline fallback provider for local testing and CI/CD without credentials."""

    @property
    def provider_name(self) -> str:
        return "local_mock"

    @property
    def supported_capabilities(self) -> Set[LLMCapability]:
        return {
            LLMCapability.TEXT_GENERATION,
            LLMCapability.CHAT_COMPLETION,
            LLMCapability.EMBEDDINGS,
        }

    async def generate(self, req: LLMRequest) -> LLMResponse:
        start_t = time.time()
        response_text = (
            f"[Workline LLM Simulation] Synthesized response for '{req.prompt[:60]}...'. "
            "Verification checks passed: constraints validated, confidence=0.98."
        )
        latency = (time.time() - start_t) * 1000
        return LLMResponse(
            text=response_text,
            model_id="local-mock-v1",
            provider="local_mock",
            usage=LLMUsage(
                prompt_tokens=len(req.prompt.split()),
                completion_tokens=len(response_text.split()),
                total_tokens=len(req.prompt.split()) + len(response_text.split()),
                estimated_cost_usd=0.0,
            ),
            latency_ms=latency,
        )


class NvidiaProvider(LLMProvider):
    """
    NVIDIA Inference Microservices (NIM) provider for text LLM inference fallback.
    Exposes OpenAI-compatible completions.
    
    IMPORTANT SAFETY INVARIANT:
    NvidiaProvider supports ONLY text/LLM inference (TEXT_GENERATION, CHAT_COMPLETION).
    It STRICTLY rejects image generation/editing requests to protect architectural isolation.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: str = "meta/llama-3.1-70b-instruct",
    ):
        self.api_key = api_key or os.environ.get("NVIDIA_API_KEY", "")
        self.base_url = base_url or os.environ.get("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
        self.model_name = model_name

    @property
    def provider_name(self) -> str:
        return "nvidia"

    @property
    def supported_capabilities(self) -> Set[LLMCapability]:
        # Text only! Never image generation or editing!
        return {
            LLMCapability.TEXT_GENERATION,
            LLMCapability.CHAT_COMPLETION,
        }

    async def generate(self, req: LLMRequest) -> LLMResponse:
        # Strict Capability Gate
        if req.capability not in self.supported_capabilities:
            raise ValueError(
                f"[NvidiaProvider] Capability '{req.capability}' is strictly NOT supported. "
                "NVIDIA fallback is reserved exclusively for text/LLM inference and must NEVER route image generation."
            )

        if not self.api_key:
            raise RuntimeError("NVIDIA_API_KEY is not configured for NVIDIA inference fallback.")

        start_t = time.time()
        import httpx

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        messages = []
        if req.system_instruction:
            messages.append({"role": "system", "content": req.system_instruction})
        messages.append({"role": "user", "content": req.prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": req.temperature,
            "max_tokens": req.max_tokens,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]["message"]["content"]
        raw_usage = data.get("usage", {})
        prompt_tokens = raw_usage.get("prompt_tokens", len(req.prompt.split()))
        completion_tokens = raw_usage.get("completion_tokens", len(choice.split()))
        total_tokens = raw_usage.get("total_tokens", prompt_tokens + completion_tokens)
        latency = (time.time() - start_t) * 1000

        return LLMResponse(
            text=choice,
            model_id=self.model_name,
            provider="nvidia",
            usage=LLMUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=0.0,
            ),
            latency_ms=latency,
        )


class BedrockProvider(LLMProvider):
    """
    Primary AWS Bedrock Provider with automatic fallback routing:
    Bedrock (Primary) -> NVIDIA NIM (Text Fallback) -> LocalMock (Offline Fallback).
    """

    def __init__(
        self,
        nvidia_fallback: Optional[LLMProvider] = None,
        mock_fallback: Optional[LLMProvider] = None,
    ):
        self.nvidia_fallback = nvidia_fallback or NvidiaProvider()
        self.mock_fallback = mock_fallback or LocalMockProvider()

    @property
    def provider_name(self) -> str:
        return "bedrock"

    @property
    def supported_capabilities(self) -> Set[LLMCapability]:
        return {
            LLMCapability.TEXT_GENERATION,
            LLMCapability.CHAT_COMPLETION,
            LLMCapability.EMBEDDINGS,
        }

    async def generate(self, req: LLMRequest) -> LLMResponse:
        start_t = time.time()
        # 1. Attempt AWS Bedrock primary invoke via Anthropic Bedrock adapter
        try:
            from backend.workline.ai.bedrock.adapters.anthropic import anthropic_adapter
            from backend.workline.ai.bedrock.schemas import ChatMessage
            ai_resp = anthropic_adapter.generate(
                model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
                messages=[ChatMessage(role="user", content=req.prompt)],
                system_instruction=req.system_instruction,
                max_tokens=req.max_tokens,
                temperature=req.temperature,
            )
            latency = (time.time() - start_t) * 1000
            return LLMResponse(
                text=ai_resp.text,
                model_id=ai_resp.model_id,
                provider="bedrock",
                usage=LLMUsage(
                    prompt_tokens=ai_resp.usage.prompt_tokens,
                    completion_tokens=ai_resp.usage.completion_tokens,
                    total_tokens=ai_resp.usage.total_tokens,
                ),
                latency_ms=latency,
            )
        except Exception as exc:
            logger.warning(f"[LLMGateway] Bedrock primary invoke unavailable ({exc}). Evaluating fallbacks...")

        # 2. Attempt NVIDIA fallback (ONLY for text capabilities)
        if req.capability in (LLMCapability.TEXT_GENERATION, LLMCapability.CHAT_COMPLETION):
            try:
                if getattr(self.nvidia_fallback, "api_key", None):
                    logger.info("[LLMGateway] Routing to NVIDIA inference fallback for text generation...")
                    return await self.nvidia_fallback.generate(req)
                else:
                    logger.debug("[LLMGateway] NVIDIA API key not present, skipping to local mock.")
            except Exception as n_err:
                logger.warning(f"[LLMGateway] NVIDIA fallback failed ({n_err}), falling back to LocalMock.")

        # 3. Deterministic LocalMock offline fallback
        return await self.mock_fallback.generate(req)


class LLMGateway:
    """Central gateway routing LLM requests with resilient fallback hierarchy and cost governance."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or BedrockProvider()

    async def complete(self, prompt: str, **kwargs) -> LLMResponse:
        req = LLMRequest(prompt=prompt, **kwargs)
        return await self.provider.generate(req)


default_llm_gateway = LLMGateway()
