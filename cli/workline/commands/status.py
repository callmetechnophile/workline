"""Implementation of `wg status` — quick project and stack status summary."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def status_command(
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """Show current project and WORKLINE stack status."""
    console.print("\n[bold white]WORKLINE Status[/bold white]\n")

    target = Path(path).resolve() if path else Path.cwd()

    # Project
    from cli.workline.project.filesystem import find_project_root
    root = find_project_root(target)

    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("Key", style="bold", no_wrap=True)
    table.add_column("Value")

    if root:
        readme_file = root / "README.wl"
        project_name = root.name
        project_id = "—"
        project_version = "—"
        if readme_file.exists():
            try:
                from cli.workline.project.readme import parse_readme_wl
                identity = parse_readme_wl(readme_file)
                project_name = identity.name
                project_id = identity.project_id
                project_version = identity.version
            except Exception:
                pass
        table.add_row("Project", f"[green]{project_name}[/green]")
        table.add_row("ID", project_id)
        table.add_row("Version", project_version)
        table.add_row("Root", str(root))
    else:
        table.add_row("Project", "[yellow]No project found[/yellow]")

    # Stack services
    services = {
        "API": ("http://localhost:8000/health", 8000),
        "SurrealDB": ("http://localhost:8001/health", 8001),
        "Qdrant": ("http://localhost:6333/livez", 6333),
        "Redis": (None, 6379),
    }

    table.add_row("", "")
    for svc_name, (url, port) in services.items():
        running = _check_service(url, port)
        status_str = "[green]running[/green]" if running else "[dim]stopped[/dim]"
        table.add_row(svc_name, status_str)

    # Moss index
    if root:
        moss_file = root / ".wl" / "moss.wl"
        if moss_file.exists():
            try:
                import yaml
                data = yaml.safe_load(moss_file.read_text(encoding="utf-8")) or {}
                mc = data.get("moss", {})
                status = mc.get("status", "UNKNOWN")
                count = mc.get("document_count", 0)
                s_color = "green" if status == "READY" else "yellow"
                table.add_row("", "")
                table.add_row("Moss index", f"[{s_color}]{status}[/{s_color}] ({count:,} records)")
            except Exception:
                pass
        else:
            table.add_row("", "")
            table.add_row("Moss index", "[yellow]not indexed[/yellow]")

    console.print(table)

    # Hint
    if root:
        console.print("[dim]Run [bold]wg open[/bold] to open this project in WORKLINE.[/dim]\n")
    else:
        console.print("[dim]Run [bold]wg init <name>[/bold] or [bold]wg new[/bold] to create a project.[/dim]\n")


def _check_service(url: Optional[str], port: int) -> bool:
    import socket
    try:
        with socket.create_connection(("localhost", port), timeout=1.5):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False
