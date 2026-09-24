"""
Test suite for LiveKit Realtime Agent Integration in WORKLINE CLI.
Verifies WorklineRealtimeAgent, dynamic Moss retrieval through ProjectRetriever,
multi-turn live session context, project-scoped rooms, zero-secrets policy,
and team collaboration room integration.
"""

from pathlib import Path
import pytest
from typer.testing import CliRunner

from cli.wg.main import app as wg_app
from cli.workline.agent.realtime_agent import WorklineRealtimeAgent
from cli.workline.config.config import LiveKitConfig, WorklineCLIConfig
from cli.workline.livekit.adapter import LiveKitAgentAdapter
from cli.workline.project.manager import ProjectManager
from cli.workline.retrieval.retriever import ProjectRetriever

runner = CliRunner()


@pytest.fixture
def realtime_project(tmp_path):
    """Fixture providing an initialized WORKLINE project with components and decisions."""
    mgr = ProjectManager()
    proj_dir = mgr.init_project(
        name="Autonomous Delivery Drone Power Distribution",
        target_dir=tmp_path / "drone-realtime",
        project_id="PROJ-AUTO",
        description="Autonomous power distribution system with synchronous buck-boost",
        domain="Hardware Systems & Power Engineering",
    )
    
    # 1. Component dossier
    comp_dir = proj_dir / "components" / "TPS62160"
    comp_dir.mkdir(parents=True, exist_ok=True)
    comp_wl = (
        "type: component\n"
        "name: TPS62160 High Efficiency Step-Down Converter\n"
        "mpn: TPS62160\n"
        "manufacturer: Texas Instruments\n"
        "category: Voltage Regulator\n"
        "system: power\n"
        "subsystem: power\n"
        "description: 17V step-down buck converter for 12V to 5V rail conversion.\n"
    )
    (comp_dir / "component.wl").write_text(comp_wl, encoding="utf-8")
    
    # 2. Decision dossier
    dec_dir = proj_dir / "decisions"
    dec_dir.mkdir(parents=True, exist_ok=True)
    dec_wl = (
        "type: decision\n"
        "decision_id: DEC-014\n"
        "title: Selection of TPS62160 for Intermediate Power Rail\n"
        "status: APPROVED\n"
        "subsystem: power\n"
        "context: Need high-efficiency 5V intermediate rail with low quiescent current.\n"
        "decision: Selected TPS62160 due to 95% peak efficiency and small 2x2mm package.\n"
    )
    (dec_dir / "decision-014.wl").write_text(dec_wl, encoding="utf-8")
    
    # 3. BOM line item
    bom_file = proj_dir / "bom" / "bom.wl"
    bom_content = (
        "bom_id: BOM-PROJ-AUTO\n"
        "project_id: PROJ-AUTO\n"
        "items:\n"
        "  - mpn: TPS62160\n"
        "    manufacturer: Texas Instruments\n"
        "    category: Voltage Regulator\n"
        "    quantity: 2\n"
        "    unit_cost: 1.25\n"
        "    supplier: DigiKey\n"
    )
    bom_file.write_text(bom_content, encoding="utf-8")
    
    # Index project using ProjectIndexer
    from cli.workline.retrieval.indexer import ProjectIndexer
    ProjectIndexer(proj_dir).index_full()
    
    return proj_dir


def test_livekit_config_loading_and_zero_secrets(realtime_project, monkeypatch):
    """Verify LiveKit configuration loads from .wl/livekit.wl and env without storing secrets."""
    livekit_file = realtime_project / ".wl" / "livekit.wl"
    assert livekit_file.exists()
    
    content = livekit_file.read_text(encoding="utf-8")
    assert "livekit:" in content
    assert "agent_name: workline-realtime-agent" in content
    assert "room_prefix: workline-project-" in content
    # Strict zero-secrets check: API keys and secrets must NOT be in the file
    assert "LIVEKIT_API_KEY" not in content
    assert "LIVEKIT_API_SECRET" not in content

    # Test loading with environment variables
    monkeypatch.setenv("LIVEKIT_URL", "wss://livekit.example.com")
    monkeypatch.setenv("LIVEKIT_API_KEY", "devkey123")
    monkeypatch.setenv("LIVEKIT_API_SECRET", "secretxyz456")

    cfg = LiveKitConfig.load(realtime_project)
    assert cfg.enabled is True
    assert cfg.url == "wss://livekit.example.com"
    assert cfg.api_key == "devkey123"
    assert cfg.api_secret == "secretxyz456"
    assert cfg.room_prefix == "workline-project-"


