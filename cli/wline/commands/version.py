"""Project versioning, deterministic snapshotting, and release commands."""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel

from backend.workline.git.repository import project_repo_manager
from backend.workline.git.service import git_service
from cli.wline import __version__ as CLI_VERSION
from cli.wline.core.paths import get_active_project_name, get_workspace_dir
from cli.wline.core.workspace import find_project

console = Console()


def _resolve_project_dir(project_name: Optional[str] = None) -> Optional[Path]:
    """Resolve project directory if one is active or provided."""
    target = project_name if isinstance(project_name, str) and project_name.strip() else get_active_project_name()
    if target:
        found = find_project(target)
        if found:
            return found[0]
        ws_p = get_workspace_dir() / target
        if ws_p.exists():
            return ws_p

    # Check cwd
    cwd = Path.cwd().resolve()
    if git_service.is_repository(cwd) or (cwd / ".workline").exists():
        return cwd
    return None


def version_command(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name."),
) -> None:
    """Display comprehensive Workline CLI, active project, Git commit, and schema version."""
    proj_dir = _resolve_project_dir(project)

    project_version = "None"
    schema_version = 1
    git_commit_short = "None"

    if proj_dir:
        manifest = project_repo_manager.load_toon_manifest(proj_dir)
        if manifest:
            project_version = manifest.project_version
            schema_version = manifest.schema_version

        commit_hash = git_service.get_current_commit(proj_dir)
        if commit_hash:
            git_commit_short = commit_hash[:7]

    panel_text = (
        f"[bold]Workline:[/bold] {CLI_VERSION}\n"
        f"[bold]Project:[/bold]  {project_version}\n"
        f"[bold]Git:[/bold]      {git_commit_short}\n"
        f"[bold]Schema:[/bold]   {schema_version}"
    )
    console.print(Panel(panel_text, title="WORKLINE VERSION", border_style="cyan"))


def snapshot_command(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name."),
    export: bool = typer.Option(False, "--export", "-e", help="Export snapshot package (.wlipjt)."),
) -> None:
    """Create a deterministic project state snapshot record linked to the current Git commit."""
    proj_dir = _resolve_project_dir(project)
    if not proj_dir:
        console.print("[bold red][ERROR][/bold red] No active project selected. Open a project first.\n")
        raise typer.Exit(code=1)

    snapshot = project_repo_manager.create_snapshot(proj_dir)
    panel_text = (
        f"[bold]Snapshot ID:[/bold]     [cyan]{snapshot.snapshot_id}[/cyan]\n"
        f"[bold]Project ID:[/bold]      {snapshot.project_id}\n"
        f"[bold]Project Version:[/bold] {snapshot.project_version}\n"
        f"[bold]Git Commit:[/bold]      {snapshot.git_commit[:7]}\n"
        f"[bold]Schema Version:[/bold]  {snapshot.schema_version}\n"
        f"[bold]Timestamp:[/bold]       {snapshot.timestamp[:19].replace('T', ' ')}"
    )
    console.print(Panel(panel_text, title="PROJECT SNAPSHOT CREATED", border_style="green"))

    if export:
        from backend.workline.project.export_service import export_service
        snapshots_dir = proj_dir / "snapshots"
        snapshots_dir.mkdir(parents=True, exist_ok=True)
        pkg_name = f"{snapshot.project_id}-{snapshot.project_version}-{snapshot.git_commit[:7]}.wlipjt"
        target_pkg = snapshots_dir / pkg_name
        pkg_file, _, _ = export_service.export_project(proj_dir, output_file=target_pkg)
        console.print(f"[bold green][PACKAGE][/bold green] Exported snapshot package: [cyan]{pkg_file}[/cyan]\n")
    else:
        console.print()


def release_command(
    version: str = typer.Argument(..., help="Release version number (e.g. 0.3.0 or v0.3.0)."),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name."),
    message: Optional[str] = typer.Option(None, "--message", "-m", help="Release annotation message."),
) -> None:
    """Create a formal project release: bumps version, creates release commit, and tags Git."""
    proj_dir = _resolve_project_dir(project)
    if not proj_dir:
        console.print("[bold red][ERROR][/bold red] No active project selected. Open a project first.\n")
        raise typer.Exit(code=1)

    console.print(f"\n[bold cyan]CREATING PROJECT RELEASE:[/bold cyan] [bold green]v{version.lstrip('v')}[/bold green]\n")

    try:
        rel_info = project_repo_manager.create_release(
            project_path=proj_dir,
            release_version=version,
            tag_message=message,
        )
        panel_text = (
            f"[bold]Project:[/bold]          {rel_info['project_id']}\n"
            f"[bold]Previous Version:[/bold] {rel_info['previous_version']}\n"
            f"[bold]Release Version:[/bold]  [bold green]{rel_info['release_version']}[/bold green]\n"
            f"[bold]Git Tag:[/bold]          [cyan]{rel_info['git_tag']}[/cyan]\n"
            f"[bold]Release Commit:[/bold]   {rel_info['short_hash']}\n"
            f"[bold]Timestamp:[/bold]        {rel_info['timestamp'][:19].replace('T', ' ')}"
        )
        console.print(Panel(panel_text, title=f"RELEASE {rel_info['git_tag']} CREATED", border_style="green"))
        console.print("[dim]Next step: Run 'wline git push --tags' or 'wline github push' to publish tag.[/dim]\n")
    except Exception as exc:
        console.print(f"[bold red][ERROR][/bold red] Release failed: {str(exc)}\n")
        raise typer.Exit(code=1)
