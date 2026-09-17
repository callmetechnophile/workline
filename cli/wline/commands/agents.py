"""
wline agents - Unified agent registry, inspection, capabilities, and health commands.

All data is sourced from the Authoritative Agent Registry; no agent class
is imported directly by this file.
"""

import re
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cli.wline.core.errors import exit_with_error, print_json_output, ExitCode

agents_app = typer.Typer(
    name="agents",
    help="List, inspect, and health-check the 27 internal WORKLINE domain agents.",
)
console = Console()


def _registry():
    """Lazy import to keep startup fast."""
    from armourflow.registry.registry import get_agent_registry
    return get_agent_registry()


def normalize_agent_id(raw_id: str) -> str:
    """
    Normalize various agent ID forms:
      '1' -> 'agent.01'
      '14' -> 'agent.14'
      '#14' -> 'agent.14'
      'agent.14' -> 'agent.14'
      'Agent #14' -> 'agent.14'
    """
    clean = raw_id.strip()
    match = re.match(r"^(?:agent\s*\.?\s*#?|#)?(\d+)$", clean, re.IGNORECASE)
    if match:
        num = int(match.group(1))
        return f"agent.{num:02d}"
    return clean.lower()


def get_agent_index(agent_id: str) -> Optional[int]:
    """Extract integer 1-27 from agent_id if possible."""
    match = re.search(r"(\d+)", agent_id)
    if match:
        return int(match.group(1))
    return None


@agents_app.command("list")
def agents_list(
    json_output: bool = typer.Option(False, "--json", help="Output agents list as pure JSON"),
):
    """
    List all 27 internal WORKLINE domain engineering agents individually.
    Never collapses or omits agents.
    """
    reg = _registry()
    agents = sorted(reg.list_agents(), key=lambda a: get_agent_index(a.agent_id) or 999)

    # Determine status for each agent
    agent_rows = []
    for a in agents:
        h = reg.check_health(a.agent_id)
        # Status mapping: if importable -> READY, otherwise DEGRADED/UNKNOWN
        if h.get("status") == "HEALTHY":
            status = "READY"
        elif h.get("status") == "DEGRADED":
            status = "DEGRADED"
        else:
            status = "UNKNOWN"

        idx = get_agent_index(a.agent_id)
        id_display = f"#{idx:02d}" if idx is not None else a.agent_id

        agent_rows.append({
            "id": a.agent_id,
            "number": idx,
            "display_id": id_display,
            "name": a.name,
            "version": a.version,
            "status": status,
            "execution_level": a.execution_level,
            "capabilities": a.capabilities,
            "dependencies": a.dependencies,
        })

    if json_output:
        print_json_output({"agents": agent_rows, "total": len(agent_rows)})
        return

    table = Table(
        title="WORKLINE INTERNAL AGENTS",
        border_style="cyan",
        header_style="bold cyan",
    )
    table.add_column("ID", style="bold cyan", no_wrap=True)
    table.add_column("Agent Name", style="bold white")
    table.add_column("Status", justify="center")
    table.add_column("Level", style="magenta")
    table.add_column("Capabilities", style="dim")

    for r in agent_rows:
        color = "green" if r["status"] == "READY" else ("yellow" if r["status"] == "DEGRADED" else "red")
        caps = ", ".join(r["capabilities"][:3])
        if len(r["capabilities"]) > 3:
            caps += f" (+{len(r['capabilities']) - 3})"
        table.add_row(r["display_id"], r["name"], f"[{color}]{r['status']}[/]", r["execution_level"], caps)

    console.print(table)


