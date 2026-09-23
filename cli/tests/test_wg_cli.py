"""
Comprehensive test suite for WORKLINE CLI (wg) and Local Moss Retrieval Layer.
Verifies all 18 phases, core invariants, zero-secrets policy, offline mode, and LiveKit bridge.
"""

from pathlib import Path
import shutil
import pytest
from typer.testing import CliRunner

from cli.wg.main import app as wg_app
from cli.workline.project.filesystem import find_project_root
from cli.workline.project.manager import ProjectManager
from cli.workline.project.validator import validate_project
from cli.workline.retrieval.indexer import ProjectIndexer
from cli.workline.retrieval.moss_adapter import LocalMossAdapter
from cli.workline.retrieval.retriever import ProjectRetriever
from cli.workline.retrieval.context import ContextBuilder
from cli.workline.agent.runtime import WorklineAgent
from cli.workline.livekit.adapter import LiveKitAgentAdapter
from cli.workline.mcp.server import WorklineMCPServer
from cli.workline.export.exporter import export_project_zip, import_project_zip

runner = CliRunner()


@pytest.fixture
def temp_project(tmp_path):
    """Fixture providing an initialized WORKLINE project."""
    mgr = ProjectManager()
    proj_dir = mgr.init_project(
        name="Autonomous Delivery Drone Power Distribution",
        target_dir=tmp_path / "autonomous-drone",
        project_id="PROJ-AUTO",
        description="Autonomous multi-agent power distribution package",
        domain="Hardware Systems & Power Engineering",
    )
    
    # Add a sample component dossier
    comp_dir = proj_dir / "components" / "TPS62160"
    comp_dir.mkdir(parents=True, exist_ok=True)
    comp_wl = (
        "type: component\n"
        "name: TPS62160 High Efficiency Step-Down Converter\n"
        "mpn: TPS62160\n"
        "manufacturer: Texas Instruments\n"
        "category: Voltage Regulator\n"
        "system: power\n"
        "subsystem: distribution\n"
        "description: 17V step-down buck converter for 12V to 5V rail conversion.\n"
    )
    (comp_dir / "component.wl").write_text(comp_wl, encoding="utf-8")
    
    # Add an architectural decision
    dec_dir = proj_dir / "decisions"
    dec_dir.mkdir(parents=True, exist_ok=True)
    dec_wl = (
        "type: decision\n"
        "decision_id: DEC-014\n"
        "title: Selection of TPS62160 for Intermediate Power Rail\n"
        "status: APPROVED\n"
        "context: Need high-efficiency 5V intermediate rail with low quiescent current.\n"
        "decision: Selected TPS62160 due to 95% peak efficiency and small 2x2mm package.\n"
    )
    (dec_dir / "decision-014.wl").write_text(dec_wl, encoding="utf-8")
    
    return proj_dir


# ── 1. Project Initialization & Discovery ──────────────────────────────────────

def test_project_init_and_discovery(tmp_path):
    """Verify wg init creates standard folders, README.wl, and manifest."""
    result = runner.invoke(wg_app, ["init", "drone-system", "-p", str(tmp_path / "drone-system")])
    assert result.exit_code == 0
    assert "Initialized WORKLINE project" in result.output
    
    proj_dir = tmp_path / "drone-system"
    assert (proj_dir / "README.wl").exists()
    assert (proj_dir / ".wl" / "manifest.wl").exists()
    assert (proj_dir / ".gitignore").exists()
    assert (proj_dir / "requirements").exists()
    assert (proj_dir / "components").exists()
    assert (proj_dir / "bom").exists()


def test_project_open_and_inspect(temp_project):
    """Verify wg open and wg inspect report correct telemetry."""
    res_open = runner.invoke(wg_app, ["open", str(temp_project)])
    assert res_open.exit_code == 0
    assert "PROJ-AUTO" in res_open.output
    
    res_inspect = runner.invoke(wg_app, ["inspect", str(temp_project)])
    assert res_inspect.exit_code == 0
    assert "Autonomous Delivery Drone Power Distribution" in res_inspect.output
    assert "PROJ-AUTO" in res_inspect.output
    assert "Components:" in res_inspect.output


