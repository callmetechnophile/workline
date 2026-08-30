"""
Unit tests for EngineeringQueryRouter (Sections 6–9).
"""

from research_agents.engineering_copilot.services.query_router import EngineeringQueryRouter


def test_query_router_intent_classification_and_entity_extraction():
    router = EngineeringQueryRouter()

    # 1. Requirement Trace
    i1, e1 = router.classify_intent_and_entities("Trace REQ-SAR-001 through the system")
    assert i1 == "REQUIREMENT_TRACE"
    assert e1["requirement_id"] == "REQ-SAR-001"

    # 2. Component Impact
    i2, e2 = router.classify_intent_and_entities("What happens if I replace component 500-0771-01?")
    assert i2 == "COMPONENT_IMPACT"
    assert e2["component_id"] == "500-0771-01"

    # 3. BOM Comparison
    i3, _ = router.classify_intent_and_entities("Compare BOM V1 and V2")
    assert i3 == "BOM_COMPARISON"

    # 4. Next Action
    i4, _ = router.classify_intent_and_entities("What should happen next?")
    assert i4 == "NEXT_ACTION"

    # 5. Failure Query
    i5, _ = router.classify_intent_and_entities("Why is the project blocked?")
    assert i5 == "FAILURE_QUERY"

    # 6. Action Request
    i6, e6 = router.classify_intent_and_entities("Run TASK-001")
    assert i6 == "ACTION_REQUEST"
    assert e6["task_id"] == "TASK-001"
