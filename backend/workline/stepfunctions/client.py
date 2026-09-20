"""
AWS Step Functions client dispatcher for Workline / ArmourFlow multi-agent workflows.
"""

import json
import os
import uuid
from typing import Any, Dict, Optional
from loguru import logger


class StepFunctionsWorkflowDispatcher:
    """
    Triggers and inspects AWS Step Functions executions.
    Falls back to synchronous/asynchronous local execution if Step Functions is unconfigured.
    """

    def __init__(
        self,
        state_machine_arn: Optional[str] = None,
        region_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ):
        self.state_machine_arn = state_machine_arn or os.environ.get("STEP_FUNCTIONS_WORKFLOW_ARN")
        self.region_name = region_name or os.environ.get("AWS_REGION", "us-east-1")
        self.endpoint_url = endpoint_url or os.environ.get("STEPFUNCTIONS_ENDPOINT_URL")
        self._client = None
        self._local_executions: Dict[str, Dict[str, Any]] = {}
        self._init_client()

    def _init_client(self):
        try:
            import boto3
            kwargs: Dict[str, Any] = {"region_name": self.region_name}
            if self.endpoint_url:
                kwargs["endpoint_url"] = self.endpoint_url
            self._client = boto3.client("stepfunctions", **kwargs)
            logger.info("[StepFunctions] Initialized Step Functions client.")
        except Exception as e:
            logger.warning(f"[StepFunctions] Could not initialize client ({e}); using local mock dispatcher.")
            self._client = None

    async def start_workflow(
        self,
        project_id: str,
        user_intent: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Start a new multi-agent execution run."""
        execution_id = f"exec-{uuid.uuid4().hex[:12]}"
        payload = {
            "project_id": project_id,
            "user_intent": user_intent,
            "context": context or {},
        }

        if not self._client or not self.state_machine_arn:
            logger.info(f"[StepFunctions Local] Simulated workflow execution started for {project_id}")
            record = {
                "executionArn": f"arn:aws:states:{self.region_name}:123456789012:execution:WorklineWorkflow:{execution_id}",
                "status": "RUNNING",
                "project_id": project_id,
                "input": payload,
            }
            self._local_executions[record["executionArn"]] = record
            return record

        try:
            resp = self._client.start_execution(
                stateMachineArn=self.state_machine_arn,
                name=f"{project_id}-{execution_id}",
                input=json.dumps(payload),
            )
            return {
                "executionArn": resp.get("executionArn"),
                "startDate": str(resp.get("startDate")),
                "status": "RUNNING",
            }
        except Exception as e:
            logger.warning(f"[StepFunctions] start_execution failed ({e})")
            return {"error": str(e), "status": "FAILED"}

    async def get_execution_status(self, execution_arn: str) -> Dict[str, Any]:
        """Get the current state and result of a Step Functions execution."""
        if execution_arn in self._local_executions:
            return self._local_executions[execution_arn]

        if not self._client:
            return {"status": "UNKNOWN", "executionArn": execution_arn}

        try:
            resp = self._client.describe_execution(executionArn=execution_arn)
            output_data = None
            if resp.get("output"):
                try:
                    output_data = json.loads(resp["output"])
                except Exception:
                    output_data = resp["output"]

            return {
                "executionArn": resp.get("executionArn"),
                "status": resp.get("status"),
                "startDate": str(resp.get("startDate")),
                "stopDate": str(resp.get("stopDate")) if resp.get("stopDate") else None,
                "output": output_data,
            }
        except Exception as e:
            return {"error": str(e), "status": "UNKNOWN"}


# Global singleton instance
step_functions_dispatcher = StepFunctionsWorkflowDispatcher()
