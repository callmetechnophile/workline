"""
Workline AI — Amazon Bedrock Normalized Error Taxonomy.
"""

class BedrockError(Exception):
    """Base exception for Bedrock operations."""
    def __init__(self, message: str, model_id: str = "", status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.model_id = model_id
        self.status_code = status_code


class BedrockAuthenticationError(BedrockError):
    """Raised when AWS credentials or IAM permissions fail."""
    def __init__(self, message: str = "AWS authentication failed. Check credentials or IAM role.", model_id: str = ""):
        super().__init__(message, model_id=model_id, status_code=401)


class BedrockModelNotFoundError(BedrockError):
    """Raised when the requested model ID is not available in the region."""
    def __init__(self, model_id: str, region: str = ""):
        super().__init__(f"Bedrock model '{model_id}' is not available or enabled in region '{region}'.", model_id=model_id, status_code=404)


class BedrockThrottlingError(BedrockError):
    """Raised when Bedrock rate limits or concurrency limits are exceeded."""
    def __init__(self, message: str = "Bedrock rate limit / throttling exceeded.", model_id: str = ""):
        super().__init__(message, model_id=model_id, status_code=429)


class BedrockTimeoutError(BedrockError):
    """Raised when model invocation exceeds the configured timeout."""
    def __init__(self, message: str = "Bedrock model invocation timed out.", model_id: str = ""):
        super().__init__(message, model_id=model_id, status_code=504)


class BedrockValidationError(BedrockError):
    """Raised when request payload fails validation."""
    def __init__(self, message: str, model_id: str = ""):
        super().__init__(message, model_id=model_id, status_code=400)


class BedrockContentFilterError(BedrockError):
    """Raised when prompt or response violates automated guardrails."""
    def __init__(self, message: str = "Content violated automated safety guardrails.", model_id: str = ""):
        super().__init__(message, model_id=model_id, status_code=400)
