"""
Parser and generator for README.wl - the primary project entry point.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import yaml


@dataclass
class ProjectIdentity:
    """Project identity and high-level summary from README.wl."""
    name: str
    project_id: str
    version: str = "1.0"
    status: str = "ACTIVE"
    domain: str = "Hardware Systems & Engineering"
    description: str = ""
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_workline_version: str = "1.0.0"
    schema_version: str = "1.0"
    raw_data: Dict[str, Any] = field(default_factory=dict)


def parse_readme_wl(readme_path: Path) -> ProjectIdentity:
    """
    Parse a README.wl file into a ProjectIdentity instance.
    Handles standard WORKLINE_PROJECT header and structured YAML fields.
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
            # When we hit our first key: line, we stop skipping
            if ":" in stripped:
                skip_header = False
                clean_lines.append(line)
        else:
            clean_lines.append(line)
            
    parsed_yaml = yaml.safe_load("\n".join(clean_lines)) or {}
    
    return ProjectIdentity(
        name=str(parsed_yaml.get("name", "Untitled Project")),
        project_id=str(parsed_yaml.get("project_id", "PROJ-DEFAULT")),
        version=str(parsed_yaml.get("version", "1.0")),
        status=str(parsed_yaml.get("status", "ACTIVE")),
        domain=str(parsed_yaml.get("domain", "Hardware Systems & Engineering")),
        description=str(parsed_yaml.get("description", "")),
        generated_at=str(parsed_yaml.get("generated_at", datetime.now(timezone.utc).isoformat())),
        source_workline_version=str(parsed_yaml.get("source_workline_version", "1.0.0")),
        schema_version=str(parsed_yaml.get("schema_version", "1.0")),
        raw_data=parsed_yaml,
    )


def generate_readme_wl(
    identity: ProjectIdentity,
    resource_counts: Optional[Dict[str, int]] = None,
) -> str:
    """Generate canonical README.wl file content according to standard specification."""
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
