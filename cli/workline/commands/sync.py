"""Implementation of `wg sync` — sync .wl state from live WORKLINE API."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

_API_BASE = "http://localhost:8000"


def sync_command(
    project_id: Optional[str] = typer.Argument(None, help="Project ID to sync (auto-detected if omitted)"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
    api_url: str = typer.Option(_API_BASE, "--api", help="WORKLINE API base URL"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be synced without writing"),
) -> None:
    """Sync .wl project state from the live WORKLINE API."""
    console.print("\n[bold white]WORKLINE Sync[/bold white]\n")

    target = Path(path).resolve() if path else Path.cwd()

    # Find project
    from cli.workline.project.filesystem import find_project_root
    root = find_project_root(target)
    if not root:
        console.print(f"[red]Error:[/red] No WORKLINE project found at '{target}'")
        raise typer.Exit(code=1)

    # Determine project ID
    pid = project_id
    if not pid:
        readme_file = root / "README.wl"
        if readme_file.exists():
            try:
                from cli.workline.project.readme import parse_readme_wl
                pid = parse_readme_wl(readme_file).project_id
            except Exception:
                pass

    if not pid:
        console.print("[red]Error:[/red] Could not determine project ID. Pass it explicitly: wg sync <project_id>")
        raise typer.Exit(code=1)

    console.print(f"[bold]Project:[/bold] {root.name} ([dim]{pid}[/dim])")
    console.print(f"[bold]API:[/bold]     {api_url}")

    # Check API is reachable
    try:
        import urllib.request
        urllib.request.urlopen(f"{api_url}/health", timeout=3)
    except Exception:
        console.print(f"[red]Error:[/red] WORKLINE API is not reachable at {api_url}")
        console.print("[dim]  Run [bold]wg start[/bold] to start the local stack.[/dim]")
        raise typer.Exit(code=1)

    # Call the export-wl endpoint to pull .wl filemap
    export_url = f"{api_url}/api/project/data/export-wl"
    console.print(f"[dim]Pulling project state from {export_url}...[/dim]")

    try:
        import json
        import urllib.request

        req = urllib.request.Request(
            export_url,
            method="POST",
            data=json.dumps({"project_id": pid}).encode(),
            headers={"Content-Type": "application/json", "X-Dev-Auth": "true"},
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[dim]{task.description}[/dim]"),
            transient=True,
            console=console,
        ) as progress:
            progress.add_task("Syncing project state...", total=None)
            with urllib.request.urlopen(req, timeout=30) as resp:
                filemap = json.loads(resp.read().decode())

        files_written = 0
        for rel_path, content in filemap.items():
            abs_path = root / rel_path
            if dry_run:
                console.print(f"  [dim]would write:[/dim] {rel_path}")
            else:
                abs_path.parent.mkdir(parents=True, exist_ok=True)
                abs_path.write_text(content, encoding="utf-8")
                files_written += 1

        if dry_run:
            console.print(f"\n[dim]Dry run: {len(filemap)} files would be updated[/dim]")
        else:
            console.print(f"\n[bold green]✓[/bold green] Synced {files_written} files to {root.name}")

    except Exception as e:
        console.print(f"[red]Sync failed:[/red] {e}")
        console.print("[dim]Ensure WORKLINE is running and the project exists.[/dim]")
        raise typer.Exit(code=1)

    console.print()
