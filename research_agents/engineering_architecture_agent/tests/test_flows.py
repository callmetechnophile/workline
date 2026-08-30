"""
Unit tests for FlowBuilder (data flows, control flows, and feedback loops).
"""

from research_agents.engineering_architecture_agent.schemas import SubsystemItem
from research_agents.engineering_architecture_agent.services.flow_builder import FlowBuilder


def test_data_and_control_flows_with_feedback_loops():
    builder = FlowBuilder()
    subsystems = [
        SubsystemItem(subsystem_id="SUB-001", name="Compute Subsystem", purpose="AI compute"),
        SubsystemItem(subsystem_id="SUB-002", name="Sensing Subsystem", purpose="Sensors"),
        SubsystemItem(subsystem_id="SUB-004", name="Control Subsystem", purpose="Autopilot"),
    ]

    data_flows, control_flows, feedback_loops = builder.build_flows(subsystems)

    assert len(data_flows) >= 2
    assert "VoSPI" in data_flows[0].protocol or "SPI" in data_flows[0].protocol
    assert data_flows[0].latency_requirement is not None

    assert len(control_flows) >= 1
    assert "Human" in control_flows[0].trigger

    assert len(feedback_loops) >= 1
    assert feedback_loops[0].type == "closed_loop_control"
    assert feedback_loops[0].sensor != ""
    assert feedback_loops[0].actuator != ""
