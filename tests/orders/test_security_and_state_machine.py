"""Unit tests for Order State Machine transitions, Role Policies, and Audit Logging."""

import asyncio
import pytest
from backend.workline.orders.audit import OrderAuditLogger
from backend.workline.orders.models import (
    ApprovalStatus,
    AuditEventType,
    Order,
    OrderStatus,
)
from backend.workline.orders.policies.approval import ApprovalPolicyValidator
from backend.workline.orders.service import OrderService
from backend.workline.orders.validator import OrderValidator


def test_order_state_machine_valid_and_invalid_transitions():
    """Test state machine enforcement: valid sequence vs blocked illegal jumps."""
    validator = OrderValidator()

    # Valid transitions
    ok1, _ = validator.validate_transition(OrderStatus.DRAFT, OrderStatus.VALIDATING)
    assert ok1 is True

    ok2, _ = validator.validate_transition(OrderStatus.APPROVED, OrderStatus.PAYMENT_REQUIRED)
    assert ok2 is True

    ok3, _ = validator.validate_transition(OrderStatus.PAYMENT_AUTHORIZED, OrderStatus.SUBMITTING)
    assert ok3 is True

    # Invalid illegal state jumps
    bad1, err1 = validator.validate_transition(OrderStatus.DRAFT, OrderStatus.CONFIRMED)
    assert bad1 is False
    assert "Invalid state transition" in err1

    bad2, err2 = validator.validate_transition(OrderStatus.PAYMENT_REQUIRED, OrderStatus.SUBMITTED)
    assert bad2 is False


def test_role_policy_and_agent_approval_prohibition():
    """Test role privilege boundaries and ensure autonomous agents are strictly forbidden from approving orders."""
    approval_val = ApprovalPolicyValidator()

    # Owner / Admin can approve
    ok_owner, _ = approval_val.can_approve_order(user_role="OWNER", is_agent=False)
    assert ok_owner is True

    ok_admin, _ = approval_val.can_approve_order(user_role="ADMIN", is_agent=False)
    assert ok_admin is True

    # Viewer cannot approve
    ok_viewer, err_viewer = approval_val.can_approve_order(user_role="VIEWER", is_agent=False)
    assert ok_viewer is False
    assert "lacks order approval authority" in err_viewer

    # Autonomous Agent CANNOT approve under any circumstances
    ok_agent, err_agent = approval_val.can_approve_order(user_role="OWNER", is_agent=True)
    assert ok_agent is False
    assert "Autonomous agents cannot approve orders" in err_agent


def test_order_audit_trail_logging():
    """Test append-only immutable audit trail recording."""
    async def _run():
        logger = OrderAuditLogger()
        evt = await logger.log_event(
            order_id="WL-ORD-AUDIT",
            project_id="test_proj",
            event_type=AuditEventType.USER_APPROVED,
            user_id="user:lead",
            actor_type="USER",
            actor_id="Lead Engineer",
            previous_status="READY_FOR_APPROVAL",
            new_status="APPROVED",
        )
        assert evt.event_id is not None
        assert evt.event_type == AuditEventType.USER_APPROVED

        events = logger.get_order_events("WL-ORD-AUDIT")
        assert len(events) >= 1
        assert events[-1].event_type == AuditEventType.USER_APPROVED

    asyncio.run(_run())
