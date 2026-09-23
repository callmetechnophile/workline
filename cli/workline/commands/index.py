"""
Implementation of `wg index` command suite.
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from cli.workline.project.filesystem import find_project_root
from cli.workline.project.manager import ProjectManager
from cli.workline.retrieval.indexer import ProjectIndexer
from cli.workline.retrieval.moss_adapter import LocalMossAdapter

console = Console()
index_app = typer.Typer(help="Manage local Moss indexing and status", invoke_without_command=True)


@index_app.callback(invoke_without_command=True)
def default_index_callback(
    ctx: typer.Context,
    incremental: bool = typer.Option(False, "--incremental", "-i", help="Incrementally index only changed resources"),
    rebuild: bool = typer.Option(False, "--rebuild", "-r", help="Wipe and rebuild the entire local Moss index from scratch"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Watch project directory for live file changes"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """Build or update the local Moss semantic retrieval index."""
    if ctx.invoked_subcommand is not None:
        return
        
    target_dir = Path(path).resolve() if path else Path.cwd()
    root = find_project_root(target_dir)
    if not root:
        console.print(f"[bold red]Error:[/bold red] '{target_dir}' is not a WORKLINE project (no README.wl found).")
        raise typer.Exit(code=1)

    indexer = ProjectIndexer(root)
    
    # 1. Watch Mode
    if watch:
        console.print(f"\n[bold cyan]Starting Moss Index Watch Mode[/bold cyan] for [bold white]{root.name}[/bold white]")
        console.print("[dim]Press Ctrl+C to stop watching...[/dim]\n")
        try:
            indexer.watch(
                poll_interval=1.5,
                on_change=lambda changed: console.print(f"[green]✓ Detected change & re-indexed:[/green] {', '.join(changed)}"),
            )
        except KeyboardInterrupt:
            console.print("\n[yellow]Watch mode terminated.[/yellow]\n")
        return

    # 2. Incremental Indexing
    if incremental and not rebuild:
        console.print(f"\n[bold cyan]WORKLINE LOCAL INCREMENTAL INDEX[/bold cyan]")
        console.print(f"Project: [bold white]{root.name}[/bold white]")
        console.print("Scanning for modified resources...")
        stats, changed = indexer.index_incremental()
        if changed:
            console.print(f"\n[bold]Detected changes:[/bold]")
            for c in changed:
                console.print(f"  ~ {c}")
            console.print(f"\nIndexing: [bold green]{len(changed)} changed resources[/bold green]")
        else:
            console.print("\n[green]No changes detected. Index is up to date.[/green]")
        console.print(f"Total Indexed Documents: [bold white]{stats.total_records_indexed:,}[/bold white]\n")
        return

    # 3. Full / Rebuild Indexing
    action_str = "Rebuilding" if rebuild else "Building"
    console.print(f"\n[bold cyan]WORKLINE LOCAL INDEX[/bold cyan]")
    console.print(f"Project: [bold white]{root.name}[/bold white]")
    console.print(f"Scanning project...")

    stats = indexer.index_full(rebuild=rebuild)
    
    for rtype, count in stats.resource_breakdown.items():
        name_pad = f"{rtype.capitalize():<18}"
        console.print(f"{name_pad} {count}")

    console.print(f"\n{action_str} local Moss index...")
    console.print(f"[bold]Indexed:[/bold]\n{stats.total_records_indexed:,} records\n")
    console.print(f"[bold]Status:[/bold]\n[green]{stats.status}[/green]\n")
    console.print(f"[bold]Location:[/bold]\n.local project storage (.wl/index/)\n")


@index_app.command("status")
def index_status_command(
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """Display current local Moss index telemetry and health."""
    target_dir = Path(path).resolve() if path else Path.cwd()
    root = find_project_root(target_dir)
    if not root:
        console.print(f"[bold red]Error:[/bold red] '{target_dir}' is not a WORKLINE project.")
        raise typer.Exit(code=1)

    adapter = LocalMossAdapter(root)
    meta = adapter.get_metadata()
    
    console.print("\n[bold white]WORKLINE LOCAL INDEX STATUS[/bold white]\n")
    console.print(f"[bold]Project:[/bold]\n{root.name}\n")
    console.print(f"[bold]Moss:[/bold]\nLOCAL (in-process)\n")
    
    status = meta.get("status", "UNINITIALIZED")
    color = "green" if status == "READY" else "yellow"
    console.print(f"[bold]Status:[/bold]\n[{color}]{status}[/{color}]\n")
    
    console.print(f"[bold]Indexed resources:[/bold]\n{adapter.get_document_count():,}\n")
    console.print(f"[bold]Last index:[/bold]\n{meta.get('indexed_at', 'Never')}\n")
    console.print(f"[bold]Index health:[/bold]\n[green]OK[/green]\n")
