"""
Workline AI — Sequential Orchestration (R1 -> R2 -> R3 -> R4 -> R5) & Context Isolation Test Suite.

Verifies:
1. Sequential stage execution order with explicit stage contracts.
2. Versioned context lineage (based_on: requirements_revision, research_revision, architecture_revision).
3. Fail-fast error propagation (downstream stages never run if upstream fails).
4. Strict data isolation between Project A (USB-C Hub) and Project B (Autonomous Quadcopter).
5. Switching A -> B -> A with zero context leakage or stale cross-domain artifacts.
6. Pipeline run and stage run persistence in database.
"""

import pytest
from backend.database import init_db, get_pipeline_run, get_pipeline_stages_for_run, get_pipeline_runs_for_project
from backend.workline.pipeline.orchestrator import SequentialPipelineOrchestrator, PipelineStageError
from backend.agents.planner_agent import run_engineering_pipeline


@pytest.fixture(autouse=True)
def setup_database():
    """Ensure clean schema with pipeline tracking tables."""
    init_db()


def test_sequential_pipeline_execution_and_lineage():
    """Verify that R1 executes R2 -> R3 -> R4 -> R5 sequentially and records exact versioned lineage."""
    orchestrator = SequentialPipelineOrchestrator(run_id="test_run_seq_001")
    project_id = "PROJ-USB-HUB-1"
    intent = "High-speed USB 3.2 Gen 2 Type-C Hub Controller with Power Delivery"
    
    result = orchestrator.execute_pipeline(
        project_id=project_id,
        user_intent=intent,
        project_name="USB-C Hub Pro",
        target_days=30,
        engineering_template="USB-C Hub",
        team_id="Embedded Hardware Team",
    )

    # Verify return payload contains lineage and stage outputs
    assert result["project_id"] == project_id
    assert result["project_name"] == "USB-C Hub Pro"
    assert "pipeline_lineage" in result
    lineage = result["pipeline_lineage"]
    assert lineage["requirements_revision"] >= 1
    assert lineage["research_revision"] >= 1
    assert lineage["architecture_revision"] >= 1
    assert lineage["bom_revision"] >= 1

    # Verify BOM and cost
    assert len(result["bom"]) > 0
    assert result["total_usd"] > 0

    # Verify database persistence
    run_db = get_pipeline_run("test_run_seq_001")
    assert run_db is not None
    assert run_db["project_id"] == project_id
    assert run_db["status"] == "COMPLETED"
    assert run_db["current_stage"] == "COMPLETED"

    stages = get_pipeline_stages_for_run("test_run_seq_001")
    assert len(stages) == 4
    stage_names = [s["stage"] for s in stages]
    assert stage_names == ["R2_REQUIREMENTS", "R3_RESEARCH", "R4_ENGINEERING", "R5_BOM"]
    assert all(s["status"] == "COMPLETED" for s in stages)


def test_fail_fast_stops_downstream_stages(monkeypatch):
    """Verify that when an upstream stage (e.g. R3) fails, downstream stages (R4, R5) are never invoked."""
    orchestrator = SequentialPipelineOrchestrator(run_id="test_run_fail_002")
    project_id = "PROJ-FAIL-TEST"

    # Mock R3 to raise an exception
    def failing_r3(*args, **kwargs):
        raise RuntimeError("R3 Literature Vector Database Unreachable")

    monkeypatch.setattr(orchestrator, "_execute_r3_research", failing_r3)

    r4_invoked = False
    def track_r4(*args, **kwargs):
        nonlocal r4_invoked
        r4_invoked = True

    monkeypatch.setattr(orchestrator, "_execute_r4_engineering", track_r4)

    with pytest.raises(PipelineStageError) as exc_info:
        orchestrator.execute_pipeline(
            project_id=project_id,
            user_intent="Fail Fast Verification Node",
        )

    assert "R3_RESEARCH" in str(exc_info.value)
    assert not r4_invoked, "R4 must NOT be executed if R3 fails!"

    # Verify database recorded FAILED state
    run_db = get_pipeline_run("test_run_fail_002")
    assert run_db is not None
    assert run_db["status"] == "FAILED"
    assert run_db["current_stage"] == "R3_RESEARCH"


def test_strict_project_data_isolation_usb_vs_quadcopter():
    """
    Test Project A (USB-C Hub) vs Project B (Autonomous Quadcopter).
    Verify zero cross-domain leakage or hardcoded global fallbacks.
    """
    # 1. Run Project A (USB-C Hub)
    res_a = run_engineering_pipeline(
        user_intent="High-speed USB 3.2 Gen 2 Type-C Hub Controller with Power Delivery",
        project_name="USB-C Hub Controller",
        project_id="PROJ-USB-A",
    )

    bom_a_names = [c["component"].lower() for c in res_a["bom"]]
    bom_a_text = " ".join(bom_a_names)

    # Verify USB components present
    assert any("usb" in name or "controller" in name or "tps" in name or "esd" in name for name in bom_a_names), \
        f"USB-C Hub BOM should have USB components, got: {bom_a_names}"

    # Verify ABSOLUTELY NO Drone components in Project A
    forbidden_drone_terms = ["pixhawk", "620kv", "brushless motor", "dshot", "lipo", "quadcopter", "airframe"]
    for term in forbidden_drone_terms:
        assert term not in bom_a_text, f"Forbidden drone term '{term}' leaked into Project A (USB-C Hub)!"

    # 2. Run Project B (Autonomous Quadcopter)
    res_b = run_engineering_pipeline(
        user_intent="Autonomous Quadcopter with GPS Waypoints and Cargo Delivery Hook",
        project_name="Autonomous Quadcopter",
        project_id="PROJ-DRONE-B",
    )

    bom_b_names = [c["component"].lower() for c in res_b["bom"]]
    bom_b_text = " ".join(bom_b_names)

    # Verify Drone components present
    assert any("pixhawk" in name or "motor" in name or "esc" in name or "lipo" in name or "frame" in name for name in bom_b_names), \
        f"Drone BOM should have flight/motor components, got: {bom_b_names}"

    # Verify ABSOLUTELY NO USB-C Hub controller components in Project B
    forbidden_usb_terms = ["usb5734", "tps65987d", "tpd4e05u06", "type-c 24-pin"]
    for term in forbidden_usb_terms:
        assert term not in bom_b_text, f"Forbidden USB term '{term}' leaked into Project B (Drone)!"

    # 3. Re-run Project A to verify switching A -> B -> A has NO context leakage or stale state
    res_a2 = run_engineering_pipeline(
        user_intent="High-speed USB 3.2 Gen 2 Type-C Hub Controller with Power Delivery",
        project_name="USB-C Hub Controller",
        project_id="PROJ-USB-A",
    )

    bom_a2_names = [c["component"].lower() for c in res_a2["bom"]]
    bom_a2_text = " ".join(bom_a2_names)
    for term in forbidden_drone_terms:
        assert term not in bom_a2_text, f"Forbidden drone term '{term}' leaked into Project A on switch-back!"
