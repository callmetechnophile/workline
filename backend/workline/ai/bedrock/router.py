"""
Workline AI — Central Amazon Bedrock Model Router.

Single entry point for all Workline AI capabilities:
- research() -> DeepSeek V3/R1 or Claude Sonnet
- fast_code() -> Claude 3.5 Haiku
- reasoning() -> Claude 3.5 / 3.7 Sonnet
- report_generation() -> Claude 3.5 Sonnet
- image_generation() -> Amazon Nova Canvas / Titan Image Generator
"""

import os
from typing import Any, Dict, List, Optional, Union
from loguru import logger

from backend.workline.ai.bedrock.adapters.anthropic import anthropic_adapter
from backend.workline.ai.bedrock.adapters.deepseek import deepseek_adapter
from backend.workline.ai.bedrock.adapters.image import bedrock_image_adapter
from backend.workline.ai.bedrock.schemas import (
    AIResponse,
    BedrockImageRequest,
    BedrockImageResponse,
    ChatMessage,
)


class BedrockModelRouter:
    """
    Central router directing high-level agent tasks to the appropriate Bedrock models.
    """

    def __init__(self):
        # Configuration-driven model IDs with sensible defaults
        self.research_model_id = os.getenv(
            "BEDROCK_RESEARCH_MODEL_ID",
            "deepseek.r1-v1:0"
        )
        self.fast_code_model_id = os.getenv(
            "BEDROCK_FAST_CODE_MODEL_ID",
            "anthropic.claude-3-5-haiku-20241022-v1:0"
        )
        self.reasoning_model_id = os.getenv(
            "BEDROCK_REASONING_MODEL_ID",
            "anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        self.report_model_id = os.getenv(
            "BEDROCK_REPORT_MODEL_ID",
            "anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        self.image_model_id = os.getenv(
            "BEDROCK_IMAGE_MODEL_ID",
            "amazon.nova-canvas-v1:0"
        )

    def _normalize_messages(self, prompt_or_messages: Union[str, List[ChatMessage], List[Dict[str, str]]]) -> List[ChatMessage]:
        """Converts raw strings or dicts into standard ChatMessage lists."""
        if isinstance(prompt_or_messages, str):
            return [ChatMessage(role="user", content=prompt_or_messages)]
        if isinstance(prompt_or_messages, list):
            res = []
            for item in prompt_or_messages:
                if isinstance(item, ChatMessage):
                    res.append(item)
                elif isinstance(item, dict):
                    res.append(ChatMessage(role=item.get("role", "user"), content=item.get("content", "")))
            return res
        return [ChatMessage(role="user", content=str(prompt_or_messages))]

    def _dispatch_text_model(
        self,
        model_id: str,
        messages: List[ChatMessage],
        system_instruction: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> AIResponse:
        """Dispatches to the appropriate adapter based on model ID."""
        if "deepseek" in model_id.lower():
            return deepseek_adapter.generate(
                model_id=model_id,
                messages=messages,
                system_instruction=system_instruction,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        # Default to Claude / Anthropic adapter
        return anthropic_adapter.generate(
            model_id=model_id,
            messages=messages,
            system_instruction=system_instruction,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def research(
        self,
        prompt: Union[str, List[ChatMessage], List[Dict[str, str]]],
        system_instruction: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.4,
    ) -> AIResponse:
        """Academic literature synthesis, contradiction analysis, and deep engineering research."""
        msgs = self._normalize_messages(prompt)
        logger.info(f"[ModelRouter] Routing research task to model '{self.research_model_id}'")
        return self._dispatch_text_model(
            model_id=self.research_model_id,
            messages=msgs,
            system_instruction=system_instruction,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def fast_code(
        self,
        prompt: Union[str, List[ChatMessage], List[Dict[str, str]]],
        system_instruction: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> AIResponse:
        """Fast coding, syntax validation, unit testing, and lightweight code transformations."""
        msgs = self._normalize_messages(prompt)
        logger.info(f"[ModelRouter] Routing fast code task to model '{self.fast_code_model_id}'")
        return self._dispatch_text_model(
            model_id=self.fast_code_model_id,
            messages=msgs,
            system_instruction=system_instruction,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def reasoning(
        self,
        prompt: Union[str, List[ChatMessage], List[Dict[str, str]]],
        system_instruction: Optional[str] = None,
        max_tokens: int = 8192,
        temperature: float = 0.2,
    ) -> AIResponse:
        """Multi-physics reasoning, topological tradeoff balancing, and system architecture."""
        msgs = self._normalize_messages(prompt)
        logger.info(f"[ModelRouter] Routing complex reasoning task to model '{self.reasoning_model_id}'")
        return self._dispatch_text_model(
            model_id=self.reasoning_model_id,
            messages=msgs,
            system_instruction=system_instruction,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def report_generation(
        self,
        prompt: Union[str, List[ChatMessage], List[Dict[str, str]]],
        system_instruction: Optional[str] = None,
        max_tokens: int = 8192,
        temperature: float = 0.2,
    ) -> AIResponse:
        """PDF report synthesis, executive summaries, and formal engineering verification logs."""
        msgs = self._normalize_messages(prompt)
        logger.info(f"[ModelRouter] Routing report generation task to model '{self.report_model_id}'")
        return self._dispatch_text_model(
            model_id=self.report_model_id,
            messages=msgs,
            system_instruction=system_instruction,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def image_generation(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "16:9",
        width: int = 1280,
        height: int = 720,
    ) -> BedrockImageResponse:
        """Generates engineering diagrams and visual architecture charts via Bedrock."""
        req = BedrockImageRequest(
            prompt=prompt,
            negative_prompt=negative_prompt,
            aspect_ratio=aspect_ratio,
            width=width,
            height=height,
        )
        logger.info(f"[ModelRouter] Routing visual generation task to model '{self.image_model_id}'")
        return bedrock_image_adapter.generate_image(
            model_id=self.image_model_id,
            request=req,
        )


# Global singleton instance
model_router = BedrockModelRouter()
