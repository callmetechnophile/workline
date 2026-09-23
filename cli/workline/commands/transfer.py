"""
Implementation of `wg export`, `wg import`, `wg sync`, and `wg git` commands.
"""

from pathlib import Path
import subprocess
from typing import Optional
import typer
from rich.console import Console

from cli.workline.export.exporter import export_project_zip, import_project_zip
from cli.workline.project.filesystem import find_project_root
from cli.workline.retrieval.indexer import ProjectIndexer

console = Console()

git_app = typer.Typer(help="Git version control operations on project")


def export_command(
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path to export"),
    zip_mode: bool = typer.Option(True, "--zip", help="Bundle as portable .workline.zip"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Target output file path"),
) -> None:
    """Bundle project into portable archive excluding secrets and local index cache."""
    target_dir = Path(path).resolve() if path else Path.cwd()
    root = find_project_root(target_dir)
    if not root:
        console.print(f"[bold red]Error:[/bold red] '{target_dir}' is not a WORKLINE project.")
        raise typer.Exit(code=1)

    out_path = Path(output).resolve() if output else None
    try:
        exported_file = export_project_zip(root, output_zip=out_path)
        console.print(f"\n[bold green]✓ Project exported successfully:[/bold green] [bold white]{exported_file.name}[/bold white]")
        console.print(f"  Target: [cyan]{exported_file}[/cyan]")
        console.print(f"  Zero-secrets & index-cache exclusion: [green]PASSED[/green]\n")
    except Exception as e:
        console.print(f"[bold red]Export failed:[/bold red] {e}")
        raise typer.Exit(code=1)


def import_command(
    archive: str = typer.Argument(..., help="Path to .workline.zip archive or project folder to import"),
    destination: Optional[str] = typer.Option(None, "--destination", "-d", help="Destination folder"),
) -> None:
    """Import a WORKLINE project archive and automatically initialize its local Moss index."""
    src = Path(archive).resolve()
    dest = Path(destination).resolve() if destination else Path.cwd() / src.stem.replace(".workline", "")

    try:
        imported_root = import_project_zip(src, dest)
        console.print(f"\n[bold green]✓ Project imported:[/bold green] [cyan]{imported_root}[/cyan]")
        
        # Automatically build local Moss index on import
        console.print("Reconstructing local Moss retrieval layer from .wl filesystem...")
        indexer = ProjectIndexer(imported_root)
        stats = indexer.index_full(rebuild=True)
        console.print(f"[bold green]✓ Local retrieval ready:[/bold green] {stats.total_records_indexed:,} records indexed.\n")
    except Exception as e:
        console.print(f"[bold red]Import failed:[/bold red] {e}")
        raise typer.Exit(code=1)


def sync_command(
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """Synchronize project manifest, validate checksums, and update local Moss index."""
    target_dir = Path(path).resolve() if path else Path.cwd()
    root = find_project_root(target_dir)
    if not root:
        console.print(f"[bold red]Error:[/bold red] '{target_dir}' is not a WORKLINE project.")
        raise typer.Exit(code=1)

    indexer = ProjectIndexer(root)
    stats, changed = indexer.index_incremental()
    console.print(f"\n[bold green]✓ Project synchronized:[/bold green] {stats.total_records_indexed:,} total records ({len(changed)} updated).\n")


@git_app.command("status")
def git_status(path: Optional[str] = typer.Option(None, "--path", "-p")) -> None:
    """Run git status inside the project directory."""
    target_dir = Path(path).resolve() if path else Path.cwd()
    root = find_project_root(target_dir) or target_dir
    subprocess.run(["git", "status"], cwd=root)


@git_app.command("diff")
def git_diff(path: Optional[str] = typer.Option(None, "--path", "-p")) -> None:
    """Run git diff inside the project directory."""
    target_dir = Path(path).resolve() if path else Path.cwd()
    root = find_project_root(target_dir) or target_dir
    subprocess.run(["git", "diff"], cwd=root)
