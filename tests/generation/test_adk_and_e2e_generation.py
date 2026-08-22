"""Tests for Google ADK Generation tools and End-to-End visual & presentation workflows."""

import pytest
from backend.workline.agents.generation_tools import (
    generate_architecture_image,
    generate_hackathon_deck,
    generate_pcb_visual,
    generate_presentation,
    generate_project_visual,
)


@pytest.mark.asyncio
async def test_adk_visual_generation_tools():
    # 1. Architecture visual
    arch_res = await generate_architecture_image("rover_v2")
    assert arch_res["status"] == "COMPLETED"
    assert arch_res["provider"] == "PaperBanana"
    assert arch_res["format"] == "svg"

    # 2. PCB visual
    pcb_res = await generate_pcb_visual("rover_v2")
    assert pcb_res["status"] == "COMPLETED"
    assert pcb_res["format"] == "svg"


@pytest.mark.asyncio
async def test_adk_presentation_generation_tools():
    # 1. Standard technical presentation
    pres_res = await generate_presentation(
        project_id="rover_v2",
        title="Rover Architecture Review",
        slide_count=6,
    )
    assert pres_res["status"] == "COMPLETED"
    assert pres_res["provider"] == "Gamma"
    assert pres_res["slide_count"] == 6

    # 2. Hackathon pitch deck
    hack_res = await generate_hackathon_deck("rover_v2", "Autonomous Exploration Rover")
    assert hack_res["status"] == "COMPLETED"
    assert hack_res["provider"] == "Gamma"
    assert hack_res["slide_count"] == 7
