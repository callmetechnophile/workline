"""
Parser and generator for README.wl - the primary project entry point.

Expanded to support the full WORKLINE project schema including:
- intent block (what the project is trying to achieve)
- state block (current lifecycle phase and stage)
- analysis_entrypoint block (pointer to analysis/power.wl, etc.)
- livekit block (realtime session configuration, zero-secrets)
- moss block (local retrieval status)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class ProjectIntent:
    """What the project is trying to achieve."""
    goal: str = ""
    problem_statement: str = ""
    constraints: List[str] = field(default_factory=list)
    target_platform: str = ""
    budget_usd: float = 0.0


@dataclass
class ProjectState:
    """Current lifecycle state of the project."""
    stage: str = "requirements"       # requirements, architecture, bom, pinout, firmware, simulation, release
    phase: str = "active"             # active, paused, archived, released
    completion_pct: int = 0
    last_updated: str = ""
    active_milestone: str = ""


@dataclass
class AnalysisEntrypoint:
    """Pointers to key analysis files."""
    power_analysis: str = "analysis/power.wl"
    thermal_analysis: str = "analysis/thermal.wl"
    pcb_analysis: str = "analysis/pcb.wl"
    primary: str = "analysis/power.wl"


@dataclass
class LiveKitConfig:
    """Zero-secrets LiveKit room configuration for this project."""
    room_name: str = ""          # workline-project-{project_id}
    enabled: bool = False
    session_ttl_minutes: int = 60
    # NOTE: No API keys stored here — loaded from environment at runtime


@dataclass
class MossStatus:
    """Local Moss retrieval index status embedded in README.wl."""
    status: str = "UNINITIALIZED"    # UNINITIALIZED, INDEXING, READY, STALE
    document_count: int = 0
    indexed_at: str = ""
    index_path: str = ".wl/index/"


@dataclass
class ProjectIdentity:
    """Complete project identity and high-level summary from README.wl."""
    name: str
    project_id: str
    version: str = "1.0"
    status: str = "ACTIVE"
    domain: str = "Hardware Systems & Engineering"
    description: str = ""
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_workline_version: str = "1.0.0"
    schema_version: str = "2.0"
    # Extended blocks (v2 schema)
    intent: ProjectIntent = field(default_factory=ProjectIntent)
    state: ProjectState = field(default_factory=ProjectState)
    analysis_entrypoint: AnalysisEntrypoint = field(default_factory=AnalysisEntrypoint)
    livekit: LiveKitConfig = field(default_factory=LiveKitConfig)
    moss: MossStatus = field(default_factory=MossStatus)
    raw_data: Dict[str, Any] = field(default_factory=dict)


# ── Parser ────────────────────────────────────────────────────────────────────

def parse_readme_wl(readme_path: Path) -> ProjectIdentity:
    """
    Parse a README.wl file into a ProjectIdentity instance.
    Handles both v1 schema (flat) and v2 schema (with intent/state/analysis_entrypoint blocks).
    """
    if not readme_path.exists():
        raise FileNotFoundError(f"README.wl not found at {readme_path}")

    content = readme_path.read_text(encoding="utf-8")

    # Strip optional decorative headers (e.g. WORKLINE_PROJECT followed by ===)
    lines = content.splitlines()
    clean_lines = []
    skip_header = True

    for line in lines:
        stripped = line.strip()
        if skip_header:
            if stripped.startswith("WORKLINE_PROJECT") or (stripped and set(stripped) == {"="}):
                continue
            if ":" in stripped:
                skip_header = False
                clean_lines.append(line)
        else:
            clean_lines.append(line)

    parsed_yaml = yaml.safe_load("\n".join(clean_lines)) or {}

    # Parse extended blocks
    intent_data = parsed_yaml.get("intent", {}) or {}
    intent = ProjectIntent(
        goal=str(intent_data.get("goal", "")),
        problem_statement=str(intent_data.get("problem_statement", "")),
        constraints=list(intent_data.get("constraints", [])),
        target_platform=str(intent_data.get("target_platform", "")),
        budget_usd=float(intent_data.get("budget_usd", 0.0)),
    )

    state_data = parsed_yaml.get("state", {}) or {}
    state = ProjectState(
        stage=str(state_data.get("stage", "requirements")),
        phase=str(state_data.get("phase", "active")),
        completion_pct=int(state_data.get("completion_pct", 0)),
        last_updated=str(state_data.get("last_updated", "")),
        active_milestone=str(state_data.get("active_milestone", "")),
    )

    ae_data = parsed_yaml.get("analysis_entrypoint", {}) or {}
    ae = AnalysisEntrypoint(
        power_analysis=str(ae_data.get("power_analysis", "analysis/power.wl")),
        thermal_analysis=str(ae_data.get("thermal_analysis", "analysis/thermal.wl")),
        pcb_analysis=str(ae_data.get("pcb_analysis", "analysis/pcb.wl")),
        primary=str(ae_data.get("primary", "analysis/power.wl")),
    )

    lk_data = parsed_yaml.get("livekit", {}) or {}
    livekit = LiveKitConfig(
        room_name=str(lk_data.get("room_name", "")),
        enabled=bool(lk_data.get("enabled", False)),
        session_ttl_minutes=int(lk_data.get("session_ttl_minutes", 60)),
    )

    moss_data = parsed_yaml.get("moss", {}) or {}
    moss = MossStatus(
        status=str(moss_data.get("status", "UNINITIALIZED")),
        document_count=int(moss_data.get("document_count", 0)),
        indexed_at=str(moss_data.get("indexed_at", "")),
        index_path=str(moss_data.get("index_path", ".wl/index/")),
    )

    return ProjectIdentity(
        name=str(parsed_yaml.get("name", "Untitled Project")),
        project_id=str(parsed_yaml.get("project_id", "PROJ-DEFAULT")),
        version=str(parsed_yaml.get("version", "1.0")),
        status=str(parsed_yaml.get("status", "ACTIVE")),
        domain=str(parsed_yaml.get("domain", "Hardware Systems & Engineering")),
        description=str(parsed_yaml.get("description", "")),
        generated_at=str(parsed_yaml.get("generated_at", datetime.now(timezone.utc).isoformat())),
        source_workline_version=str(parsed_yaml.get("source_workline_version", "1.0.0")),
        schema_version=str(parsed_yaml.get("schema_version", "2.0")),
        intent=intent,
        state=state,
        analysis_entrypoint=ae,
        livekit=livekit,
        moss=moss,
        raw_data=parsed_yaml,
    )


# ── Generator ─────────────────────────────────────────────────────────────────

def generate_readme_wl(
    identity: ProjectIdentity,
    resource_counts: Optional[Dict[str, int]] = None,
) -> str:
    """Generate canonical README.wl file content (v2 schema)."""
    counts = resource_counts or {}

    doc = [
        "WORKLINE_PROJECT",
        "================",
        "",
        f"name: {identity.name}",
        f"project_id: {identity.project_id}",
        f"version: {identity.version}",
        f"status: {identity.status}",
        f"domain: {identity.domain}",
        f"description: {identity.description}",
        f"schema_version: {identity.schema_version}",
        f"generated_at: {identity.generated_at}",
        f"source_workline_version: {identity.source_workline_version}",
        "",
        "# ── Project Intent ───────────────────────────────────────────────────",
        "intent:",
        f"  goal: {identity.intent.goal}",
        f"  problem_statement: {identity.intent.problem_statement}",
        f"  target_platform: {identity.intent.target_platform}",
        f"  budget_usd: {identity.intent.budget_usd}",
    ]

    if identity.intent.constraints:
        doc.append("  constraints:")
        for c in identity.intent.constraints:
            doc.append(f"    - {c}")
    else:
        doc.append("  constraints: []")

    doc += [
        "",
        "# ── Project State ────────────────────────────────────────────────────",
        "state:",
        f"  stage: {identity.state.stage}",
        f"  phase: {identity.state.phase}",
        f"  completion_pct: {identity.state.completion_pct}",
        f"  last_updated: {identity.state.last_updated or datetime.now(timezone.utc).isoformat()}",
        f"  active_milestone: {identity.state.active_milestone}",
        "",
        "# ── Analysis Entrypoints ─────────────────────────────────────────────",
        "analysis_entrypoint:",
        f"  primary: {identity.analysis_entrypoint.primary}",
        f"  power_analysis: {identity.analysis_entrypoint.power_analysis}",
        f"  thermal_analysis: {identity.analysis_entrypoint.thermal_analysis}",
        f"  pcb_analysis: {identity.analysis_entrypoint.pcb_analysis}",
        "",
        "# ── LiveKit Realtime Session ─────────────────────────────────────────",
        "# NOTE: No API keys stored here. Keys are loaded from environment at runtime.",
        "livekit:",
        f"  room_name: {identity.livekit.room_name or f'workline-project-{identity.project_id}'}",
        f"  enabled: {str(identity.livekit.enabled).lower()}",
        f"  session_ttl_minutes: {identity.livekit.session_ttl_minutes}",
        "",
        "# ── Moss Local Retrieval Index ────────────────────────────────────────",
        "moss:",
        f"  status: {identity.moss.status}",
        f"  document_count: {identity.moss.document_count}",
        f"  indexed_at: {identity.moss.indexed_at}",
        f"  index_path: {identity.moss.index_path}",
        "",
        "# ── Resource Summary ─────────────────────────────────────────────────",
        "team:",
        "  team_name: Engineering Team",
        f"  members_count: {counts.get('team', 1)}",
        "",
        "architecture:",
        f"  subsystems: {counts.get('architecture', 1)}",
        "  specification_summary: System block architecture and module definitions.",
        "",
        "requirements:",
        f"  total: {counts.get('requirements', 0)}",
        "",
        "components:",
        f"  total_mpns: {counts.get('components', 0)}",
        "",
        "bom:",
        f"  total_line_items: {counts.get('bom', 0)}",
        "",
        "research:",
        f"  indexed_papers: {counts.get('research', 0)}",
        "",
        "documents:",
        f"  total_docs: {counts.get('documents', 0)}",
        "",
        "analysis:",
        f"  reports_count: {counts.get('analysis', 0)}",
        "",
        "tasks:",
        f"  total_tasks: {counts.get('tasks', 0)}",
        "",
        "decisions:",
        f"  recorded_decisions: {counts.get('decisions', 0)}",
        "",
        "agents:",
        f"  configured_agents: {counts.get('agents', 0)}",
        "",
        "history:",
        f"  recorded_events: {counts.get('history', 0)}",
        "",
        "filesystem:",
        "  root: .",
        "  manifest: .wl/manifest.wl",
        "  entry: README.wl",
        "  data_modules: requirements/, architecture/, components/, bom/, research/, documents/, analysis/, decisions/, tasks/, team/, agents/, history/",
        "",
    ]
    return "\n".join(doc)
