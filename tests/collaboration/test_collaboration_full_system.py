import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.workline.collaboration.teams.models import TeamRole
from backend.workline.collaboration.teams.service import team_service, PermissionDeniedError
from backend.workline.collaboration.tasks.models import TaskPriority, TaskStatus, RelatedArtifact, CreateTaskRequest, UpdateTaskRequest
from backend.workline.collaboration.tasks.service import task_service
from backend.workline.collaboration.comments.models import CreateCommentRequest
from backend.workline.collaboration.comments.service import comment_service
from backend.workline.collaboration.approvals.models import ApprovalStatus, CreateApprovalRequest, ResolveApprovalRequest
from backend.workline.collaboration.approvals.service import approval_service
from backend.workline.collaboration.notifications.service import notification_service
from backend.workline.collaboration.permissions import permission_service, ActionType, ArtifactType
from backend.services.connection_chatbot_service import ask_connection_assistant


@pytest.fixture
def client():
    return TestClient(app)


def test_join_code_format_and_preview(client):
    # 1. Create a team and verify WL-XXXXXX join code format
    team = team_service.create_team(name="Robotics Core Team", creator_user_id="engineer_lead", project_id="proj_robotics_1")
    assert team.join_code is not None
    assert team.join_code.startswith("WL-")
    assert len(team.join_code) == 9  # "WL-" + 6 chars
    code_body = team.join_code[3:]
    unambiguous_alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    for char in code_body:
        assert char in unambiguous_alphabet
        assert char not in "01IO"

    # 2. Test preview endpoint without joining
    res = client.get(f"/api/teams/preview-code/{team.join_code}")
    assert res.status_code == 200
    data = res.json()
    assert data["team_name"] == "Robotics Core Team"
    assert data["member_count"] == 1
    assert data["require_join_approval"] is False

    # Also preview works case-insensitively and without prefix
    res_lower = client.get(f"/api/teams/preview-code/{team.join_code.lower()}")
    assert res_lower.status_code == 200

    res_raw = client.get(f"/api/teams/preview-code/{code_body}")
    assert res_raw.status_code == 200


def test_join_approval_workflow(client):
    # Team requiring approval to join
    team = team_service.create_team(name="Avionics Flight Team", creator_user_id="flight_dir")
    team_service.update_team_settings(team.team_id, "flight_dir", require_join_approval=True)

    # User attempts to join with require_approval=True
    join_res = team_service.join_team(team.join_code, user_id="cadet_bob")
    assert join_res.status == "PENDING_APPROVAL"
    assert "admin must approve" in join_res.message.lower()

    # Verify membership requests list
    reqs = team_service.list_membership_requests(team.team_id, "flight_dir")
    assert len(reqs) == 1
    assert reqs[0].user_id == "cadet_bob"
    assert reqs[0].status.value == "PENDING"

    # Review request: approve
    res = team_service.review_membership_request(
        request_id=reqs[0].id,
        action="APPROVE",
        actor_user_id="flight_dir",
        assigned_role=TeamRole.ENGINEER
    )
    assert res["status"] == "APPROVED"
    members = {m["user_id"]: m["role"] for m in team_service.list_members(team.team_id, "flight_dir")}
    assert "cadet_bob" in members
    assert members["cadet_bob"] == TeamRole.ENGINEER.value


def test_ownership_transfer_safety():
    team = team_service.create_team(name="Battery Pack Team", creator_user_id="lead_alice")
    team_service.add_member(team.team_id, "lead_alice", "engineer_carol", TeamRole.ENGINEER)

    # Demoting or transferring requires exact team name confirmation
    with pytest.raises(ValueError):
        team_service.transfer_ownership(team.team_id, target_user_id="engineer_carol", actor_user_id="lead_alice", confirmation_phrase="Wrong Name")

    # Transfer with correct confirmation
    transferred = team_service.transfer_ownership(team.team_id, target_user_id="engineer_carol", actor_user_id="lead_alice", confirmation_phrase="Battery Pack Team")
    members_map = {m["user_id"]: m["role"] for m in team_service.list_members(team.team_id, "engineer_carol")}
    assert members_map["engineer_carol"] == TeamRole.OWNER.value
    assert members_map["lead_alice"] == TeamRole.ADMIN.value
    assert transferred["status"] == "TRANSFERRED"
    assert transferred["new_owner"] == "engineer_carol"

    # Invariant: cannot remove sole owner
    with pytest.raises(PermissionDeniedError):
        team_service.remove_member(team.team_id, target_user_id="engineer_carol", actor_user_id="lead_alice")


