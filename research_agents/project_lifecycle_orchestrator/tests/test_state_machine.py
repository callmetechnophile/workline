"""
Unit tests for deterministic state transitions in ProjectLifecycleOrchestrator (Sections 7–9).
"""

from research_agents.project_lifecycle_orchestrator.services.next_action_engine import NextActionEngine


def test_state_machine_deterministic_progression():
    engine = NextActionEngine()

    # Research -> Synthesis
    a1 = engine.determine_next_action("p1", "RESEARCH")
    assert a1.next_state == "SYNTHESIS"
    assert a1.target_agent == "EngineeringSynthesisAgent"

    # Synthesis -> Architecture
    a2 = engine.determine_next_action("p1", "SYNTHESIS")
    assert a2.next_state == "ARCHITECTURE"
    assert a2.target_agent == "EngineeringArchitectureAgent"

    # Architecture -> BOM
    a3 = engine.determine_next_action("p1", "ARCHITECTURE")
    assert a3.next_state == "BOM"
    assert a3.target_agent == "ComponentPlanningAgent"

    # BOM -> Procurement
    a4 = engine.determine_next_action("p1", "BOM")
    assert a4.next_state == "PROCUREMENT"
    assert a4.target_agent == "BOMOptimizationAgent"

    # Procurement -> Validation
    a5 = engine.determine_next_action("p1", "PROCUREMENT")
    assert a5.next_state == "VALIDATION"
    assert a5.target_agent == "EngineeringValidationAgent"

    # Validation -> Planning
    a6 = engine.determine_next_action("p1", "VALIDATION", validation_status="READY")
    assert a6.next_state == "PLANNING"
    assert a6.target_agent == "ProjectExecutionAgent"

    # Planning -> Implementation
    a7 = engine.determine_next_action("p1", "PLANNING")
    assert a7.next_state == "IMPLEMENTATION"
    assert a7.target_agent == "EngineeringExecutionAgent"

    # Implementation -> QA
    a8 = engine.determine_next_action("p1", "IMPLEMENTATION")
    assert a8.next_state == "QA"
    assert a8.target_agent == "VerificationQAAgent"

    # QA -> Verified
    a9 = engine.determine_next_action("p1", "QA", qa_status="VERIFIED")
    assert a9.next_state == "VERIFIED"