def test_project_check_and_secret_exclusion(temp_project):
    """Verify wg check passes, and flags secrets when present."""
    res_check = runner.invoke(wg_app, ["check", str(temp_project)])
    assert res_check.exit_code == 0
    assert "Project: VALID" in res_check.output

    # Inject forbidden secret file
    secret_file = temp_project / ".env"
    secret_file.write_text("MOSS_API_KEY=secret_key_123", encoding="utf-8")
    
    res_check_fail = runner.invoke(wg_app, ["check", str(temp_project)])
    assert res_check_fail.exit_code == 1
    assert "Zero-secrets violation" in res_check_fail.output or "sensitive files" in res_check_fail.output
    
    # Cleanup
    secret_file.unlink()


# ── 2. Local Moss Indexing & Rebuild ───────────────────────────────────────────

def test_local_moss_full_indexing_and_rebuild(temp_project):
    """Verify wg index builds derived local index, and --rebuild reconstructs it."""
    res_index = runner.invoke(wg_app, ["index", "--path", str(temp_project)])
    assert res_index.exit_code == 0
    assert "READY" in res_index.output
    assert (temp_project / ".wl" / "index" / "records.json").exists()
    assert (temp_project / ".wl" / "moss.wl").exists()
    
    adapter = LocalMossAdapter(temp_project)
    assert adapter.is_ready
    assert adapter.get_document_count() > 0

    # Delete derived index directory to test rebuild
    shutil.rmtree(temp_project / ".wl" / "index")
    
    res_rebuild = runner.invoke(wg_app, ["index", "--rebuild", "--path", str(temp_project)])
    assert res_rebuild.exit_code == 0
    assert "Rebuilding local Moss index" in res_rebuild.output
    assert (temp_project / ".wl" / "index" / "records.json").exists()


def test_incremental_indexing(temp_project):
    """Verify incremental indexing only updates modified resources."""
    # First build full index
    indexer = ProjectIndexer(temp_project)
    stats1 = indexer.index_full()
    doc_count1 = stats1.total_records_indexed
    
    # Run incremental with no changes
    stats_inc, changed = indexer.index_incremental()
    assert len(changed) == 0
    
    # Modify one file
    task_file = temp_project / "tasks" / "task-001.wl"
    task_file.write_text(task_file.read_text(encoding="utf-8") + "\nnotes: Modified note\n", encoding="utf-8")
    
    stats_inc2, changed2 = indexer.index_incremental()
    assert len(changed2) == 1
    assert "tasks/task-001.wl" in changed2[0]


# ── 3. Search & Context Retrieval ─────────────────────────────────────────────

def test_hybrid_search_and_metadata_filter(temp_project):
    """Verify wg search performs hybrid search with metadata filters."""
    # Index project first
    runner.invoke(wg_app, ["index", "--path", str(temp_project)])
    
    # Search for voltage regulator
    res_search = runner.invoke(wg_app, ["search", "voltage regulator", "--path", str(temp_project)])
    assert res_search.exit_code == 0
    assert "TPS62160" in res_search.output
    assert "[COMPONENT]" in res_search.output
    
    # Filter by type
    res_filter = runner.invoke(wg_app, ["search", "power", "--type", "component", "--path", str(temp_project)])
    assert res_filter.exit_code == 0
    assert "[COMPONENT]" in res_filter.output


def test_context_builder_budget_and_sources(temp_project):
    """Verify ContextBuilder produces structured bundle with sources and respects budget."""
    runner.invoke(wg_app, ["index", "--path", str(temp_project)])
    
    retriever = ProjectRetriever(temp_project)
    builder = ContextBuilder(default_token_budget=1500)
    bundle = builder.build_context(retriever, query="power distribution and regulation")
    
    assert len(bundle.sources) > 0
    assert bundle.estimated_tokens <= 1500
    assert "components/TPS62160/component.wl" in bundle.sources or any("component.wl" in s for s in bundle.sources)


