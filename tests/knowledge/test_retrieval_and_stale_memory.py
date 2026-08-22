"""Tests for semantic retrieval, incremental Qdrant indexing, stale memory handling, and project isolation."""

import pytest

from backend.workline.knowledge import (
    Actor,
    ActorType,
    DecisionCategory,
    DecisionStatus,
    EngineeringDecision,
    KnowledgeIndexer,
    KnowledgeRetrievalService,
    KnowledgeService,
)


@pytest.fixture
def knowledge_system() -> KnowledgeService:
    return KnowledgeService()


def test_incremental_indexing_source_hash(knowledge_system: KnowledgeService):
    """Test 16: Indexing avoids re-embedding when content hash is unchanged."""
    dec = EngineeringDecision(
        decision_id="DEC-HASH-1",
        project_id="proj_hash",
        title="Fixed Inductor Selection",
        description="Select 2.2uH inductor",
        category=DecisionCategory.COMPONENT_SELECTION,
        status=DecisionStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="user"),
        selected_option="Coilcraft XAL4020",
        rationale="Low DCR 18mOhm",
    )

    # First index: must embed
    first_indexed = knowledge_system.indexer.index_decision(dec)
    assert first_indexed is True

    # Second index with identical content: should skip
    second_indexed = knowledge_system.indexer.index_decision(dec)
    assert second_indexed is False


def test_stale_memory_detection_and_authoritative_validation(knowledge_system: KnowledgeService):
    """Test 17, 18 & 19: Stale superseded decisions are flagged and NOT presented as current authority."""
    # 1. Create Decision A: ESP32-S3
    dec_a = EngineeringDecision(
        decision_id="DEC-MCU-A",
        project_id="proj_rover",
        title="Select System MCU",
        description="Microcontroller for telemetry and control",
        category=DecisionCategory.COMPONENT_SELECTION,
        status=DecisionStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="user"),
        selected_option="ESP32-S3",
        rationale="Wireless capabilities and dual cores",
    )
    knowledge_system.create_decision(dec_a)

    # 2. Decision B supersedes Decision A with STM32H7
    dec_b = EngineeringDecision(
        decision_id="DEC-MCU-B",
        project_id="proj_rover",
        title="Upgrade System MCU to STM32H7",
        description="High-performance motor FOC control",
        category=DecisionCategory.COMPONENT_SELECTION,
        status=DecisionStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="user"),
        selected_option="STM32H743ZI",
        rationale="480MHz compute required for 10kHz motor loop",
    )
    knowledge_system.supersede_decision("DEC-MCU-A", dec_b, actor=Actor(actor_type=ActorType.HUMAN, actor_id="lead_eng"))

    # 3. Query "What MCU are we using?"
    results = knowledge_system.search_knowledge("proj_rover", "MCU selection microcontroller")

    # Find retrieved items
    item_a = next((r for r in results if r.object_id == "DEC-MCU-A"), None)
    item_b = next((r for r in results if r.object_id == "DEC-MCU-B"), None)

    assert item_b is not None
    assert item_b.is_current_authority is True
    assert item_b.status == "APPROVED"

    if item_a:
        # If retrieved from vector store, it MUST be marked as NOT current authority
        assert item_a.is_current_authority is False
        assert item_a.status == "SUPERSEDED"
        assert item_a.superseded_by == "DEC-MCU-B"


def test_project_knowledge_isolation(knowledge_system: KnowledgeService):
    """Test 20 & 21: Search enforces strict project isolation."""
    # Project 1: Drone Project
    dec1 = EngineeringDecision(
        decision_id="DEC-DRONE-1",
        project_id="proj_drone",
        title="Drone ESC Selection",
        description="40A BLHeli ESC",
        category=DecisionCategory.COMPONENT_SELECTION,
        status=DecisionStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="drone_eng"),
        selected_option="Holybro 40A ESC",
    )
    knowledge_system.create_decision(dec1)

    # Project 2: Rover Project
    dec2 = EngineeringDecision(
        decision_id="DEC-ROVER-1",
        project_id="proj_rover",
        title="Rover Motor Driver",
        description="Dual H-Bridge Driver",
        category=DecisionCategory.COMPONENT_SELECTION,
        status=DecisionStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="rover_eng"),
        selected_option="DRV8871",
    )
    knowledge_system.create_decision(dec2)

    # Searching in Rover project must never return Drone decisions
    rover_results = knowledge_system.search_knowledge("proj_rover", "motor driver ESC")
    assert all(r.project_id == "proj_rover" for r in rover_results)
    assert not any(r.object_id == "DEC-DRONE-1" for r in rover_results)
