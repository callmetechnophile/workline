"""
Implementation of `wg init <name>` command.
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from cli.workline.project.manager import ProjectManager

console = Console()


def init_project_command(
    name: str = typer.Argument(..., help="Name of the WORKLINE engineering project to create"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Target directory for project"),
    domain: str = typer.Option("Hardware Systems & Power Engineering", "--domain", "-d", help="Engineering domain"),
    description: str = typer.Option("", "--description", help="Project description"),
) -> None:
    """Initialize a new portable WORKLINE .wl project directory."""
    mgr = ProjectManager()
    target_dir = Path(path).resolve() if path else None
    
    try:
        root = mgr.init_project(
            name=name,
            target_dir=target_dir,
            description=description,
            domain=domain,
        )
        console.print(f"\n[bold green]✓ Initialized WORKLINE project:[/bold green] [bold white]{name}[/bold white]")
        console.print(f"  Location: [cyan]{root}[/cyan]")
        console.print("  Filesystem: [dim]README.wl, .wl/manifest.wl, standard modules[/dim]")
        console.print("\n[dim]Run 'wg open' or 'wg index' inside the project directory to begin.[/dim]\n")
    except Exception as e:
        console.print(f"[bold red]Error initializing project:[/bold red] {e}")
        raise typer.Exit(code=1)
