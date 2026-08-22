"""Tests for Generation FastAPI routes and Typer CLI subcommands."""

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from backend.main import app
from cli.wline.main import app as cli_app

client = TestClient(app)
runner = CliRunner()


def test_api_generation_image_and_presentation():
    # 1. POST /api/generation/image
    img_res = client.post(
        "/api/generation/image",
        json={
            "project_id": "api_rover",
            "purpose": "ARCHITECTURE",
            "prompt": "Highlight SurrealDB and Qdrant integration",
            "aspect_ratio": "16:9",
        },
    )
    assert img_res.status_code == 200
    img_data = img_res.json()
    assert img_data["provider"] == "PaperBanana"
    assert img_data["format"] == "svg"
    art_id = img_data["artifact_id"]

    # 2. POST /api/generation/presentation
    pres_res = client.post(
        "/api/generation/presentation",
        json={
            "project_id": "api_rover",
            "title": "API Rover Architecture Deck",
            "slide_count": 6,
        },
    )
    assert pres_res.status_code == 200
    pres_data = pres_res.json()
    assert pres_data["provider"] == "Gamma"
    assert pres_data["slide_count"] == 6

    # 3. GET /api/generation/artifacts
    list_res = client.get("/api/generation/artifacts?project_id=api_rover")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 2

    # 4. GET /api/generation/artifacts/{id}
    detail_res = client.get(f"/api/generation/artifacts/{art_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["artifact_id"] == art_id


def test_cli_generation_subcommands():
    # 1. wline generate image
    res = runner.invoke(cli_app, ["generate", "image", "-p", "cli_test_proj"])
    assert res.exit_code == 0
    assert "WORKLINE TECHNICAL VISUAL GENERATION" in res.stdout
    assert "PaperBanana" in res.stdout or "Paper Banana" in res.stdout

    # 2. wline generate architecture
    res = runner.invoke(cli_app, ["generate", "architecture", "-p", "cli_arch_proj"])
    assert res.exit_code == 0

    # 3. wline generate pcb-visual
    res = runner.invoke(cli_app, ["generate", "pcb-visual", "-p", "cli_pcb_proj"])
    assert res.exit_code == 0

    # 4. wline generate presentation
    res = runner.invoke(cli_app, ["generate", "presentation", "-p", "cli_deck_proj", "-s", "6"])
    assert res.exit_code == 0
    assert "WORKLINE TECHNICAL PRESENTATION GENERATION" in res.stdout

    # 5. wline generate deck
    res = runner.invoke(cli_app, ["generate", "deck", "-p", "cli_deck_proj"])
    assert res.exit_code == 0
