"""
Unit tests for ActionProposalManager (Sections 36–38, 64, 80).
"""

from research_agents.engineering_copilot.services.action_proposal_mgr import ActionProposalManager


def test_action_proposal_creation_and_human_gating():
    mgr = ActionProposalManager()

    # Normal execution proposal
    p1 = mgr.create_action_proposal(
        project_id="p1",
        requested_action="Run TASK-001",
        target_agent="EngineeringExecutionAgent",
        is_destructive=False,
    )
    assert p1.status == "pending"
    assert p1.requires_authorization is True
    assert p1.requires_human_approval is False

    # Destructive / deployment proposal
    p2 = mgr.create_action_proposal(
        project_id="p1",
        requested_action="Deploy firmware to production hardware",
        is_destructive=True,
    )
    assert p2.requires_human_approval is True
