"""
Canonical verification test for the 27 internal WORKLINE agents.

Verifies:
1. All agent numbers 1 through 27 exist individually in the Authoritative Agent Registry.
2. None of the 27 agents are missing, unresolved, or collapsed.
3. Specific inspection for Agents #1, #10, #11, #12, #13, #14, #18, #24, #27.
4. Capability lookup for Agent #18.
5. Live health check for all 27 agents.
6. Proper error handling and exit code for non-existent agents (e.g., #31).
7. Pure JSON output format (--json) without decorative ANSI or banner output.
"""

import json
import pytest
from typer.testing import CliRunner

from cli.wline.main import app
from cli.wline.core.errors import ExitCode

runner = CliRunner()


EXPECTED_27_AGENTS = {
    1: "ResearchPaperAgent",
    2: "WebResearchAgent",
    3: "DocumentProcessingAgent",
    4: "DeepResearchAgent",
    5: "EngineeringSynthesisAgent",
    6: "EngineeringArchitectureAgent",
    7: "ComponentPlanningAgent",
    8: "BOMOptimizationAgent",
    9: "EngineeringValidationAgent",
    10: "EngineeringExecutionAgent",
    11: "VerificationQAAgent",
    12: "ProjectExecutionAgent",
    13: "EngineeringKnowledgeGraphAgent",
    14: "ProjectLifecycleOrchestrator",
    15: "EngineeringCopilotAgent",
    16: "EngineeringChangeControlAgent",
    17: "EngineeringComplianceAgent",
    18: "EngineeringVerificationAgent",
    19: "EngineeringSimulationAgent",
    20: "EngineeringOptimizationAgent",
    21: "EngineeringRiskAgent",
    22: "SecurityThreatModelingAgent",
    23: "HardwareThermalAgent",
    24: "ManufacturingDFMAgent",
    25: "CostSupplyChainAgent",
    26: "DeploymentOpsAgent",
    27: "TechDocAgent",
}


def test_registry_contains_all_27_agents_individually():
    """Verify that every agent from 1 to 27 exists in AuthoritativeAgentRegistry."""
    from armourflow.registry.registry import get_agent_registry

    reg = get_agent_registry()
    all_agents = reg.list_agents()
    indexed_agents = {a.agent_id: a for a in all_agents}

    missing = []
    for num in range(1, 28):
        canonical_id = f"agent.{num:02d}"
        if canonical_id not in indexed_agents:
            missing.append(canonical_id)

    assert not missing, f"Missing agents from registry: {missing}"
    assert len(all_agents) == 27, f"Expected exactly 27 agents, found {len(all_agents)}"


def test_cli_agents_list_displays_all_27_individually():
    """Verify 'wline agents list' outputs all 27 agents individually."""
    result = runner.invoke(app, ["agents", "list"])
    assert result.exit_code == 0, f"Command failed: {result.output}"

    output = result.output
    for num in range(1, 28):
        id_str = f"#{num:02d}"
        assert id_str in output, f"Agent {id_str} not individually listed in output:\n{output}"


def test_cli_agents_list_json_cleanliness():
    """Verify 'wline agents list --json' returns parseable JSON containing all 27 agents."""
    result = runner.invoke(app, ["agents", "list", "--json"])
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert "agents" in data
    assert len(data["agents"]) == 27
    assert data["total"] == 27

    agent_ids = {a["id"] for a in data["agents"]}
    for num in range(1, 28):
        assert f"agent.{num:02d}" in agent_ids


@pytest.mark.parametrize("agent_arg", ["1", "01", "#01", "agent.01", "agent.1", "Agent #1"])
def test_cli_agents_info_flexible_id_agent_01(agent_arg):
    """Verify 'wline agents info' accepts multiple flexible ID formats for Agent #1."""
    result = runner.invoke(app, ["agents", "info", agent_arg])
    assert result.exit_code == 0
    assert "ResearchPaperAgent" in result.output
    assert "agent.01" in result.output


@pytest.mark.parametrize("agent_num, expected_name", [
    (10, "EngineeringExecutionAgent"),
    (11, "VerificationQAAgent"),
    (12, "ProjectExecutionAgent"),
    (13, "EngineeringKnowledgeGraphAgent"),
    (14, "ProjectLifecycleOrchestrator"),
    (18, "EngineeringVerificationAgent"),
    (24, "ManufacturingDFMAgent"),
    (27, "TechDocAgent"),
])
def test_cli_agents_info_specific_milestones(agent_num, expected_name):
    """Verify info for critical milestones: #10-#14, #18, #24, #27."""
    result = runner.invoke(app, ["agents", "info", str(agent_num)])
    assert result.exit_code == 0
    assert expected_name in result.output


def test_cli_agents_info_json():
    """Verify 'wline agents info 18 --json' outputs valid clean JSON."""
    result = runner.invoke(app, ["agents", "info", "18", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["id"] == "agent.18"
    assert data["name"] == "EngineeringVerificationAgent"
    assert "verification.matrix" in data["capabilities"]


def test_cli_agents_capabilities_specific_agent():
    """Verify 'wline agents capabilities 18' returns capabilities directly for Agent #18."""
    result = runner.invoke(app, ["agents", "capabilities", "18"])
    assert result.exit_code == 0
    assert "verification.matrix" in result.output
    assert "verification.evidence" in result.output


def test_cli_agents_capabilities_specific_agent_json():
    """Verify 'wline agents capabilities 18 --json'."""
    result = runner.invoke(app, ["agents", "capabilities", "18", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["agent_id"] == "agent.18"
    assert "verification.matrix" in data["capabilities"]


def test_cli_agents_health():
    """Verify 'wline agents health' runs and checks all 27 agents."""
    result = runner.invoke(app, ["agents", "health"])
    assert result.exit_code == 0
    for num in range(1, 28):
        assert f"#{num:02d}" in result.output


def test_cli_agents_health_json():
    """Verify 'wline agents health --json' outputs valid JSON with 27 health records."""
    result = runner.invoke(app, ["agents", "health", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "agent_health" in data
    assert len(data["agent_health"]) == 27
    for record in data["agent_health"]:
        assert "status" in record
        assert "importable" in record


def test_cli_agents_invalid_id():
    """Verify non-existent agent returns error message and deterministic exit code 2."""
    result = runner.invoke(app, ["agents", "info", "31"])
    assert result.exit_code == int(ExitCode.INVALID_ARGUMENTS)
    assert "Agent '31' does not exist" in result.output or "Valid agent IDs: 1-27" in result.output


def test_cli_agents_invalid_id_json():
    """Verify non-existent agent with --json outputs clean JSON with error code."""
    result = runner.invoke(app, ["agents", "info", "99", "--json"])
    assert result.exit_code == int(ExitCode.INVALID_ARGUMENTS)
    data = json.loads(result.output)
    assert data["status"] == "error"
    assert data["code"] == int(ExitCode.INVALID_ARGUMENTS)
