"""Implementation of `wg restore` — restore a project from a .wlipjt archive."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

_STRATEGIES = ["restore", "merge", "new"]


def restore_command(
    package: str = typer.Argument(..., help="Path to the .wlipjt package file"),
    target: Optional[str] = typer.Option(None, "--target", "-t", help="Target directory for restore"),
    strategy: str = typer.Option("restore", "--strategy", "-s", help="Import strategy: restore, merge, new"),
    rebuild_index: Optional[bool] = typer.Option(None, "--rebuild-index/--no-rebuild-index", help="Rebuild Moss/Qdrant index after restore"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts"),
) -> None:
    """Restore a project from a .wlipjt archive."""
    console.print("\n[bold white]WORKLINE Restore[/bold white]\n")

    pkg_path = Path(package).resolve()
    if not pkg_path.exists():
        console.print(f"[red]Error:[/red] Package not found: {pkg_path}")
        raise typer.Exit(code=1)
    if pkg_path.suffix not in (".wlipjt", ".zip"):
        console.print(f"[yellow]Warning:[/yellow] Unexpected file extension '{pkg_path.suffix}' — expected .wlipjt")

    target_dir = Path(target).resolve() if target else Path.cwd()

    if strategy not in _STRATEGIES:
        console.print(f"[red]Error:[/red] Unknown strategy '{strategy}'. Use: {', '.join(_STRATEGIES)}")
        raise typer.Exit(code=1)

    # Step 1: Verify package integrity
    console.print("[dim]Step 1/4: Verifying package integrity...[/dim]")
    try:
        from backend.workline.project.inspector import PackageInspector
        is_valid, errors = PackageInspector.verify(pkg_path)
        if not is_valid:
            console.print("[red]✗[/red] Package verification failed:")
            for e in errors:
                console.print(f"  [red]•[/red] {e}")
            if not yes:
                proceed = Confirm.ask("Continue anyway?")
                if not proceed:
                    raise typer.Exit()
        else:
            console.print("[bold green]✓[/bold green] Package integrity verified")

        manifest = PackageInspector.read_manifest(pkg_path)
        console.print(f"  Project:  {manifest.project_name} ({manifest.project_id})")
        console.print(f"  Version:  {manifest.project_version}")
        console.print(f"  Exported: {manifest.exported_at}")
    except ImportError:
        console.print("[yellow]⚠[/yellow] Backend not available — skipping full verification")
        _basic_verify(pkg_path)
        manifest = None

    # Step 2: Import
    console.print("\n[dim]Step 2/4: Restoring project...[/dim]")
    try:
        from backend.workline.project.import_service import ImportService
        from backend.workline.project.models import ImportStrategy

        strategy_map = {
            "restore": ImportStrategy.RESTORE,
            "merge": ImportStrategy.MERGE,
            "new": ImportStrategy.NEW_PROJECT,
        }

        with Progress(
            SpinnerColumn(),
            TextColumn("[dim]{task.description}[/dim]"),
            transient=True,
            console=console,
        ) as progress:
            progress.add_task("Importing project data...", total=None)
            svc = ImportService()
            result = svc.import_project(
                package_path=pkg_path,
                target_directory=target_dir,
                strategy=strategy_map[strategy],
            )

        project_dir = Path(result.get("project_path", target_dir))
        console.print(f"[bold green]✓[/bold green] Project restored to: {project_dir}")

    except ImportError:
        # Fallback: extract zip
        project_dir = _fallback_restore(pkg_path, target_dir)

    # Step 3: Check for missing Qdrant/Moss
    console.print("\n[dim]Step 3/4: Checking local index status...[/dim]")
    qdrant_available = _check_qdrant()
    moss_available = _check_moss(project_dir)

    if not qdrant_available:
        console.print("[yellow]⚠[/yellow] Qdrant is not running — vector index not available")
        console.print("  Run [bold]wg start[/bold] to start the local stack, then open WORKLINE to re-index.")
    if not moss_available:
        console.print("[yellow]⚠[/yellow] Moss index not found — project will use filesystem fallback until indexed")

    # Step 4: Offer to rebuild index
    console.print("\n[dim]Step 4/4: Index rebuild[/dim]")
    should_rebuild = rebuild_index
    if should_rebuild is None and (not qdrant_available or not moss_available):
        if not yes:
            should_rebuild = Confirm.ask(
                "Rebuild local Moss retrieval index now?",
                default=False,
            )
        else:
            should_rebuild = False

    if should_rebuild and project_dir.exists():
        _rebuild_index(project_dir)
    elif should_rebuild:
        console.print("[yellow]⚠[/yellow] Cannot rebuild index — project directory not found")
    else:
        console.print("[dim]Index rebuild skipped. Run [bold]wg open[/bold] to auto-index in WORKLINE.[/dim]")

    console.print(f"\n[bold green]✓[/bold green] Restore complete. Run [bold]wg open {project_dir}[/bold] to start working.\n")


def _basic_verify(pkg_path: Path) -> None:
    import zipfile
    try:
        with zipfile.ZipFile(pkg_path, "r") as zf:
            names = zf.namelist()
        if "manifest.toon" not in names:
            console.print("[yellow]⚠[/yellow] manifest.toon not found in package")
        else:
            console.print("[bold green]✓[/bold green] Basic ZIP structure OK")
    except Exception as e:
        console.print(f"[red]Cannot read package: {e}[/red]")
        raise typer.Exit(code=1)


def _fallback_restore(pkg_path: Path, target_dir: Path) -> Path:
    import zipfile
    console.print("[dim]Backend not available — using basic extraction[/dim]")
    project_dir = target_dir / pkg_path.stem
    project_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(pkg_path, "r") as zf:
        zf.extractall(project_dir)
    console.print(f"[bold green]✓[/bold green] Extracted to: {project_dir}")
    return project_dir


def _check_qdrant() -> bool:
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:6333/livez", timeout=2)
        return True
    except Exception:
        return False


def _check_moss(project_dir: Path) -> bool:
    moss_file = project_dir / ".wl" / "moss.wl"
    if not moss_file.exists():
        return False
    try:
        import yaml
        data = yaml.safe_load(moss_file.read_text(encoding="utf-8")) or {}
        status = data.get("moss", {}).get("status", "UNINITIALIZED")
        return status == "READY"
    except Exception:
        return False


def _rebuild_index(project_dir: Path) -> None:
    """Rebuild the local Moss retrieval index."""
    try:
        from cli.workline.retrieval.indexer import ProjectIndexer
        from cli.workline.retrieval.moss_adapter import LocalMossAdapter
        adapter = LocalMossAdapter(project_dir)
        indexer = ProjectIndexer(project_dir, adapter)
        console.print("[dim]Rebuilding index from project files...[/dim]")
        result = indexer.build_index()
        count = result.get("documents_indexed", 0)
        console.print(f"[bold green]✓[/bold green] Index rebuilt: {count:,} records")
    except Exception as e:
        console.print(f"[yellow]⚠[/yellow] Index rebuild failed: {e}")
        console.print("[dim]  Open WORKLINE to auto-index from the UI.[/dim]")
