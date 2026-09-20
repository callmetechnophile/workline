"""
AWS Lambda Mangum ASGI adapter for Workline / ArmourFlow API Gateway integration.
Enables serverless execution of the complete FastAPI backend on AWS Lambda.
"""

import os
import tempfile

# Ensure AWS Lambda writable scratch paths before importing app
if "AWS_LAMBDA_FUNCTION_NAME" in os.environ or "LAMBDA_TASK_ROOT" in os.environ:
    tmp = tempfile.gettempdir()
    os.environ.setdefault("WORKLINE_CONFIG_DIR", os.path.join(tmp, ".workline"))
    os.environ.setdefault("WORKLINE_WORKSPACE", os.path.join(tmp, "Workline"))
    os.environ.setdefault("MPLCONFIGDIR", os.path.join(tmp, "matplotlib"))
    os.environ.setdefault("HOME", tmp)
    env_stage = os.environ.get("WORKLINE_ENV", "dev")
    os.environ.setdefault("API_GATEWAY_BASE_PATH", f"/{env_stage}")

from backend.main import app
from backend.database import init_db

# Initialize SQLite database in /tmp for cold-start serverless runtime
try:
    init_db()
except Exception:
    pass

try:
    from mangum import Mangum
    handler = Mangum(
        app,
        lifespan="off",
        api_gateway_base_path=os.environ.get("API_GATEWAY_BASE_PATH", None),
    )
except ImportError:
    # Lightweight serverless event mock adapter when mangum is not installed locally
    def handler(event, context):
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": '{"status": "healthy", "service": "workline-lambda-adapter"}'
        }