@agents_app.command("info")
@agents_app.command("inspect", hidden=True)
def agents_info(
    agent_id: str = typer.Argument(..., help="Agent ID (e.g. 14, '#14', 'agent.14') or name"),
    json_output: bool = typer.Option(False, "--json", help="Output agent info as pure JSON"),
):
    """Show comprehensive metadata for a specific internal agent."""
    canonical_id = normalize_agent_id(agent_id)
    reg = _registry()
    a = reg.get_agent(canonical_id)
    if not a:
        a = reg.get_agent(agent_id)

    if not a:
        exit_with_error(
            f"Agent '{agent_id}' does not exist. Valid agent IDs: 1-27.",
            code=ExitCode.INVALID_ARGUMENTS,
            json_mode=json_output,
        )

    h = reg.check_health(a.agent_id)
    status = "READY" if h.get("status") == "HEALTHY" else ("DEGRADED" if h.get("status") == "DEGRADED" else "UNKNOWN")

    info_data = {
        "id": a.agent_id,
        "legacy_alias": a.alias_id,
        "name": a.name,
        "version": a.version,
        "status": status,
        "execution_level": a.execution_level,
        "entrypoint": a.entrypoint,
        "description": a.description,
        "dependencies": a.dependencies,
        "permissions": a.permissions,
        "capabilities": a.capabilities,
    }

    if json_output:
        print_json_output(info_data)
        return

    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold cyan", justify="right")
    grid.add_column(style="white")

    grid.add_row("Agent ID:", a.agent_id)
    if a.alias_id:
        grid.add_row("Legacy Alias:", a.alias_id)
    grid.add_row("Name:", a.name)
    grid.add_row("Status:", f"[green]{status}[/]" if status == "READY" else f"[yellow]{status}[/]")
    grid.add_row("Version:", a.version)
    grid.add_row("Execution Level:", a.execution_level)
    grid.add_row("Entrypoint:", a.entrypoint)
    grid.add_row("Description:", a.description)
    grid.add_row("Dependencies:", ", ".join(a.dependencies) if a.dependencies else "None")
    grid.add_row("Permissions:", ", ".join(a.permissions) if a.permissions else "None")
    grid.add_row("Capabilities:", ", ".join(a.capabilities))

    console.print(Panel(grid, title=f"[bold green]Agent Manifest: {a.name}[/]", border_style="cyan"))


@agents_app.command("capabilities")
def agents_capabilities(
    agent_id: Optional[str] = typer.Argument(None, help="Specific agent ID (e.g. 18, 'agent.18')"),
    json_output: bool = typer.Option(False, "--json", help="Output capabilities as pure JSON"),
):
    """List capabilities for an agent or across all registered agents."""
    reg = _registry()

    if agent_id:
        canonical_id = normalize_agent_id(agent_id)
        a = reg.get_agent(canonical_id)
        if not a:
            a = reg.get_agent(agent_id)
        if not a:
            exit_with_error(
                f"Agent '{agent_id}' does not exist. Valid agent IDs: 1-27.",
                code=ExitCode.INVALID_ARGUMENTS,
                json_mode=json_output,
            )

        if json_output:
            print_json_output({
                "agent_id": a.agent_id,
                "name": a.name,
                "capabilities": a.capabilities,
            })
            return

        table = Table(title=f"Capabilities for {a.name} ({a.agent_id})", border_style="cyan")
        table.add_column("Capability", style="bold cyan")
        for cap in a.capabilities:
            table.add_row(cap)
        console.print(table)
        return

    # Platform-wide capabilities
    caps = reg.get_all_capabilities()
    if json_output:
        all_mapping = {}
        for cap in caps:
            providing = reg.find_by_capability(cap)
            all_mapping[cap] = [p.agent_id for p in providing]
        print_json_output({"capabilities": all_mapping, "total": len(caps)})
        return

    table = Table(title=f"WORKLINE Capabilities ({len(caps)} indexed)", border_style="cyan")
    table.add_column("Capability", style="bold cyan")
    table.add_column("Providing Agents", style="white")

    for cap in sorted(caps):
        providing = reg.find_by_capability(cap)
        names = ", ".join(p.agent_id for p in providing)
        table.add_row(cap, names)

    console.print(table)


@agents_app.command("health")
def agents_health(
    json_output: bool = typer.Option(False, "--json", help="Output health as pure JSON"),
):
    """
    Show live health and readiness of all 27 internal WORKLINE agents.
    Uses real checks without fake states.
    """
    reg = _registry()
    agents = sorted(reg.list_agents(), key=lambda a: get_agent_index(a.agent_id) or 999)

    results = []
    for a in agents:
        h = reg.check_health(a.agent_id)
        importable = h.get("importable", False)
        status = "READY" if importable else "DEGRADED"

        idx = get_agent_index(a.agent_id)
        id_display = f"#{idx:02d}" if idx is not None else a.agent_id

        results.append({
            "agent_id": a.agent_id,
            "display_id": id_display,
            "name": a.name,
            "status": status,
            "importable": importable,
            "error": h.get("error"),
        })

    if json_output:
        print_json_output({"agent_health": results})
        return

    table = Table(title="Agent Live Health Status", border_style="cyan")
    table.add_column("ID", style="bold cyan")
    table.add_column("Name", style="bold white")
    table.add_column("Status", justify="center")
    table.add_column("Importable", justify="center")
    table.add_column("Detail", style="dim")

    for r in results:
        color = "green" if r["status"] == "READY" else "red"
        err = r.get("error") or ""
        err_display = (err[:50] + "...") if len(err) > 50 else err
        table.add_row(
            r["display_id"],
            r["name"],
            f"[{color}]{r['status']}[/]",
            "[green]YES[/]" if r["importable"] else "[red]NO[/]",
            err_display,
        )

    console.print(table)
