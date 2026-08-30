"""
Unit tests for ArmorIQ authorization separation (Sections 26–28, 71).
"""

from research_agents.project_lifecycle_orchestrator.services.armoriq_delegator import ArmorIQDelegator


def test_armoriq_delegation_granted_and_denied():
    # 1. Granted authority
    delegator_grant = ArmorIQDelegator(simulate_denial=False)
    grant = delegator_grant.request_delegation_authority(
        project_id="p1",
        target_agent="EngineeringExecutionAgent",
        task_id="TASK-01",
        required_scopes=["filesystem.write"],
    )
    assert grant["authorized"] is True
    assert grant["status"] == "GRANTED"

    # 2. Denied authority
    delegator_deny = ArmorIQDelegator(simulate_denial=True)
    deny = delegator_deny.request_delegation_authority(
        project_id="p1",
        target_agent="EngineeringExecutionAgent",
        task_id="TASK-01",
        required_scopes=["filesystem.write"],
    )
    assert deny["authorized"] is False
    assert deny["status"] == "DENIED"