def test_tasks_with_artifact_linking():
    team = team_service.create_team(name="Sensor Architecture", creator_user_id="sensor_lead")
    
    # Create task linked to BOM component MPU6050
    payload = CreateTaskRequest(
        team_id=team.team_id,
        project_id="proj_sensor_1",
        title="Verify I2C Pull-Up Resistors on MPU6050",
        description="Check 4.7k pullups on SDA/SCL lines for 400kHz Fast Mode.",
        priority=TaskPriority.HIGH,
        assignee_id="sensor_lead",
        related_artifact=RelatedArtifact(
            artifact_type="BOM",
            artifact_id="comp_mpu6050",
            artifact_name="MPU6050 IMU Accelerometer/Gyro",
        )
    )
    task = task_service.create_task(payload=payload, creator_id="sensor_lead")
    assert task.related_artifact is not None
    assert task.related_artifact.artifact_type == "BOM"
    assert task.related_artifact.artifact_name == "MPU6050 IMU Accelerometer/Gyro"

    # Update task status
    update_payload = UpdateTaskRequest(status=TaskStatus.IN_PROGRESS)
    updated = task_service.update_task(task.id, payload=update_payload, actor_id="sensor_lead")
    assert updated.status == TaskStatus.IN_PROGRESS


def test_comments_and_mentions_generate_notifications():
    team = team_service.create_team(name="Thermal Team", creator_user_id="lead_dave")
    team_service.add_member(team.team_id, "lead_dave", "analyst_emma", TeamRole.RESEARCHER)

    # Lead comments mentioning analyst_emma
    comment_payload = CreateCommentRequest(
        project_id="proj_thermal",
        team_id=team.team_id,
        parent_type="TASK",
        parent_id="task_thermal_sim",
        content="Hey @analyst_emma, please review the boundary conditions for the heatsink simulation."
    )
    comment = comment_service.create_comment(
        payload=comment_payload,
        author_id="lead_dave",
        author_name="Dave Lead"
    )
    assert "analyst_emma" in comment.mentions

    # Verify notification created for analyst_emma
    notifs = notification_service.list_notifications(user_id="analyst_emma", unread_only=True)
    matching = [n for n in notifs if n.type.value == "MENTION"]
    assert len(matching) >= 1
    assert "mentioned you" in matching[0].title


def test_approvals_workflow():
    team = team_service.create_team(name="Power Electronics", creator_user_id="lead_felix")
    team_service.add_member(team.team_id, "lead_felix", "eng_george", TeamRole.ENGINEER)

    # eng_george submits BOM substitution approval
    payload = CreateApprovalRequest(
        project_id="proj_pwr",
        team_id=team.team_id,
        artifact_type="COMPONENT_SUBSTITUTION",
        artifact_id="comp_lm7805",
        action="Substitute LM7805 with MP1584 Buck Converter",
        reason="Improves efficiency from 38% to 92% under 1.5A load.",
        diff_summary="LM7805 -> MP1584EN",
    )
    req = approval_service.create_request(payload=payload, requester_id="eng_george", requester_name="George Engineer")
    assert req.status == ApprovalStatus.PENDING

    # Review and approve by lead_felix (OWNER/ADMIN)
    resolve_payload = ResolveApprovalRequest(
        status=ApprovalStatus.APPROVED,
        notes="Approved for prototype batch 2."
    )
    approved = approval_service.resolve_request(
        approval_id=req.id,
        payload=resolve_payload,
        approver_id="lead_felix",
        approver_name="Felix Lead"
    )
    assert approved.status == ApprovalStatus.APPROVED
    assert approved.approver_id == "lead_felix"


def test_rbac_artifact_permissions():
    team = team_service.create_team(name="Firmware Team", creator_user_id="fw_lead")
    team_service.add_member(team.team_id, "fw_lead", "auditor_helen", TeamRole.VIEWER)

    # Viewer can READ tasks but cannot CREATE or UPDATE
    assert permission_service.can_perform("auditor_helen", team.team_id, ArtifactType.TASK, ActionType.READ) is True
    assert permission_service.can_perform("auditor_helen", team.team_id, ArtifactType.TASK, ActionType.CREATE) is False
    assert permission_service.can_perform("auditor_helen", team.team_id, ArtifactType.TEAM_MANAGEMENT, ActionType.APPROVE) is False

    # Owner can do everything
    assert permission_service.can_perform("fw_lead", team.team_id, ArtifactType.TEAM_MANAGEMENT, ActionType.APPROVE) is True


def test_chatbot_team_collaboration_context():
    team = team_service.create_team(name="Avionics AI Squad", creator_user_id="chief_engineer")
    task_payload = CreateTaskRequest(
        team_id=team.team_id,
        project_id="proj_avionics",
        title="Flash Bootloader on STM32H7",
        priority=TaskPriority.CRITICAL,
        assignee_id="chief_engineer",
    )
    task_service.create_task(payload=task_payload, creator_id="chief_engineer")

    context = {"team_id": team.team_id, "project_id": "proj_avionics", "bom": []}
    
    # Query tasks
    reply = ask_connection_assistant("Who is working on what tasks?", context, user_id="chief_engineer")
    assert "Bedrock DeepSeek" in reply or "Collaboration Agent" in reply or "Flash Bootloader" in reply
