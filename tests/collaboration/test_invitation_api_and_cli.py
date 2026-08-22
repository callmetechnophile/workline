"""Tests for team invitation CLI commands and REST API endpoints."""

from pathlib import Path
from fastapi.testclient import TestClient
from typer.testing import CliRunner
import pytest

from backend.main import app
from backend.workline.collaboration.invitations import invitation_service
from cli.wline.commands.team import team_app


def test_cli_invitation_workflow(tmp_path: Path):
    """Test full CLI workflow: create -> list -> regenerate -> revoke."""
    runner = CliRunner()

    # 1. wline team invitation create
    res_create = runner.invoke(
        team_app,
        ["invitation", "create", "--team", "team_rover", "--ttl", "7", "--max-uses", "5"],
    )
    assert res_create.exit_code == 0
    assert "TEAM INVITATION" in res_create.stdout
    assert "https://workline.app/team/join/" in res_create.stdout

    # 2. wline team invitation list
    res_list = runner.invoke(team_app, ["invitation", "list", "--team", "team_rover"])
    assert res_list.exit_code == 0
    assert "Team Invitations (team_rover)" in res_list.stdout
    assert "ACTIVE" in res_list.stdout

    # Extract an invitation id from service
    invitations = invitation_service.list_invitations("team_rover")
    assert len(invitations) >= 1
    inv_id = invitations[0].invitation_id

    # 3. wline team invitation regenerate
    res_regen = runner.invoke(team_app, ["invitation", "regenerate", inv_id])
    assert res_regen.exit_code == 0
    assert "INVITATION REGENERATED" in res_regen.stdout

    # 4. wline team invitation revoke
    invitations_after = invitation_service.list_invitations("team_rover")
    active_inv = [i for i in invitations_after if i.status.value == "ACTIVE"][0]
    res_revoke = runner.invoke(team_app, ["invitation", "revoke", active_inv.invitation_id])
    assert res_revoke.exit_code == 0
    assert "has been revoked successfully" in res_revoke.stdout


def test_fastapi_invitation_endpoints():
    """Test REST API routes: create, preview, accept, list, revoke, regenerate."""
    client = TestClient(app)

    # 1. POST /api/teams/{team_id}/invitations
    res_create = client.post(
        "/api/teams/team_flight/invitations",
        json={"ttl_days": 14, "max_uses": 5, "role": "ENGINEER"},
    )
    assert res_create.status_code == 200
    data = res_create.json()
    assert data["team_id"] == "team_flight"
    assert "/team/join/" in data["join_url"]
    assert data["status"] == "ACTIVE"

    token = data["join_url"].split("/team/join/")[1]
    inv_id = data["invitation_id"]

    # 2. GET /api/invitations/{token}/preview
    res_prev = client.get(f"/api/invitations/{token}/preview")
    assert res_prev.status_code == 200
    prev_data = res_prev.json()
    assert prev_data["valid"] is True
    assert prev_data["team_id"] == "team_flight"

    # 3. POST /api/invitations/{token}/accept
    res_accept = client.post(
        f"/api/invitations/{token}/accept",
        json={"user_id": "eng_carol", "user_name": "Carol"},
    )
    assert res_accept.status_code == 200
    accept_data = res_accept.json()
    assert accept_data["success"] is True
    assert accept_data["team_id"] == "team_flight"

    # 4. GET /api/teams/{team_id}/invitations
    res_list = client.get("/api/teams/team_flight/invitations")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # 5. POST /api/teams/{team_id}/invitations/{id}/revoke
    res_rev = client.post(f"/api/teams/team_flight/invitations/{inv_id}/revoke")
    assert res_rev.status_code == 200
    assert res_rev.json()["status"] == "REVOKED"

    # 6. Attempt preview after revoke must return 404
    res_prev_after = client.get(f"/api/invitations/{token}/preview")
    assert res_prev_after.status_code == 404
