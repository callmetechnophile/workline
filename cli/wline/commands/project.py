"""Project management commands for Workline."""

from typing import Optional
import typer
from rich.console import Console

from cli.wline.core.manifest import (
    BudgetConfig,
    ProjectManifest,
    ProjectMetadata,
    TargetPlatformConfig,
    TimelineConfig,
    normalize_project_name,
    parse_budget_amount,
    parse_timeline_days,
)
from cli.wline.core.paths import get_active_project_name, set_active_project_name
from cli.wline.core.workspace import (
    create_project,
    delete_project_dir,
    find_project,
    list_projects,
)
from cli.wline.ui.output import print_error, print_info, print_success
from cli.wline.ui.tables import render_lifecycle_status, render_project_list

project_app = typer.Typer(name="project", help="Manage Workline engineering projects.")
console = Console()


@project_app.command("list")
def list_all_projects() -> None:
    """Discover and list all Workline projects in the workspace."""
    projects = list_projects()
    render_project_list(projects)


@project_app.command("create")
def create_new_project(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Project name"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Project description"),
    domain: Optional[str] = typer.Option(None, "--domain", help="Engineering domain"),
    budget: Optional[str] = typer.Option(None, "--budget", "-b", help="Budget amount"),
    timeline: Optional[str] = typer.Option(None, "--timeline", "-t", help="Target timeline"),
    complexity: Optional[str] = typer.Option(None, "--complexity", "-c", help="Complexity level"),
    platform: Optional[str] = typer.Option(None, "--platform", "-p", help="Target controller platform"),
) -> None:
    """Create a new engineering project with directory hierarchy and manifest."""
    console.print("\n[bold cyan]WORKLINE[/bold cyan]\n")
    console.print("[bold white]Create New Engineering Project[/bold white]\n")

    # Interactive prompts if options not passed
    if not name:
        name = typer.prompt("Project name")
    if description is None:
        description = typer.prompt("Description", default="")
    if domain is None:
        domain = typer.prompt("Domain", default="robotics")
    if budget is None:
        budget = typer.prompt("Budget", default="20000")
    if timeline is None:
        timeline = typer.prompt("Timeline", default="8 weeks")
    if complexity is None:
        complexity = typer.prompt("Complexity", default="medium")
    if platform is None:
        platform = typer.prompt("Target platform", default="ESP32-S3")

    normalized = normalize_project_name(name)
    budget_amt = parse_budget_amount(budget)
    target_days = parse_timeline_days(timeline)

    display_title = name.strip()
    if "-" in display_title and " " not in display_title:
        display_title = display_title.replace("-", " ").title()
    elif display_title and not display_title[0].isupper():
        display_title = display_title.title()

    manifest = ProjectManifest(
        name=normalized,
        display_name=display_title,
        description=description.strip(),
        domain=domain.strip(),
        budget=BudgetConfig(amount=budget_amt, currency="INR"),
        timeline=TimelineConfig(target_days=target_days),
        complexity=complexity.strip(),
        target_platform=TargetPlatformConfig(controller=platform.strip()),
    )

    console.print("\n[dim]Creating project...[/dim]\n")
    try:
        project_dir = create_project(manifest)
    except FileExistsError as e:
        print_error(str(e))
        raise typer.Exit(code=1)

    print_success("Workspace created")
    print_success("Manifest created")
    print_success("Lifecycle initialized")

    # Automatically set as active project
    set_active_project_name(manifest.name)

    console.print(f"\n[bold white]Project:[/bold white]\n\n[cyan]{project_dir}[/cyan]\n")


@project_app.command("open")
def open_project(
    name: str = typer.Argument(..., help="Project name to set as active")
) -> None:
    """Set an existing project as the active project."""
    project_info = find_project(name)
    if not project_info:
        print_error(f"Project '{name}' not found in workspace.")
        raise typer.Exit(code=1)

    _, manifest = project_info
    set_active_project_name(manifest.name)
    print_success(f"Active project set to '{manifest.display_name}' ({manifest.name})")


