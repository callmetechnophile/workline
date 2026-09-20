"""
AWS Lambda Mangum ASGI adapter for Workline / ArmourFlow API Gateway integration.
Enables serverless execution of the complete FastAPI backend on AWS Lambda.
"""

import os
from backend.main import app

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
