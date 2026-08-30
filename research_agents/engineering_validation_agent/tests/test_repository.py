"""
Unit tests for ValidationRepository interface (Section 45).
"""

import pytest
from research_agents.engineering_validation_agent.repository import InMemoryValidationRepository
from research_agents.engineering_validation_agent.schemas import (
    EngineeringValidationAgentOutput,
    FinalVerdict,
    RequirementValidationItem,
    ValidationItem,
    ValidationTraceabilityItem,
)


@pytest.mark.asyncio
async def test_validation_repository_all_methods():
    repo = InMemoryValidationRepository()
    proj_id = "proj_test_val_01"

    # 1. Save rule result
    await repo.save_validation_rule_result(
        ValidationItem(
            validation_id="VAL-01",
            category="electrical",
            title="Voltage Check",
            description="3.3V verified",
        ),
        proj_id,
    )

    # 2. Save requirement status
    await repo.save_requirement_status(
        RequirementValidationItem(
            requirement_id="REQ-01",
            description="Thermal sensing",
            status="PASS",
        ),
        proj_id,
    )

    # 3. Save verdict
    await repo.save_design_verdict(
        FinalVerdict(verdict="READY"),
        proj_id,
    )

    # 4. Save traceability
    await repo.save_validation_traceability(
        ValidationTraceabilityItem(
            traceability_id="TRACE-01",
            requirement_ids=["REQ-01"],
            status="PASS",
        ),
        proj_id,
    )

    # 5. Save full output
    output = EngineeringValidationAgentOutput(
        project_id=proj_id,
        validation_id="VAL-01",
        verdict="READY",
    )
    saved_id = await repo.save_validation(output)
    assert saved_id == proj_id

    retrieved = await repo.get_validation(proj_id)
    assert retrieved is not None
    assert retrieved.verdict == "READY"
