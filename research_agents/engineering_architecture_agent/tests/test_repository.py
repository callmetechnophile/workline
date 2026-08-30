"""
Unit tests for ArchitectureRepository interface (Section 41).
"""

import pytest
from research_agents.engineering_architecture_agent.repository import InMemoryArchitectureRepository
from research_agents.engineering_architecture_agent.schemas import (
    ArchitectureDecision,
    ArchitectureMeta,
    ArchitectureRisk,
    ArchitectureValidationRequirement,
    ComponentRoleItem,
    ControlFlowItem,
    DataFlowItem,
    DependencyItem,
    EngineeringArchitectureAgentOutput,
    InterfaceItem,
    PowerDomainItem,
    ProjectMeta,
    SubsystemItem,
)


@pytest.mark.asyncio
async def test_repository_all_methods():
    repo = InMemoryArchitectureRepository()
    proj_id = "proj_test_01"

    # 1. Save Subsystem
    await repo.save_subsystem(SubsystemItem(subsystem_id="SUB-01", name="Compute", purpose="AI"), proj_id)

    # 2. Save Component Role
    await repo.save_component_role(ComponentRoleItem(component="Jetson", role="processor", subsystem_id="SUB-01", reason="AI"), proj_id)

    # 3. Save Interface
    await repo.save_interface(InterfaceItem(interface_id="IF-01", source="SUB-01", target="SUB-02", interface_type="SPI", purpose="Video"), proj_id)

    # 4. Save Power Domain
    await repo.save_power_domain(PowerDomainItem(power_domain_id="PWR-01", name="5V Rail", source="Buck", voltage="5.0V", regulation="Buck", protection=[]), proj_id)

    # 5. Save Data Flow & Control Flow
    await repo.save_data_flow(DataFlowItem(flow_id="DATA-01", source="A", destination="B", data_type="Video", protocol="SPI"), proj_id)
    await repo.save_control_flow(ControlFlowItem(control_id="CTRL-01", control_source="A", control_target="B", trigger="T", decision_stage="D"), proj_id)

    # 6. Save Dependency, Decision, Risk, Validation
    await repo.save_dependency(DependencyItem(dependency_id="DEP-01", source="A", dependency_type="power", target="B", description="D"), proj_id)
    await repo.save_architecture_decision(ArchitectureDecision(architecture_decision_id="DEC-01", decision_area="Compute", selected_architecture="Edge", reason="AI"), proj_id)
    await repo.save_architecture_risk(ArchitectureRisk(risk_id="RISK-01", category="thermal", description="Thermal", mitigation="Fan"), proj_id)
    await repo.save_validation_requirement(ArchitectureValidationRequirement(validation_id="VAL-01", category="electrical", description="Test", acceptance_criteria="OK"), proj_id)
    await repo.save_architecture_relationship("node_a", "node_b", "contains")

    # 7. Save Full Output
    output = EngineeringArchitectureAgentOutput(
        project=ProjectMeta(project_id=proj_id, title="Test Project"),
        architecture=ArchitectureMeta(architecture_id="ARCH-01", architecture_name="Test Arch", description="Desc", architecture_type="Type"),
    )
    saved_id = await repo.save_architecture(output)
    assert saved_id == proj_id

    retrieved = await repo.get_architecture(proj_id)
    assert retrieved is not None
    assert retrieved.project.title == "Test Project"
