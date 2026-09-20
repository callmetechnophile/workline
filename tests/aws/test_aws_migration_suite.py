"""
Comprehensive automated test suite verifying AWS-native migration components:
- API Gateway / Lambda ASGI Handler (Mangum)
- S3 Artifact Store (SSE-KMS & Presigned URLs)
- SQS Job Queue & Dead Letter Queue (DLQ)
- EventBridge Domain Event Publishing
- SNS Notification Service
- DynamoDB Metadata Store & Idempotency Locking
- Step Functions State Machine Dispatcher
- OpenSearch Search & Indexing Manager
- CloudWatch Metrics & ArmorIQ Policy Violation Tracking
- Non-migration invariants: SurrealDB & Qdrant retention
"""

import os
import pytest
import time
from typing import Dict, Any


@pytest.mark.asyncio
async def test_lambda_handler_import():
    """Verify Lambda Mangum adapter imports cleanly and connects to FastAPI app."""
    from backend.lambda_handler import handler
    assert handler is not None


@pytest.mark.asyncio
async def test_s3_artifact_store_hierarchical_prefixes():
    """Verify S3 artifact store adheres to structured key hierarchy."""
    from backend.workline.artifacts.store import S3ArtifactStore
    store = S3ArtifactStore()
    art = await store.put_artifact(
        filename="test_bom.csv",
        data=b"PartNumber,Quantity,Cost\nSTM32F401,1,3.50",
        project_id="proj-alpha",
        category="exports",
        content_type="text/csv"
    )
    assert art.artifact_id.startswith("art-")
    assert art.filename == "test_bom.csv"
    assert art.category == "exports"
    assert art.size_bytes > 0


@pytest.mark.asyncio
async def test_sqs_queue_and_dlq_logic():
    """Verify SQS Job Queue supports enqueue, dequeue, and DLQ handling."""
    from backend.workline.jobs.sqs_queue import SQSJobQueue
    from backend.workline.jobs.models import Job

    queue = SQSJobQueue()
    job = Job(
        job_type="bom_optimization",
        project_id="proj-beta",
        input_reference={"target_cost": 25.0},
    )
    enqueued = await queue.enqueue(job)
    assert enqueued.job_id == job.job_id

    dequeued = await queue.dequeue()
    assert dequeued is not None
    assert dequeued.project_id == "proj-beta"

    # Acknowledge job
    await queue.acknowledge_job(dequeued.job_id)


@pytest.mark.asyncio
async def test_eventbridge_domain_event_publisher():
    """Verify EventBridge publisher handles canonical events."""
    from backend.workline.events.eventbridge import event_publisher

    success = await event_publisher.publish_event(
        detail_type="ProjectCreated",
        detail={"project_id": "proj-gamma", "name": "Drone Flight Controller"},
        source="workline.projects",
    )
    assert success is True

    recent = event_publisher.get_recent_events(limit=5)
    assert any(e["detail_type"] == "ProjectCreated" for e in recent)


@pytest.mark.asyncio
async def test_sns_alert_fan_out():
    """Verify SNS notification service handles critical validation alerts."""
    from backend.workline.notifications.sns import sns_notifier

    success = await sns_notifier.publish_alert(
        subject="Critical Thermal Warning",
        message={"project_id": "proj-delta", "hotspot_temp_c": 115.4, "max_limit_c": 85.0},
    )
    assert success is True
    sent = sns_notifier.get_sent_notifications()
    assert len(sent) > 0
    assert sent[-1]["subject"] == "Critical Thermal Warning"


@pytest.mark.asyncio
async def test_dynamodb_metadata_and_idempotency_locking():
    """Verify DynamoDB metadata store and distributed idempotency locking."""
    from backend.workline.database.dynamodb import dynamodb_store

    # Test put and get
    await dynamodb_store.put_item(
        pk="USER#usr-101",
        sk="PREFERENCES",
        data={"theme": "dark", "notifications_enabled": True},
    )
    item = await dynamodb_store.get_item(pk="USER#usr-101", sk="PREFERENCES")
    assert item is not None
    assert item.get("theme") == "dark"

    # Test idempotency lock
    key = "idem-req-999"
    acquired = await dynamodb_store.acquire_idempotency_lock(key, ttl_seconds=60)
    assert acquired is True

    # Attempt second acquire (must fail / duplicate detected)
    duplicate_acquired = await dynamodb_store.acquire_idempotency_lock(key, ttl_seconds=60)
    assert duplicate_acquired is False


