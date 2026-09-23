"""
Implementation of `wg open`, `wg inspect`, and `wg check` commands.
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

from cli.workline.project.manager import ProjectManager

console = Console()


def open_command(
    path: Optional[str] = typer.Argument(None, help="Optional path to WORKLINE project directory"),
) -> None:
    """Detect and open a WORKLINE project."""
    target_dir = Path(path).resolve() if path else Path.cwd()
    mgr = ProjectManager(target_dir)
    
    try:
        root, readme, manifest = mgr.open_project(target_dir)
        console.print(f"\n[bold cyan]WORKLINE PROJECT OPENED[/bold cyan]")
        console.print(f"  Name:        [bold white]{readme.name}[/bold white]")
        console.print(f"  Project ID:  [bold yellow]{readme.project_id}[/bold yellow]")
        console.print(f"  Version:     {readme.version}")
        console.print(f"  Status:      [green]{readme.status}[/green]")
        console.print(f"  Path:        [dim]{root}[/dim]")
        console.print(f"  Description: {readme.description or 'No description'}\n")
    except Exception as e:
        console.print(f"[bold red]Error opening project:[/bold red] {e}")
        raise typer.Exit(code=1)


def inspect_command(
    path: Optional[str] = typer.Argument(None, help="Optional path to WORKLINE project directory"),
) -> None:
    """Inspect project resources, counts, and local Moss index status."""
    target_dir = Path(path).resolve() if path else Path.cwd()
    mgr = ProjectManager(target_dir)
    
    try:
        data = mgr.inspect_project(target_dir)
        readme = data["identity"]
        manifest = data["manifest"]
        res = data["resources"]
        moss = data["moss"]
        
        console.print("\n[bold white]WORKLINE PROJECT[/bold white]\n")
        console.print(f"[bold]Name:[/bold]\n{readme.name}\n")
        console.print(f"[bold]Project ID:[/bold]\n{readme.project_id}\n")
        console.print(f"[bold]Version:[/bold]\n{readme.version}\n")
        console.print(f"[bold]Schema:[/bold]\n{manifest.schema_version}\n")
        
        console.print("[bold]Resources:[/bold]\n")
        console.print(f"Requirements:    {res.get('requirements', 0)}")
        console.print(f"Components:      {res.get('components', 0)}")
        console.print(f"BOM Items:       {res.get('bom', 0)}")
        console.print(f"Research Papers: {res.get('research', 0)}")
        console.print(f"Documents:       {res.get('documents', 0)}")
        console.print(f"Tasks:           {res.get('tasks', 0)}")
        console.print(f"Decisions:       {res.get('decisions', 0)}\n")
        
        console.print("[bold]Moss Index:[/bold]")
        m_status = moss.get("status", "UNINITIALIZED")
        color = "green" if m_status == "READY" else "yellow"
        console.print(f"[{color}]{m_status}[/{color}]\n")
        
        console.print(f"[bold]Indexed Documents:[/bold]\n{moss.get('document_count', 0):,}\n")
        console.print(f"[bold]Last Indexed:[/bold]\n{moss.get('last_indexed', 'Never')}\n")
    except Exception as e:
        console.print(f"[bold red]Error inspecting project:[/bold red] {e}")
        raise typer.Exit(code=1)


def check_command(
    path: Optional[str] = typer.Argument(None, help="Optional path to WORKLINE project directory"),
) -> None:
    """Validate project filesystem structure, manifest hashes, and zero-secrets invariant."""
    target_dir = Path(path).resolve() if path else Path.cwd()
    mgr = ProjectManager(target_dir)
    
    console.print("\n[bold white]WORKLINE PROJECT CHECK[/bold white]\n")
    result = mgr.check_project(target_dir)
    
    for chk in result.checks:
        symbol = "[bold green]✓[/bold green]" if chk.passed else "[bold red]✗[/bold red]"
        console.print(f"{symbol} {chk.name} [dim]{chk.message}[/dim]")
        
    if result.warnings:
        console.print("\n[bold yellow]Warnings:[/bold yellow]")
        for w in result.warnings:
            console.print(f"  ⚠ {w}")
            
    if result.errors:
        console.print("\n[bold red]Errors:[/bold red]")
        for err in result.errors:
            console.print(f"  ✗ {err}")
        console.print("\n[bold red]Project: INVALID[/bold red]\n")
        raise typer.Exit(code=1)
        
    console.print("\n[bold green]Project: VALID[/bold green]\n")
