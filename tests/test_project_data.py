import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from backend.routes.project_data import (
    serialize_to_wl_filemap,
    verify_auth_endpoint,
    sync_cloud_target,
    VerifyAuthRequest,
    CloudSyncRequest,
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_serialize_to_wl_filemap_structure():
    mock_project = {
        "project_id": "TEST-PROJ-01",
        "name": "Test Drone Power Subsystem",
        "description": "High-efficiency battery management",
        "status": "ACTIVE",
        "bom": {
            "components": [
                {"mpn": "TPS54331DDA", "manufacturer": "TI", "qty": 2},
                {"mpn": "STM32F405RGT6", "manufacturer": "STMicroelectronics", "qty": 1},
            ]
        },
        "requirements": {
            "requirements": [
                {"id": "REQ-01", "text": "Input voltage 18V-24V", "status": "VERIFIED"},
            ]
        },
        "research": {
            "papers": [
                {"arxiv_id": "2401.00001", "title": "Advanced BMS Topology"},
            ]
        },
    }
    meta = {"project_id": "TEST-PROJ-01", "project_name": "Test Drone Power Subsystem", "version": "1.0"}

    file_map = serialize_to_wl_filemap(mock_project, meta)

    # Core .wl files must exist
    assert "README.wl" in file_map
    assert ".wl/project.wl" in file_map
    assert ".wl/manifest.wl" in file_map
    assert ".wl/dependencies.wl" in file_map
    assert "bom/bom.wl" in file_map
    assert "bom/bom.csv" in file_map
    assert "requirements/functional.wl" in file_map
    assert "requirements/technical.wl" in file_map
    assert "research/findings.wl" in file_map

    # Invariant §8: Zero secrets exported
    assert "credentials: NOT_EXPORTED" in file_map[".wl/dependencies.wl"]
    assert "TEST-PROJ-01" in file_map["README.wl"]
    assert "TPS54331DDA" in file_map["bom/bom.csv"]


@pytest.mark.anyio
async def test_verify_auth_missing_token():
    req = VerifyAuthRequest(provider="github", token="")
    with pytest.raises(HTTPException) as exc_info:
        await verify_auth_endpoint(req)
    assert exc_info.value.status_code == 400


@pytest.mark.anyio
async def test_verify_auth_github_success():
    req = VerifyAuthRequest(provider="github", token="ghp_realvalidtoken123")
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "login": "octocat",
        "name": "The Octocat",
        "email": "octocat@github.com",
        "avatar_url": "https://avatars.githubusercontent.com/u/583231",
        "public_repos": 8,
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await verify_auth_endpoint(req)

        assert res["success"] is True
        assert res["provider"] == "github"
        assert res["account"] == "octocat"
        assert res["name"] == "The Octocat"
        assert res["avatar_url"] == "https://avatars.githubusercontent.com/u/583231"


@pytest.mark.anyio
async def test_verify_auth_github_bad_credentials():
    req = VerifyAuthRequest(provider="github", token="ghp_invalidtoken")

    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.content = b'{"message": "Bad credentials"}'
    mock_resp.json.return_value = {"message": "Bad credentials"}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await verify_auth_endpoint(req)

        assert res["success"] is False
        assert "Bad credentials" in res["error"]


@pytest.mark.anyio
async def test_verify_auth_google_drive_success():
    req = VerifyAuthRequest(provider="google_drive", token="ya29.sampletoken")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "email": "engineer@company.com",
        "name": "Jane Engineer",
        "picture": "https://lh3.googleusercontent.com/sample",
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await verify_auth_endpoint(req)

        assert res["success"] is True
        assert res["provider"] == "google_drive"
        assert res["account"] == "engineer@company.com"
        assert res["name"] == "Jane Engineer"


@pytest.mark.anyio
async def test_verify_auth_bitbucket_requires_username():
    req = VerifyAuthRequest(provider="bitbucket", token="some_app_password", username="")
    res = await verify_auth_endpoint(req)
    assert res["success"] is False
    assert "Username" in res["error"] and "App Password" in res["error"]


@pytest.mark.anyio
async def test_verify_auth_github_id_mismatch():
    req = VerifyAuthRequest(provider="github", token="ghp_realvalidtoken123", username="different_user")
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "login": "octocat",
        "name": "The Octocat",
        "email": "octocat@github.com",
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await verify_auth_endpoint(req)

        assert res["success"] is False
        assert "GitHub ID mismatch" in res["error"]
        assert "belongs to @octocat" in res["error"]


@pytest.mark.anyio
async def test_verify_auth_google_drive_id_mismatch():
    req = VerifyAuthRequest(provider="google_drive", token="ya29.sampletoken", username="wronguser@gmail.com")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "email": "actualuser@gmail.com",
        "name": "Actual User",
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await verify_auth_endpoint(req)

        assert res["success"] is False
        assert "Gmail ID mismatch" in res["error"]
        assert "actualuser@gmail.com" in res["error"]


def test_sync_cloud_target_unverified_rejected():
    # Attempting to sync with empty or unverified account should raise 401
    req = CloudSyncRequest(
        provider="github",
        account="",
        project_id="PROJ-01",
        project_data={"title": "Test"}
    )
    with pytest.raises(HTTPException) as exc_info:
        sync_cloud_target(req)
    assert exc_info.value.status_code == 401
    assert "Verification Required" in exc_info.value.detail

    req_fake = CloudSyncRequest(
        provider="gitlab",
        account="fake-user",
        project_id="PROJ-01",
        project_data={"title": "Test"}
    )
    with pytest.raises(HTTPException) as exc_info2:
        sync_cloud_target(req_fake)
    assert exc_info2.value.status_code == 401


def test_sync_cloud_target_verified_success():
    req = CloudSyncRequest(
        provider="github",
        account="verified_octocat",
        target="my-org/my-repo",
        project_id="PROJ-01",
        project_data={"title": "Test Project", "version": "1.0"}
    )
    res = sync_cloud_target(req)
    assert res["status"] == "synchronized"
    assert res["account"] == "verified_octocat"
    assert res["target"] == "my-org/my-repo"
    assert len(res["commit_hash"]) == 7