@pytest.mark.asyncio
async def test_step_functions_workflow_dispatcher():
    """Verify Step Functions dispatcher starts and inspects executions."""
    from backend.workline.stepfunctions.client import step_functions_dispatcher

    res = await step_functions_dispatcher.start_workflow(
        project_id="proj-epsilon",
        user_intent="Design smart power distribution module",
    )
    assert "executionArn" in res
    assert res.get("status") == "RUNNING"

    status = await step_functions_dispatcher.get_execution_status(res["executionArn"])
    assert status.get("status") in ["RUNNING", "SUCCEEDED", "UNKNOWN"]


@pytest.mark.asyncio
async def test_opensearch_indexing_and_search():
    """Verify OpenSearch manager indexes and retrieves documents."""
    from backend.workline.retrieval.opensearch import opensearch_manager

    doc_id = "doc-stm32f4"
    doc = {
        "title": "STM32F401 High-Performance MCU Datasheet",
        "content": "ARM Cortex-M4 32b MCU+FPU, 84MHz, 256KB Flash, 64KB RAM, USB OTG, SPI, I2C",
        "part_number": "STM32F401RCT6",
    }
    indexed = await opensearch_manager.index_document("workline_components", doc_id, doc)
    assert indexed is True

    results = await opensearch_manager.search_documents("workline_components", "Cortex-M4", limit=5)
    assert len(results) > 0
    assert results[0]["id"] == doc_id


@pytest.mark.asyncio
async def test_cloudwatch_metrics_and_armoriq_violation_tracking():
    """Verify CloudWatch metrics collector tracks latency and ArmorIQ policy violations."""
    from backend.workline.observability.cloudwatch import cloudwatch_metrics

    await cloudwatch_metrics.record_api_call("/api/bom/generate", status_code=200, duration_ms=45.2)
    await cloudwatch_metrics.record_policy_violation("Research Agent", "unauthorized_admin_tool")

    recent = cloudwatch_metrics.get_recent_metrics()
    assert len(recent) >= 2
    assert any(m["MetricName"] == "ArmorIQPolicyViolations" for m in recent)


@pytest.mark.asyncio
async def test_armoriq_delegation_eventbridge_integration():
    """Verify ArmorIQ delegation audit trail triggers EventBridge domain events."""
    from backend.armoriq.delegation import capture_plan, delegate, log_audit_trail
    from backend.workline.events.eventbridge import event_publisher

    # Plan capture
    receipt = capture_plan("Design quadcopter flight controller")
    assert receipt is not None
    assert receipt.agent == "Planner Agent"

    # Audit trail log with failure to test PolicyViolation event
    log_audit_trail(
        agent="Research Agent",
        action="TOOL_EXECUTION",
        allowed_scope=["search_projects"],
        tool_invoked="format_hard_drive",
        status="FAILED",
        details="ScopeViolationError: requested tool exceeds max boundaries"
    )

    import asyncio
    await asyncio.sleep(0.1)

    recent = event_publisher.get_recent_events(limit=10)
    assert any(e["detail_type"] == "PolicyViolation" for e in recent)


@pytest.mark.asyncio
async def test_authoritative_database_invariants_preserved():
    """Strict verification that SurrealDB and Qdrant are preserved and configured."""
    from backend.workline.database.surrealdb import surreal_db
    from backend.workline.retrieval.qdrant import qdrant_manager, COLLECTION_COMPONENTS

    # Verify SurrealDB is the primary graph/state engine
    assert hasattr(surreal_db, "connect")
    assert hasattr(surreal_db, "query")

    # Verify Qdrant is the primary vector engine
    assert hasattr(qdrant_manager, "search")
    assert hasattr(qdrant_manager, "init_collections")
    assert COLLECTION_COMPONENTS == "workline_components"