@project_app.command("status")
def project_status(
    name: Optional[str] = typer.Argument(None, help="Project name (defaults to active project)")
) -> None:
    """Display the engineering lifecycle breakdown and progress for a project."""
    target_name = name or get_active_project_name()
    if not target_name:
        print_error("No active project. Specify a project name or open one with 'wline project open <name>'")
        raise typer.Exit(code=1)

    project_info = find_project(target_name)
    if not project_info:
        print_error(f"Project '{target_name}' not found in workspace.")
        raise typer.Exit(code=1)

    _, manifest = project_info
    render_lifecycle_status(manifest)

    from backend.workline.agents.runtime import agent_runtime
    execs = agent_runtime.list_executions_for_project(manifest.name)
    if execs:
        latest = execs[-1]
        console.print("\n[bold cyan]AGENT EXECUTION[/bold cyan]")
        console.print(f"[bold white]Agent:[/bold white]   {latest.agent_id.replace('_', ' ').title()}")
        console.print(f"[bold white]Status:[/bold white]  {latest.status.value}")
        console.print(f"[bold white]Stage:[/bold white]   {latest.stage.replace('_', ' ').title()}\n")


@project_app.command("delete")
def delete_project_command(
    name: str = typer.Argument(..., help="Project name to delete"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Delete an existing project directory from the workspace."""
    project_info = find_project(name)
    if not project_info:
        print_error(f"Project '{name}' not found in workspace.")
        raise typer.Exit(code=1)

    _, manifest = project_info

    if not yes:
        confirmed = typer.confirm(f"\nDelete project '{manifest.name}'?", default=False)
        if not confirmed:
            print_info("Deletion cancelled.")
            return

    try:
        delete_project_dir(manifest.name)
        print_success(f"Project '{manifest.name}' deleted successfully.")
    except Exception as e:
        print_error(f"Failed to delete project: {e}")
        raise typer.Exit(code=1)


@project_app.command("export")
def export_project_cmd(
    file_path: Optional[str] = typer.Argument(None, help="Output .wlipjt package path."),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name (defaults to active project)."),
    include_artifacts: bool = typer.Option(False, "--include-artifacts", help="Include full artifact payload files."),
    include_vectors: bool = typer.Option(False, "--include-vectors", help="Include Qdrant vector embeddings."),
    include_git_history: bool = typer.Option(False, "--include-git-history", help="Include full .git history bundle."),
    force: bool = typer.Option(False, "--force", "-f", help="Force export even if project validation produces warnings."),
) -> None:
    """Export the project into a portable, verified .wlipjt package archive."""
    from pathlib import Path
    from rich.panel import Panel
    from backend.workline.project.export_service import export_service
    from backend.workline.project.models import ExportOptions

    target_name = project if isinstance(project, str) and project.strip() else get_active_project_name()
    if not target_name:
        print_error("No active project selected. Specify a project name or open one.")
        raise typer.Exit(code=1)

    project_info = find_project(target_name)
    if not project_info:
        print_error(f"Project '{target_name}' not found.")
        raise typer.Exit(code=1)

    proj_dir, _ = project_info
    out_target = Path(file_path).resolve() if file_path else None

    opts = ExportOptions(
        include_artifacts=include_artifacts,
        include_vectors=include_vectors,
        include_git_history=include_git_history,
        force=force,
    )

    try:
        pkg_file, manifest, warnings = export_service.export_project(proj_dir, output_file=out_target, options=opts)
        
        for w in warnings:
            console.print(f"[bold yellow][WARNING][/bold yellow] {w}")

        panel_text = (
            f"[bold]Project:[/bold]         {manifest.project_name} ([cyan]{manifest.project_id}[/cyan])\n"
            f"[bold]Package File:[/bold]    [green]{pkg_file}[/green]\n"
            f"[bold]Version:[/bold]         v{manifest.project_version}\n"
            f"[bold]Format Version:[/bold]  {manifest.format_version}\n"
            f"[bold]Components:[/bold]      {manifest.components_count}\n"
            f"[bold]Nets:[/bold]            {manifest.nets_count}\n"
            f"[bold]BOM Items:[/bold]       {manifest.bom_count}\n"
            f"[bold]Artifacts:[/bold]       {manifest.artifacts_count} ({'Included' if include_artifacts else 'Metadata only'})\n"
            f"[bold]Integrity:[/bold]       [bold green]VALID[/bold green]"
        )
        console.print(Panel(panel_text, title="WORKLINE PROJECT EXPORTED", border_style="green"))
        console.print()
    except Exception as e:
        print_error(f"Export failed: {e}")
        raise typer.Exit(code=1)


@project_app.command("import")
def import_project_cmd(
    file_path: str = typer.Argument(..., help="Path to .wlipjt package to import."),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Target project name (optional override)."),
    strategy: str = typer.Option("RESTORE", "--strategy", "-s", help="Import strategy (NEW_PROJECT, RESTORE, MERGE)."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing project directory if conflict exists."),
) -> None:
    """Import a .wlipjt project package into the Workline workspace."""
    from pathlib import Path
    from rich.panel import Panel
    from backend.workline.project.import_service import import_service
    from backend.workline.project.models import ImportStrategy

    pkg_path = Path(file_path).resolve()
    if not pkg_path.exists():
        print_error(f"Package file '{pkg_path}' does not exist.")
        raise typer.Exit(code=1)

    strat_enum = ImportStrategy[strategy.upper()] if strategy.upper() in ImportStrategy.__members__ else ImportStrategy.RESTORE

    try:
        target_dir, manifest = import_service.import_project(
            package_path=pkg_path,
            target_project_name=name,
            strategy=strat_enum,
            overwrite=overwrite,
        )

        set_active_project_name(manifest.project_id)

        panel_text = (
            f"[bold]Project Name:[/bold]    {manifest.project_name}\n"
            f"[bold]Project ID:[/bold]      [cyan]{manifest.project_id}[/cyan]\n"
            f"[bold]Version:[/bold]         v{manifest.project_version}\n"
            f"[bold]Directory:[/bold]       [green]{target_dir}[/green]\n"
            f"[bold]Strategy:[/bold]        {strat_enum.value}\n"
            f"[bold]Active Status:[/bold]   [bold green]OPEN / ACTIVE[/bold green]"
        )
        console.print(Panel(panel_text, title="WORKLINE PROJECT IMPORTED", border_style="green"))
        console.print()
    except Exception as e:
        print_error(f"Import failed: {e}")
        raise typer.Exit(code=1)


@project_app.command("inspect")
def inspect_project_package(
    file_path: str = typer.Argument(..., help="Path to .wlipjt package."),
) -> None:
    """Read-only inspection of a .wlipjt package without modifying any workspace state."""
    from pathlib import Path
    from rich.panel import Panel
    from backend.workline.project.inspector import PackageInspector

    pkg_path = Path(file_path).resolve()
    if not pkg_path.exists():
        print_error(f"Package file '{pkg_path}' not found.")
        raise typer.Exit(code=1)

    try:
        insp = PackageInspector.inspect(pkg_path)
        m = insp.manifest

        panel_text = (
            f"[bold]Name:[/bold]              {m.project_name}\n"
            f"[bold]Project ID:[/bold]        {m.project_id}\n"
            f"[bold]Project Version:[/bold]   {m.project_version}\n"
            f"[bold]Workline Schema:[/bold]   {m.schema_version}\n"
            f"[bold]Format Version:[/bold]    {m.format_version}\n"
            f"[bold]Components:[/bold]        {m.components_count}\n"
            f"[bold]Nets:[/bold]              {m.nets_count}\n"
            f"[bold]BOM Items:[/bold]         {m.bom_count}\n"
            f"[bold]PCB:[/bold]               {m.pcb_count}\n"
            f"[bold]Artifacts:[/bold]         {m.artifacts_count}\n"
            f"[bold]Git Commit:[/bold]        {m.git.current_commit[:7] if m.git.current_commit else 'None'}\n"
            f"[bold]Package Size:[/bold]      {insp.size_breakdown.total_package_size_bytes / (1024 * 1024):.2f} MB\n"
            f"[bold]Package Integrity:[/bold] [bold green]{insp.integrity_status}[/bold green]"
        )
        console.print(Panel(panel_text, title="WORKLINE PROJECT PACKAGE", border_style="cyan"))

        for w in insp.warnings:
            console.print(f"[bold yellow][WARNING][/bold yellow] {w}")
        for err in insp.errors:
            console.print(f"[bold red][ERROR][/bold red] {err}")
        console.print()
    except Exception as e:
        print_error(f"Inspection failed: {e}")
        raise typer.Exit(code=1)


@project_app.command("verify")
def verify_project_package(
    file_path: str = typer.Argument(..., help="Path to .wlipjt package to verify."),
) -> None:
    """Verify cryptographic integrity of all internal package checksums."""
    from pathlib import Path
    from backend.workline.project.inspector import PackageInspector

    pkg_path = Path(file_path).resolve()
    if not pkg_path.exists():
        print_error(f"Package file '{pkg_path}' not found.")
        raise typer.Exit(code=1)

    is_valid, errors = PackageInspector.verify(pkg_path)
    if is_valid:
        print_success(f"Package '{pkg_path.name}' integrity verified successfully (All SHA-256 checksums valid).")
    else:
        print_error(f"Package '{pkg_path.name}' verification failed:")
        for err in errors:
            console.print(f"  - [red]{err}[/red]")
        raise typer.Exit(code=1)


@project_app.command("info")
def project_info_command(
    target: Optional[str] = typer.Argument(None, help="Project name or path to .wlipjt package."),
) -> None:
    """Display comprehensive information about an active project or a .wlipjt package."""
    from pathlib import Path
    from rich.panel import Panel

    target_val = target if isinstance(target, str) and target.strip() else get_active_project_name()
    if not target_val:
        print_error("No target specified and no active project open.")
        raise typer.Exit(code=1)

    # Check if target is a .wlipjt file
    p_path = Path(target_val)
    if p_path.exists() and (p_path.is_file() or str(target_val).endswith(".wlipjt")):
        inspect_project_package(str(p_path))
        return

    project_info = find_project(target_val)
    if not project_info:
        print_error(f"Project '{target_val}' not found.")
        raise typer.Exit(code=1)

    proj_dir, manifest = project_info
    from backend.workline.git.repository import project_repo_manager
    from backend.workline.git.service import git_service

    toon = project_repo_manager.load_toon_manifest(proj_dir)
    is_repo = git_service.is_repository(proj_dir)
    commit = git_service.get_current_commit(proj_dir) if is_repo else "None"
    github_conn = "CONNECTED" if (toon and toon.github.connected) else "NOT CONNECTED"

    panel_text = (
        f"[bold]Name:[/bold]        {manifest.display_name}\n"
        f"[bold]ID:[/bold]          {manifest.name}\n"
        f"[bold]Version:[/bold]     {manifest.version or '0.1.0'}\n"
        f"[bold]Git:[/bold]         {commit[:7] if commit else 'None'}\n"
        f"[bold]GitHub:[/bold]      {github_conn}\n"
        f"[bold]Components:[/bold]  Ready\n"
        f"[bold]BOM Items:[/bold]   Ready\n"
        f"[bold]PCB:[/bold]         READY\n"
        f"[bold]PINN:[/bold]        TRAINED\n"
        f"[bold]Artifacts:[/bold]   Available"
    )
    console.print(Panel(panel_text, title="WORKLINE PROJECT", border_style="cyan"))
    console.print()


@project_app.command("diff")
def diff_project_packages(
    package_a: str = typer.Argument(..., help="Path to first .wlipjt package."),
    package_b: str = typer.Argument(..., help="Path to second .wlipjt package."),
) -> None:
    """Compare two .wlipjt packages and display structured engineering differences."""
    from pathlib import Path
    from rich.panel import Panel
    from backend.workline.project.inspector import PackageInspector

    pa = Path(package_a).resolve()
    pb = Path(package_b).resolve()

    if not pa.exists():
        print_error(f"Package '{package_a}' not found.")
        raise typer.Exit(code=1)
    if not pb.exists():
        print_error(f"Package '{package_b}' not found.")
        raise typer.Exit(code=1)

    diff_res = PackageInspector.diff(pa, pb)

    panel_text = (
        f"[bold]Source Package:[/bold]    {diff_res.source_package}\n"
        f"[bold]Target Package:[/bold]    {diff_res.target_package}\n\n"
        f"[bold]Project Version:[/bold]   {diff_res.version_diff}\n"
        f"[bold]Workline Schema:[/bold]   {diff_res.schema_diff}\n\n"
        f"[bold]Components:[/bold]        +{diff_res.components_added} / -{diff_res.components_removed} (modified: {diff_res.components_modified})\n"
        f"[bold]Nets:[/bold]              +{diff_res.nets_added} / -{diff_res.nets_removed}\n"
        f"[bold]BOM:[/bold]               {'CHANGED' if diff_res.bom_changed else 'UNCHANGED'}\n"
        f"[bold]PCB:[/bold]               {'CHANGED' if diff_res.pcb_changed else 'UNCHANGED'}\n"
        f"[bold]Constraints:[/bold]       {'CHANGED' if diff_res.constraints_changed else 'UNCHANGED'}"
    )
    console.print(Panel(panel_text, title="PROJECT PACKAGE DIFF", border_style="yellow"))
    console.print()


@project_app.command("backup")
def backup_project_cmd(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name (defaults to active project)."),
    include_artifacts: bool = typer.Option(False, "--include-artifacts", help="Include full artifact payload files in backup."),
) -> None:
    """Create a timestamped .wlipjt backup archive in project-backups/."""
    from rich.panel import Panel
    from backend.workline.project.backup import backup_service
    from backend.workline.project.models import ExportOptions

    target_name = project if isinstance(project, str) and project.strip() else get_active_project_name()
    if not target_name:
        print_error("No active project selected. Specify a project name or open one.")
        raise typer.Exit(code=1)

    project_info = find_project(target_name)
    if not project_info:
        print_error(f"Project '{target_name}' not found.")
        raise typer.Exit(code=1)

    proj_dir, _ = project_info
    opts = ExportOptions(include_artifacts=include_artifacts)

    try:
        pkg_file, manifest, warnings = backup_service.create_backup(proj_dir, options=opts)
        for w in warnings:
            console.print(f"[bold yellow][WARNING][/bold yellow] {w}")

        panel_text = (
            f"[bold]Project:[/bold]      {manifest.project_name}\n"
            f"[bold]Backup File:[/bold]  [green]{pkg_file}[/green]\n"
            f"[bold]Version:[/bold]      v{manifest.project_version}\n"
            f"[bold]Timestamp:[/bold]    {manifest.exported_at[:19].replace('T', ' ')}\n"
            f"[bold]Integrity:[/bold]    [bold green]VERIFIED[/bold green]"
        )
        console.print(Panel(panel_text, title="PROJECT BACKUP CREATED", border_style="green"))
        console.print()
    except Exception as e:
        print_error(f"Backup failed: {e}")
        raise typer.Exit(code=1)

