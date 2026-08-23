"""
Workline AI — Central Amazon Bedrock Runtime Client.

Manages:
1. AWS credentials & IAM role authentication (backend-only, zero frontend exposure).
2. Botocore connection & read timeouts.
3. Exponential backoff retry logic for transient AWS failures and throttling.
4. Latency timing and error normalization.
"""

import json
import os
import time
import random
from typing import Any, Dict, Optional
from loguru import logger

try:
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError, ConnectTimeoutError, ReadTimeoutError
    _BOTO3_AVAILABLE = True
except ImportError:
    boto3 = None  # type: ignore
    Config = None  # type: ignore
    ClientError = Exception  # type: ignore
    ConnectTimeoutError = Exception  # type: ignore
    ReadTimeoutError = Exception  # type: ignore
    _BOTO3_AVAILABLE = False

from backend.workline.ai.bedrock.errors import (
    BedrockAuthenticationError,
    BedrockContentFilterError,
    BedrockError,
    BedrockModelNotFoundError,
    BedrockThrottlingError,
    BedrockTimeoutError,
    BedrockValidationError,
)


class BedrockClient:
    """
    Centralized, thread-safe Amazon Bedrock Runtime client.
    """

    def __init__(
        self,
        region_name: Optional[str] = None,
        connect_timeout: float = 10.0,
        read_timeout: float = 60.0,
        max_retries: int = 3,
    ):
        self.region = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.max_retries = max_retries
        self._client = None

    def _get_client(self):
        """Initializes the boto3 bedrock-runtime client with robust timeouts."""
        if self._client is not None:
            return self._client

        if not _BOTO3_AVAILABLE:
            logger.warning("[Bedrock] boto3 is not installed; operating in simulation mode.")
            return None

        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_session_token = os.getenv("AWS_SESSION_TOKEN")

        config = Config(
            region_name=self.region,
            connect_timeout=self.connect_timeout,
            read_timeout=self.read_timeout,
            retries={"max_attempts": 1},  # We handle custom backoff retries explicitly
        )

        kwargs: Dict[str, Any] = {"config": config}
        if aws_access_key and aws_secret_key:
            kwargs["aws_access_key_id"] = aws_access_key
            kwargs["aws_secret_access_key"] = aws_secret_key
            if aws_session_token:
                kwargs["aws_session_token"] = aws_session_token

        try:
            self._client = boto3.client("bedrock-runtime", **kwargs)
            logger.info(f"[Bedrock] Initialized Bedrock Runtime client in region '{self.region}'.")
            return self._client
        except Exception as e:
            logger.error(f"[Bedrock] Failed to initialize Bedrock client: {e}")
            raise BedrockAuthenticationError(f"Failed to initialize AWS Bedrock client: {str(e)}")

    def invoke_model(
        self,
        model_id: str,
        body: Dict[str, Any],
        accept: str = "application/json",
        content_type: str = "application/json",
    ) -> Dict[str, Any]:
        """
        Invokes a Bedrock model with automatic exponential backoff retries.
        Returns: (parsed_response_dict, latency_ms)
        """
        client = self._get_client()
        encoded_body = json.dumps(body).encode("utf-8") if isinstance(body, dict) else body

        # If offline or in testing without active AWS keys, return deterministic simulation
        has_aws_keys = bool(
            os.getenv("AWS_ACCESS_KEY_ID")
            or os.getenv("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI")
            or os.getenv("AWS_ROLE_ARN")
            or os.getenv("AWS_PROFILE")
        )
        if client is None or not has_aws_keys:
            return self._simulate_invocation(model_id, body)

        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            start_time = time.perf_counter()
            try:
                response = client.invoke_model(
                    modelId=model_id,
                    body=encoded_body,
                    accept=accept,
                    contentType=content_type,
                )
                latency_ms = (time.perf_counter() - start_time) * 1000.0

                raw_body = response.get("body").read()
                parsed = json.loads(raw_body.decode("utf-8")) if accept == "application/json" else raw_body
                return {
                    "data": parsed,
                    "latency_ms": latency_ms,
                    "request_id": response.get("ResponseMetadata", {}).get("RequestId", ""),
                }

            except (ClientError, ConnectTimeoutError, ReadTimeoutError) as exc:
                last_error = exc
                is_transient = self._is_transient_error(exc)
                logger.warning(
                    f"[Bedrock] Attempt {attempt}/{self.max_retries} failed for model '{model_id}': {exc}"
                )
                if attempt < self.max_retries and is_transient:
                    backoff = (2 ** (attempt - 1)) + random.uniform(0.1, 0.5)
                    time.sleep(backoff)
                else:
                    self._normalize_and_raise(exc, model_id)

            except Exception as exc:
                if "NoCredentialsError" in type(exc).__name__ or "credentials" in str(exc).lower():
                    return self._simulate_invocation(model_id, body)
                self._normalize_and_raise(exc, model_id)

        self._normalize_and_raise(last_error, model_id)

    def _is_transient_error(self, exc: Exception) -> bool:
        """Determines if the exception is temporary / retryable."""
        if isinstance(exc, (ConnectTimeoutError, ReadTimeoutError)):
            return True
        if hasattr(exc, "response"):
            code = exc.response.get("Error", {}).get("Code", "")
            return code in (
                "ThrottlingException",
                "ModelTimeoutException",
                "ServiceUnavailableException",
                "InternalServerException",
                "ResourceInUseException",
            )
        return False

    def _normalize_and_raise(self, exc: Any, model_id: str) -> None:
        """Converts AWS Botocore ClientErrors into clean Workline domain exceptions."""
        if exc is None:
            raise BedrockError("Unknown Bedrock invocation error.", model_id=model_id)

        if isinstance(exc, (ConnectTimeoutError, ReadTimeoutError)):
            raise BedrockTimeoutError(f"Bedrock invocation timed out for '{model_id}'.", model_id=model_id)

        if hasattr(exc, "response"):
            error_dict = exc.response.get("Error", {})
            code = error_dict.get("Code", "")
            msg = error_dict.get("Message", str(exc))

            if code in ("UnrecognizedClientException", "AccessDeniedException", "InvalidSignatureException"):
                raise BedrockAuthenticationError(f"AWS Auth Error: {msg}", model_id=model_id)
            if code in ("ResourceNotFoundException", "ModelNotReadyException"):
                raise BedrockModelNotFoundError(model_id=model_id, region=self.region)
            if code in ("ThrottlingException", "TooManyRequestsException"):
                raise BedrockThrottlingError(f"AWS Bedrock Rate Limit: {msg}", model_id=model_id)
            if code in ("ValidationException",):
                raise BedrockValidationError(f"AWS Bedrock Validation: {msg}", model_id=model_id)
            if "guardrail" in msg.lower() or "safety" in msg.lower():
                raise BedrockContentFilterError(f"Content filtered: {msg}", model_id=model_id)

        raise BedrockError(f"Bedrock execution error: {str(exc)}", model_id=model_id)

    def _simulate_invocation(self, model_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """Offline development / testing deterministic response simulator."""
        time.sleep(0.05)
        # Claude Messages simulation
        if "claude" in model_id.lower():
            messages = body.get("messages", [])
            last_prompt = messages[-1].get("content", "") if messages else "Simulation output"
            return {
                "data": {
                    "id": f"msg_sim_{random.randint(1000, 9999)}",
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "text", "text": f"[Bedrock {model_id}] Analysis: {last_prompt[:120]} (Synthesized)"}],
                    "model": model_id,
                    "stop_reason": "end_turn",
                    "usage": {"input_tokens": len(str(body)) // 4, "output_tokens": 85},
                },
                "latency_ms": 50.0,
                "request_id": f"req_sim_{random.randint(10000, 99999)}",
            }
        # DeepSeek simulation
        if "deepseek" in model_id.lower():
            prompt = body.get("prompt", "") or str(body.get("messages", ""))
            return {
                "data": {
                    "id": f"deepseek_sim_{random.randint(1000, 9999)}",
                    "choices": [{"message": {"content": f"[Bedrock DeepSeek] Sourced reasoning: {prompt[:120]}"}, "finish_reason": "stop"}],
                    "usage": {"prompt_tokens": len(prompt) // 4, "completion_tokens": 90, "total_tokens": 120},
                },
                "latency_ms": 60.0,
                "request_id": f"req_sim_{random.randint(10000, 99999)}",
            }
        # Image model simulation (Titan / Nova Canvas)
        return {
            "data": {
                "images": ["iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="],
            },
            "latency_ms": 80.0,
            "request_id": f"req_sim_img_{random.randint(10000, 99999)}",
        }


# Global singleton instance
bedrock_client = BedrockClient()
