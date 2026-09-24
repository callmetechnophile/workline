"""Implementation of `wg backup` — export project to a portable .wlipjt archive."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def backup_command(
    path: Optional[str] = typer.Argument(None, help="Project path (defaults to current directory)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file or directory"),
    include_git: bool = typer.Option(False, "--git", help="Include git history bundle"),
    include_vectors: bool = typer.Option(False, "--vectors", help="Include Qdrant vector data"),
    include_artifacts: bool = typer.Option(True, "--artifacts/--no-artifacts", help="Include project artifacts"),
    force: bool = typer.Option(False, "--force", help="Export even if validation has warnings"),
) -> None:
    """Export the current project to a portable .wlipjt archive."""
    console.print("\n[bold white]WORKLINE Backup[/bold white]\n")

    target = Path(path).resolve() if path else Path.cwd()

    # Discover project root
    from cli.workline.project.filesystem import find_project_root
    root = find_project_root(target)
    if not root:
        console.print(f"[red]Error:[/red] No WORKLINE project found at '{target}'")
        raise typer.Exit(code=1)

    console.print(f"[bold]Project:[/bold] {root.name}")
    console.print(f"[bold]Path:[/bold]    {root}")

    # Determine output path
    out_path: Optional[Path] = None
    if output:
        out_path = Path(output).resolve()
        if out_path.is_dir():
            out_path = None  # Let ExportService name it inside that dir

    # Try the full backend ExportService first
    try:
        from backend.workline.project.export_service import ExportService
        from backend.workline.project.models import ExportOptions

        opts = ExportOptions(
            include_git_history=include_git,
            include_vectors=include_vectors,
            include_artifacts=include_artifacts,
            force=force,
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[dim]{task.description}[/dim]"),
            transient=True,
            console=console,
        ) as progress:
            progress.add_task("Exporting project...", total=None)
            svc = ExportService()
            pkg_path, manifest, warnings = svc.export_project(
                project_path=root,
                output_file=out_path,
                options=opts,
            )

        if warnings:
            for w in warnings:
                console.print(f"[yellow]⚠[/yellow] {w}")

        size_mb = pkg_path.stat().st_size / (1024 * 1024)
        console.print(f"\n[bold green]✓[/bold green] Backup created: [bold]{pkg_path.name}[/bold]")
        console.print(f"   Location:   {pkg_path}")
        console.print(f"   Size:       {size_mb:.2f} MB")
        console.print(f"   Components: {manifest.components_count}")
        console.print(f"   BOM items:  {manifest.bom_count}")
        console.print(f"   Artifacts:  {manifest.artifacts_count}")

    except ImportError:
        # Fallback: CLI-native zip export
        _fallback_backup(root, out_path)

    console.print()


def _fallback_backup(root: Path, output: Optional[Path]) -> None:
    """Lightweight fallback backup using the CLI-native exporter."""
    console.print("[dim]Backend not available — using local exporter[/dim]")
    try:
        from cli.workline.export.exporter import WLExporter
        exporter = WLExporter(root)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out = output or root.parent / f"{root.name}_{ts}.wlipjt"
        exporter.export_to(out)
        size_mb = out.stat().st_size / (1024 * 1024)
        console.print(f"[bold green]✓[/bold green] Backup created: [bold]{out.name}[/bold] ({size_mb:.2f} MB)")
    except Exception as e:
        console.print(f"[red]Backup failed:[/red] {e}")
        raise typer.Exit(code=1)
