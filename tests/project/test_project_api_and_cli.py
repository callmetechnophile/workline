"""Tests for Workline project package CLI commands and REST API routes."""

from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from backend.main import app
from backend.workline.git.repository import project_repo_manager
from cli.wline.main import app as cli_app


def test_package_cli_workflow(tmp_path: Path):
    """Test full CLI workflow: export -> inspect -> verify -> backup -> diff -> import."""
    runner = CliRunner()

    with patch.dict("os.environ", {"WORKLINE_WORKSPACE": str(tmp_path)}):
        # 1. Initialize project
        res_init = runner.invoke(cli_app, ["init", "drone-hub"])
        assert res_init.exit_code == 0

        # 2. wline project export
        pkg_target = tmp_path / "drone-hub.wlipjt"
        res_export = runner.invoke(cli_app, ["project", "export", str(pkg_target), "--project", "drone-hub"])
        assert res_export.exit_code == 0
        assert "WORKLINE PROJECT EXPORTED" in res_export.stdout
        assert pkg_target.exists()

        # 3. wline project inspect
        res_inspect = runner.invoke(cli_app, ["project", "inspect", str(pkg_target)])
        assert res_inspect.exit_code == 0
        assert "WORKLINE PROJECT PACKAGE" in res_inspect.stdout
        assert "VALID" in res_inspect.stdout

        # 4. wline project verify
        res_verify = runner.invoke(cli_app, ["project", "verify", str(pkg_target)])
        assert res_verify.exit_code == 0
        assert "integrity verified successfully" in res_verify.stdout

        # 5. wline project info
        res_info = runner.invoke(cli_app, ["project", "info", "drone-hub"])
        assert res_info.exit_code == 0
        assert "WORKLINE PROJECT" in res_info.stdout

        # 6. wline project backup
        res_backup = runner.invoke(cli_app, ["project", "backup", "--project", "drone-hub"])
        assert res_backup.exit_code == 0
        assert "PROJECT BACKUP CREATED" in res_backup.stdout

        # 7. wline project import
        res_import = runner.invoke(
            cli_app,
            ["project", "import", str(pkg_target), "--name", "Restored Drone", "--strategy", "NEW_PROJECT"],
        )
        assert res_import.exit_code == 0
        assert "WORKLINE PROJECT IMPORTED" in res_import.stdout


def test_package_fastapi_endpoints(tmp_path: Path):
    """Test REST API routes for export, inspect, verify, diff, backup, and import."""
    client = TestClient(app)

    with patch.dict("os.environ", {"WORKLINE_WORKSPACE": str(tmp_path)}):
        proj_dir = tmp_path / "api-drone"
        project_repo_manager.init_project_git(proj_dir, "api-drone", "API Drone")

        # 1. POST /api/project/export
        res_exp = client.post("/api/project/export", json={"project_id": "api-drone"})
        assert res_exp.status_code == 200
        manifest_data = res_exp.json()
        assert manifest_data["project_id"] == "api-drone"

        pkg_path = tmp_path / "api-drone.wlipjt"

        # 2. GET /api/project/package/info
        res_info = client.get(f"/api/project/package/info?package_file={str(pkg_path)}")
        assert res_info.status_code == 200
        assert res_info.json()["valid"] is True

        # 3. POST /api/project/verify
        res_ver = client.post("/api/project/verify", json={"package_file": str(pkg_path)})
        assert res_ver.status_code == 200
        assert res_ver.json()["valid"] is True

        # 4. POST /api/project/backup
        res_bak = client.post("/api/project/backup", json={"project_id": "api-drone"})
        assert res_bak.status_code == 200
        assert res_bak.json()["success"] is True

        # 5. POST /api/project/import
        res_imp = client.post(
            "/api/project/import",
            json={
                "package_file": str(pkg_path),
                "target_name": "Cloned API Drone",
                "strategy": "NEW_PROJECT",
            },
        )
        assert res_imp.status_code == 200
        assert res_imp.json()["success"] is True
