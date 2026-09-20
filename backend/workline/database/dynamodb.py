"""
Amazon DynamoDB Metadata Adapter for Workline / ArmourFlow platform.
Stores AWS-native application metadata:
- Job Execution states
- API Idempotency locks
- User Preferences & Session states
- Workflow Execution metadata
"""

import os
import time
from typing import Any, Dict, List, Optional
from loguru import logger


class DynamoDBMetadataStore:
    """
    AWS DynamoDB metadata client with automatic local in-memory fallback.
    Table Key Schema:
      - PK (String): Partition key (e.g., 'JOB#<job_id>', 'USER#<user_id>', 'IDEMPOTENCY#<key>')
      - SK (String): Sort key (e.g., 'METADATA', 'PREFERENCES', 'STATE#<timestamp>')
    """

    def __init__(
        self,
        table_name: Optional[str] = None,
        region_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ):
        self.table_name = table_name or os.environ.get("DYNAMODB_TABLE_NAME", "workline_metadata")
        self.region_name = region_name or os.environ.get("AWS_REGION", "us-east-1")
        self.endpoint_url = endpoint_url or os.environ.get("DYNAMODB_ENDPOINT_URL")  # For LocalStack
        self._client = None
        self._resource = None
        self._table = None
        self._local_cache: Dict[str, Dict[str, Any]] = {}
        self._init_client()

    def _init_client(self):
        try:
            import boto3
            kwargs: Dict[str, Any] = {"region_name": self.region_name}
            if self.endpoint_url:
                kwargs["endpoint_url"] = self.endpoint_url

            self._resource = boto3.resource("dynamodb", **kwargs)
            self._table = self._resource.Table(self.table_name)
            self._client = boto3.client("dynamodb", **kwargs)
            logger.info(f"[DynamoDB] Initialized client for table '{self.table_name}'")
        except Exception as e:
            logger.warning(f"[DynamoDB] Could not initialize DynamoDB client ({e}); using local memory store.")
            self._table = None

    async def put_item(self, pk: str, sk: str, data: Dict[str, Any], ttl_seconds: Optional[int] = None) -> bool:
        """Put item into DynamoDB with optional TTL expiration."""
        item = {
            "PK": pk,
            "SK": sk,
            "updated_at": int(time.time()),
            **data,
        }
        if ttl_seconds:
            item["ttl"] = int(time.time()) + ttl_seconds

        composite_key = f"{pk}##{sk}"
        self._local_cache[composite_key] = item

        if not self._table:
            return True

        try:
            self._table.put_item(Item=item)
            return True
        except Exception as e:
            logger.warning(f"[DynamoDB] put_item failed for {composite_key} ({e}); using local memory cache.")
            return True

    async def get_item(self, pk: str, sk: str) -> Optional[Dict[str, Any]]:
        """Retrieve item by primary key and sort key."""
        composite_key = f"{pk}##{sk}"
        if not self._table:
            return self._local_cache.get(composite_key)

        try:
            resp = self._table.get_item(Key={"PK": pk, "SK": sk})
            return resp.get("Item") or self._local_cache.get(composite_key)
        except Exception as e:
            logger.warning(f"[DynamoDB] get_item failed for {composite_key} ({e}); using local memory cache.")
            return self._local_cache.get(composite_key)

    async def acquire_idempotency_lock(self, idempotency_key: str, ttl_seconds: int = 300) -> bool:
        """
        Conditional write ensuring idempotency lock.
        Returns True if acquired, False if already exists.
        """
        pk = f"IDEMPOTENCY#{idempotency_key}"
        sk = "LOCK"
        composite_key = f"{pk}##{sk}"

        if not self._table:
            if composite_key in self._local_cache:
                existing = self._local_cache[composite_key]
                if existing.get("ttl", 0) > time.time():
                    return False
            self._local_cache[composite_key] = {"PK": pk, "SK": sk, "ttl": int(time.time()) + ttl_seconds}
            return True

        try:
            now = int(time.time())
            self._table.put_item(
                Item={"PK": pk, "SK": sk, "ttl": now + ttl_seconds, "locked_at": now},
                ConditionExpression="attribute_not_exists(PK) OR #ttl < :now",
                ExpressionAttributeNames={"#ttl": "ttl"},
                ExpressionAttributeValues={":now": now},
            )
            return True
        except Exception as e:
            # Check if condition failed (already locked)
            err_str = str(e)
            if "ConditionalCheckFailedException" in err_str:
                return False
            # If network or credentials error, fall back to memory lock
            if composite_key in self._local_cache:
                existing = self._local_cache[composite_key]
                if existing.get("ttl", 0) > time.time():
                    return False
            self._local_cache[composite_key] = {"PK": pk, "SK": sk, "ttl": int(time.time()) + ttl_seconds}
            return True

    async def delete_item(self, pk: str, sk: str) -> bool:
        """Delete an item from DynamoDB."""
        composite_key = f"{pk}##{sk}"
        self._local_cache.pop(composite_key, None)
        if not self._table:
            return True
        try:
            self._table.delete_item(Key={"PK": pk, "SK": sk})
            return True
        except Exception as e:
            logger.warning(f"[DynamoDB] delete_item failed for {composite_key}: {e}")
            return False


# Global singleton instance
dynamodb_store = DynamoDBMetadataStore()
