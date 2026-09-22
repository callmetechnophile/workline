import os
import pytest

@pytest.fixture
def anyio_backend():
    """Configure AnyIO to use asyncio backend for tests."""
    return "asyncio"

@pytest.fixture(autouse=True)
def isolate_test_bedrock_client(monkeypatch):
    """
    Ensure Bedrock client runs safely in simulation mode during automated test suites
    without attempting external unauthenticated AWS network calls.
    """
    current = os.environ.get("PYTEST_CURRENT_TEST", "")
    if "test_live_aws" not in current:
        monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
        monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)
        monkeypatch.delenv("AWS_SESSION_TOKEN", raising=False)
        monkeypatch.delenv("AWS_PROFILE", raising=False)
        try:
            from backend.workline.ai.bedrock.client import bedrock_client
            bedrock_client._client = None
        except ImportError:
            pass