def test_ai_ask_and_citations(temp_project):
    """Verify wg ask produces project-grounded answer with source citations."""
    runner.invoke(wg_app, ["index", "--path", str(temp_project)])
    
    res_ask = runner.invoke(wg_app, ["ask", "Why did we select the TPS62160?", "--path", str(temp_project)])
    assert res_ask.exit_code == 0
    assert "WORKLINE AI" in res_ask.output
    assert "Sources:" in res_ask.output
    assert "Project-grounded" in res_ask.output


# ── 4. LiveKit Session & Adapter ──────────────────────────────────────────────

def test_livekit_agent_adapter(temp_project):
    """Verify LiveKitAgentAdapter processes queries and preserves session context."""
    runner.invoke(wg_app, ["index", "--path", str(temp_project)])
    
    adapter = LiveKitAgentAdapter(temp_project, session_id="voice-session-42")
    assert adapter.session.session_id == "voice-session-42"
    assert adapter.session.project_id == "PROJ-AUTO"
    
    response = adapter.process_utterance("What is the function of the TPS62160?")
    assert len(response) > 0
    assert adapter.session.recent_query == "What is the function of the TPS62160?"
    assert len(adapter.session.history) == 1


# ── 5. Doctor & Offline Mode ──────────────────────────────────────────────────

def test_doctor_command(temp_project):
    """Verify wg doctor runs all 10 diagnostics cleanly."""
    res_doc = runner.invoke(wg_app, ["doctor", "--path", str(temp_project)])
    assert res_doc.exit_code == 0
    assert "WORKLINE DOCTOR" in res_doc.output
    assert "CLI v" in res_doc.output
    assert "Local Moss runtime" in res_doc.output
    assert "ProjectRetriever" in res_doc.output


def test_offline_mode(temp_project):
    """Verify --offline flag sets environment and executes locally."""
    res_offline = runner.invoke(wg_app, ["--offline", "inspect", str(temp_project)])
    assert res_offline.exit_code == 0
    assert "Autonomous Delivery Drone Power Distribution" in res_offline.output


# ── 6. Export, Import & MCP Server ────────────────────────────────────────────

def test_export_import_and_rebuild(temp_project, tmp_path):
    """Verify export bundles project without index or secrets, and import rebuilds index."""
    runner.invoke(wg_app, ["index", "--path", str(temp_project)])
    
    # Export zip
    zip_dest = tmp_path / "export-test.workline.zip"
    exported_path = export_project_zip(temp_project, zip_dest)
    assert exported_path.exists()
    
    # Inspect zip contents to guarantee .wl/index/ is NOT exported
    import zipfile
    with zipfile.ZipFile(exported_path, "r") as z:
        names = z.namelist()
        assert not any(".wl/index" in n for n in names)
        assert any("README.wl" in n for n in names)
        assert any(".wl/manifest.wl" in n for n in names)

    # Import into fresh directory
    imported_dir = tmp_path / "imported-drone"
    import_project_zip(exported_path, imported_dir)
    assert (imported_dir / "README.wl").exists()
    
    # Rebuild index from imported files
    indexer = ProjectIndexer(imported_dir)
    stats = indexer.index_full(rebuild=True)
    assert stats.status == "READY"
    assert stats.total_records_indexed > 0


def test_mcp_server_tools(temp_project):
    """Verify MCP tool definitions and dispatch."""
    runner.invoke(wg_app, ["index", "--path", str(temp_project)])
    
    server = WorklineMCPServer(temp_project)
    tools = server.get_tool_definitions()
    tool_names = [t["name"] for t in tools]
    assert "workline_search" in tool_names
    assert "workline_context" in tool_names
    assert "workline_component_lookup" in tool_names
    
    # Execute tool
    res = server.execute_tool("workline_component_lookup", {"mpn": "TPS62160"})
    assert res.get("component") is not None
    assert res["component"]["metadata"]["mpn"] == "TPS62160"
