"""
Amazon Bedrock reasoning provider adapter for DeepResearchAgent.
Uses boto3 bedrock-runtime Converse API with structured error translation and no hardcoded credentials.
"""

import asyncio
import json
import re
from typing import Any, Dict, Optional, Type, TypeVar
import boto3
from botocore.exceptions import ClientError, ConnectTimeoutError, NoCredentialsError, ReadTimeoutError
from loguru import logger
from pydantic import BaseModel

from research_agents.deep_research_agent.config import deep_research_config
from research_agents.deep_research_agent.providers.base import (
    ModelUnavailableError,
    ProviderAuthenticationError,
    ProviderError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ReasoningProvider,
)

T = TypeVar("T", bound=BaseModel)


class BedrockProvider(ReasoningProvider):
    """Amazon Bedrock reasoning client using boto3 and the Converse API."""

    def __init__(
        self,
        model_id: Optional[str] = None,
        region: Optional[str] = None,
        bedrock_client: Optional[Any] = None,
    ):
        self.model_id = model_id or deep_research_config.bedrock_model_id
        self.region = region or deep_research_config.bedrock_region
        self._client = bedrock_client

    def _get_client(self):
        if self._client is None:
            try:
                self._client = boto3.client("bedrock-runtime", region_name=self.region)
            except NoCredentialsError as nce:
                raise ProviderAuthenticationError(
                    provider="bedrock",
                    message="AWS credentials not found in environment or AWS configuration.",
                )
            except Exception as e:
                raise ProviderError(
                    provider="bedrock",
                    message=f"Failed to initialize Bedrock client: {str(e)}",
                )
        return self._client

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Invokes Bedrock model via Converse API and returns raw text response."""
        client = self._get_client()
        messages = [{"role": "user", "content": [{"text": prompt}]}]
        sys_prompts = [{"text": system_prompt}] if system_prompt else []

        inference_config = {
            "maxTokens": max_tokens or deep_research_config.max_tokens,
            "temperature": temperature if temperature is not None else deep_research_config.temperature,
        }

        loop = asyncio.get_event_loop()

        def _call_bedrock():
            try:
                response = client.converse(
                    modelId=self.model_id,
                    messages=messages,
                    system=sys_prompts,
                    inferenceConfig=inference_config,
                )
                output_message = response.get("output", {}).get("message", {})
                content_blocks = output_message.get("content", [])
                text_response = "".join(b.get("text", "") for b in content_blocks)
                return text_response
            except ClientError as ce:
                code = ce.response.get("Error", {}).get("Code", "")
                msg = ce.response.get("Error", {}).get("Message", str(ce))
                if code in ("AccessDeniedException", "UnrecognizedClientException", "AuthFailure"):
                    raise ProviderAuthenticationError("bedrock", msg)
                elif code in ("ThrottlingException", "RequestLimitExceeded", "TooManyRequestsException"):
                    raise ProviderRateLimitError("bedrock", msg)
                elif code in ("ResourceNotFoundException", "ValidationException"):
                    raise ModelUnavailableError("bedrock", msg)
                raise ProviderError("bedrock", msg, code=code)
            except (ConnectTimeoutError, ReadTimeoutError) as te:
                raise ProviderTimeoutError("bedrock", f"Bedrock invocation timed out: {str(te)}")
            except NoCredentialsError:
                raise ProviderAuthenticationError("bedrock", "Missing AWS credentials for Amazon Bedrock.")

        return await loop.run_in_executor(None, _call_bedrock)

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        """Prompts Bedrock to produce JSON conforming to schema and validates with Pydantic."""
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        enhanced_prompt = (
            f"{prompt}\n\n"
            f"CRITICAL: Output ONLY a valid JSON object matching this schema, wrapped in ```json ... ```:\n"
            f"{schema_json}"
        )

        response_text = await self.generate(
            prompt=enhanced_prompt,
            system_prompt=system_prompt,
        )

        # Extract JSON from code fences or raw text
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response_text)
        json_str = json_match.group(1).strip() if json_match else response_text.strip()

        try:
            parsed_dict = json.loads(json_str)
            return schema.model_validate(parsed_dict)
        except Exception as parse_err:
            logger.error(f"[BedrockProvider] Failed to parse structured JSON: {parse_err}. Raw text:\n{response_text[:300]}")
            raise ProviderError(
                provider="bedrock",
                message=f"Model output could not be parsed into {schema.__name__}: {str(parse_err)}",
                code="STRUCTURED_OUTPUT_PARSE_ERROR",
            )
