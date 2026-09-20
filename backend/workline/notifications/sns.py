"""
Amazon SNS Notification Publisher for Workline / ArmourFlow platform.
Delivers fan-out notifications for critical alerts:
- Critical validation failures
- Security policy violations (ArmorIQ)
- Team invitations
- Project milestone completions
"""

import json
import os
from typing import Any, Dict, List, Optional
from loguru import logger


class SNSNotificationService:
    """
    Amazon SNS client with topic routing and graceful local fallback.
    """

    def __init__(
        self,
        alerts_topic_arn: Optional[str] = None,
        region_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ):
        self.alerts_topic_arn = alerts_topic_arn or os.environ.get("SNS_ALERTS_TOPIC_ARN")
        self.region_name = region_name or os.environ.get("AWS_REGION", "us-east-1")
        self.endpoint_url = endpoint_url or os.environ.get("SNS_ENDPOINT_URL")
        self._client = None
        self._notifications_sent: List[Dict[str, Any]] = []
        self._init_client()

    def _init_client(self):
        try:
            import boto3
            kwargs: Dict[str, Any] = {"region_name": self.region_name}
            if self.endpoint_url:
                kwargs["endpoint_url"] = self.endpoint_url
            self._client = boto3.client("sns", **kwargs)
            logger.info("[SNS] Initialized SNS notification client.")
        except Exception as e:
            logger.warning(f"[SNS] Could not initialize SNS client ({e}); using local mock buffer.")
            self._client = None

    async def publish_alert(
        self,
        subject: str,
        message: Dict[str, Any],
        topic_arn: Optional[str] = None,
        message_attributes: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Publish an alert notification message to SNS."""
        target_arn = topic_arn or self.alerts_topic_arn
        record = {
            "subject": subject,
            "message": message,
            "topic_arn": target_arn,
        }
        self._notifications_sent.append(record)

        if not self._client or not target_arn:
            logger.info(f"[SNS Local] Alert '{subject}': {message}")
            return True

        try:
            msg_str = json.dumps(message) if isinstance(message, dict) else str(message)
            kwargs: Dict[str, Any] = {
                "TopicArn": target_arn,
                "Subject": subject[:100],
                "Message": msg_str,
            }
            if message_attributes:
                kwargs["MessageAttributes"] = message_attributes

            resp = self._client.publish(**kwargs)
            logger.info(f"[SNS] Published alert to {target_arn} (MessageId: {resp.get('MessageId')})")
            return True
        except Exception as e:
            logger.warning(f"[SNS] publish failed ({e})")
            return False

    def get_sent_notifications(self) -> List[Dict[str, Any]]:
        """Retrieve sent alerts from local buffer for testing."""
        return list(self._notifications_sent)


# Global singleton instance
sns_notifier = SNSNotificationService()
