"""
Unit tests for FailureRouter loops (Sections 19–22).
"""

from research_agents.project_lifecycle_orchestrator.services.failure_router import FailureRouter


def test_failure_router_architecture_bom_test():
    router = FailureRouter()

    # Architecture Conformance Failure -> Agent #6
    act_arch = router.route_failure("p1", "ARCHITECTURE_CONFORMANCE_FAILURE", "Interface mismatch")
    assert act_arch.target_agent == "EngineeringArchitectureAgent"
    assert act_arch.next_state == "ARCHITECTURE"

    # BOM Conformance Failure -> Agent #8
    act_bom = router.route_failure("p1", "BOM_CONFORMANCE_FAILURE", "Unapproved capacitor substitute")
    assert act_bom.target_agent == "BOMOptimizationAgent"
    assert act_bom.next_state == "BOM"

    # Test Failure -> Agent #10
    act_test = router.route_failure("p1", "TEST_FAILURE", "Driver assertion error")
    assert act_test.target_agent == "ProjectExecutionAgent"
    assert act_test.next_state == "PLANNING"