def test_project_scoped_room_name(realtime_project):
    """Verify project-scoped room name conforms to workline-project-{project_id}."""
    adapter = LiveKitAgentAdapter(realtime_project)
    room_name = adapter.get_room_name()
    assert room_name == "workline-project-proj-auto"


def test_realtime_agent_live_context_multi_turn(realtime_project):
    """
    Verify WorklineRealtimeAgent multi-turn live context flow:
    Turn 1: 'Tell me about the power system.' -> identifies power subsystem
    Turn 2: 'What about the regulator?' -> retrieves TPS62160 regulator
    Turn 3: 'Why did we select it?' -> retrieves DEC-014 decision
    """
    agent = WorklineRealtimeAgent(realtime_project)
    
    # Turn 1: Power system overview
    turn1 = agent.process_realtime_input("Tell me about the power system.")
    assert "power" in turn1["active_subsystem"]
    assert turn1["turn"] == 1
    assert len(turn1["sources"]) > 0
    assert "Sources:" in turn1["answer"]

    # Turn 2: Follow-up on regulator (anaphoric context resolution)
    turn2 = agent.process_realtime_input("What about the regulator?")
    assert turn2["turn"] == 2
    assert "TPS62160" in turn2["answer"]
    assert any("component.wl" in s or "bom.wl" in s for s in turn2["sources"])

    # Turn 3: Follow-up on decision rationale
    turn3 = agent.process_realtime_input("Why did we select it?")
    assert turn3["turn"] == 3
    assert any("DEC-014" in s or "decision-014.wl" in s for s in turn3["sources"])
    assert "decision-014.wl" in turn3["answer"] or "95%" in turn3["answer"] or "TPS62160" in turn3["answer"]


def test_voice_command_startup_flow(realtime_project):
    """Verify voice_command outputs the official WORKLINE REALTIME status banner."""
    import typer
    from cli.workline.commands.voice import voice_command
    test_app = typer.Typer()
    test_app.command()(voice_command)
    result = runner.invoke(test_app, ["--path", str(realtime_project)])
    assert result.exit_code == 0
    assert "WORKLINE REALTIME" in result.output
    assert "Autonomous Delivery Drone Power Distribution" in result.output
    assert "LiveKit:" in result.output
    assert "CONNECTED" in result.output
    assert "Moss:" in result.output
    assert "READY" in result.output
    assert "Agent:" in result.output
    assert "READY" in result.output
    assert "Listening..." in result.output


def test_livekit_token_generation(realtime_project):
    """Verify participant token generation for LiveKit project room."""
    adapter = LiveKitAgentAdapter(realtime_project)
    token = adapter.generate_token(participant_identity="engineer_rahul")
    assert token.startswith("lk_token_engineer_rahul_") or len(token) > 20


def test_team_collaboration_realtime_room(realtime_project):
    """Verify team collaboration room handles multi-user conversation and agent responses."""
    adapter = LiveKitAgentAdapter(realtime_project)
    
    # User 1 sends message
    res1 = adapter.broadcast_team_message(sender="engineer_1", message="Hello team, starting review.")
    assert res1["agent_response"] is None  # Not addressed to agent
    assert "engineer_1" in res1["participants"]
    
    # User 2 asks an engineering question
    res2 = adapter.broadcast_team_message(sender="engineer_2", message="What regulator are we using for 5V?")
    assert res2["agent_response"] is not None
    assert "TPS62160" in res2["agent_response"]
    assert "Sources:" in res2["agent_response"]
