"""
Unit tests for AuthorizationGate and zero implicit authority (Sections 2, 7, 8, 9, 81, 82).
"""

from research_agents.engineering_execution_agent.schemas import AuthorizedExecution, ExecutionTask
from research_agents.engineering_execution_agent.services.authorization_gate import AuthorizationGate


def test_authorization_gate_validation_status_check():
    gate = AuthorizationGate()

    # READY passes
    passed, verdict, _ = gate.check_validation_gate({"verdict": "READY"})
    assert passed is True
    assert verdict == "READY"

    # READY_WITH_WARNINGS passes
    passed, verdict, _ = gate.check_validation_gate({"verdict": "READY_WITH_WARNINGS"})
    assert passed is True

    # BLOCKED fails
    passed, verdict, blocking = gate.check_validation_gate({"verdict": "BLOCKED", "critical_failures": ["RULE-ELEC-001"]})
    assert passed is False
    assert verdict == "BLOCKED"
    assert "RULE-ELEC-001" in blocking

    # INCOMPLETE fails
    passed, verdict, _ = gate.check_validation_gate({"verdict": "INCOMPLETE"})
    assert passed is False


def test_authorization_gate_scoped_checks():
    gate = AuthorizationGate()

    auth = AuthorizedExecution(
        authorization_id="AUTH-001",
        authorized_agent_id="EngineeringExecutionAgent",
        allowed_tasks=["TASK-001"],
        allowed_tools=["filesystem"],
        allowed_paths=["firmware/sensors/**"],
        allowed_operations=["read", "create", "modify"],
    )

    # 1. Authorized task passes
    task_valid = ExecutionTask(
        task_id="TASK-001",
        title="Write sensor driver",
        target_file="firmware/sensors/lepton.py",
        allowed_tools=["filesystem"],
        allowed_operations=["create"],
    )
    is_auth, status, _ = gate.validate_authorization(task_valid, auth, "proj_001")
    assert is_auth is True
    assert status == "AUTHORIZED"

    # 2. Unauthorized task ID fails
    task_invalid_id = ExecutionTask(
        task_id="TASK-999",
        title="Unlisted task",
        target_file="firmware/sensors/lepton.py",
        allowed_tools=["filesystem"],
    )
    is_auth, status, _ = gate.validate_authorization(task_invalid_id, auth, "proj_001")
    assert is_auth is False
    assert status == "AUTHORIZATION_DENIED"

    # 3. Unauthorized path fails (out of scope)
    task_invalid_path = ExecutionTask(
        task_id="TASK-001",
        title="Write server backend",
        target_file="backend/server.py",
        allowed_tools=["filesystem"],
    )
    is_auth, status, _ = gate.validate_authorization(task_invalid_path, auth, "proj_001")
    assert is_auth is False
    assert status == "OUT_OF_SCOPE"

    # 4. Unauthorized tool fails
    task_invalid_tool = ExecutionTask(
        task_id="TASK-001",
        title="Push code to git",
        allowed_tools=["git.push"],
    )
    is_auth, status, _ = gate.validate_authorization(task_invalid_tool, auth, "proj_001")
    assert is_auth is False
    assert status == "OUT_OF_SCOPE"


def test_authorization_gate_expired_and_revoked():
    gate = AuthorizationGate()

    # Expired
    auth_expired = AuthorizedExecution(
        authorization_id="AUTH-EXP",
        allowed_tasks=["TASK-001"],
        expires_at="2020-01-01T00:00:00Z",
    )
    task = ExecutionTask(task_id="TASK-001", title="Task 1")
    is_auth, status, _ = gate.validate_authorization(task, auth_expired, "proj_001")
    assert is_auth is False
    assert status == "EXPIRED_AUTHORITY"

    # Revoked
    auth_revoked = AuthorizedExecution(
        authorization_id="AUTH-REV",
        allowed_tasks=["TASK-001"],
        revoked=True,
    )
    is_auth, status, _ = gate.validate_authorization(task, auth_revoked, "proj_001")
    assert is_auth is False
    assert status == "REVOKED_AUTHORITY"
