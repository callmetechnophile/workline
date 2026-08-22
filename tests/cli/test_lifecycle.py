"""Tests for engineering lifecycle stage model, initialization, and progress calculation."""

from cli.wline.core.lifecycle import (
    ORDERED_LIFECYCLE_STAGES,
    StageStatus,
    calculate_progress,
    create_default_lifecycle,
)


def test_lifecycle_initialization():
    """Test 12: Default lifecycle initialization contains all 36 stages."""
    lifecycle = create_default_lifecycle()

    assert lifecycle.current_stage == "requirements"
    assert lifecycle.status == "not_started"
    assert len(lifecycle.stages) == 36
    assert len(ORDERED_LIFECYCLE_STAGES) == 36

    # Verify first and last stages
    first_stage_id, first_stage_name = ORDERED_LIFECYCLE_STAGES[0]
    last_stage_id, last_stage_name = ORDERED_LIFECYCLE_STAGES[-1]

    assert first_stage_id == "requirements"
    assert first_stage_name == "PROJECT REQUIREMENTS"
    assert last_stage_id == "release"
    assert last_stage_name == "RELEASE"

    # Verify all stages are NOT_STARTED
    for stage_id, _ in ORDERED_LIFECYCLE_STAGES:
        assert stage_id in lifecycle.stages
        assert lifecycle.stages[stage_id].status == StageStatus.NOT_STARTED
        assert lifecycle.stages[stage_id].order >= 1


def test_lifecycle_progress_calculation():
    """Test 13: Progress calculation accurately computes percentage from stage states."""
    lifecycle = create_default_lifecycle()

    # Initial state (0% completed)
    assert calculate_progress(lifecycle) == 0.0

    # 1 stage completed out of 36 -> (1 / 36) * 100 = 2.777% -> 2.8%
    lifecycle.stages["requirements"].status = StageStatus.COMPLETED
    assert calculate_progress(lifecycle) == 2.8

    # 1 completed + 1 in progress (0.5 weight) -> 1.5 / 36 = 4.166% -> 4.2%
    lifecycle.stages["problem_definition"].status = StageStatus.IN_PROGRESS
    assert calculate_progress(lifecycle) == 4.2

    # 18 completed out of 36 -> 50.0%
    for i in range(18):
        stage_id, _ = ORDERED_LIFECYCLE_STAGES[i]
        lifecycle.stages[stage_id].status = StageStatus.COMPLETED
    assert calculate_progress(lifecycle) == 50.0

    # All 36 completed -> 100.0%
    for stage_id, _ in ORDERED_LIFECYCLE_STAGES:
        lifecycle.stages[stage_id].status = StageStatus.COMPLETED
    assert calculate_progress(lifecycle) == 100.0
