"""Workspace and Project initialization command."""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from backend.workline.git.repository import project_repo_manager
from cli.wline.core.manifest import (
    BudgetConfig,
    ProjectManifest,
    TargetPlatformConfig,
    TimelineConfig,
    normalize_project_name,
)
from cli.wline.core.paths import set_active_project_name
from cli.wline.core.workspace import create_project, get_workspace_dir, init_workspace
from cli.wline.ui.output import print_success

console = Console()


def init_command(
    project: Optional[str] = typer.Argument(
        None, help="Optional engineering project name to initialize with Git and metadata."
    ),
    workspace: Optional[str] = typer.Option(
        None, "--workspace", "-w", help="Custom workspace directory path."
    ),
) -> None:
    """Initialize a Workline project (with Git + metadata) or initialize the workspace root."""
    if project:
        # Full Project Initialization Workflow
        norm_name = normalize_project_name(project)
        display_name = project.strip().replace("-", " ").title()

        console.print("\n[bold cyan]WORKLINE PROJECT INITIALIZATION[/bold cyan]\n")
        console.print(f"[bold]Project:[/bold]\n{norm_name}\n")
        console.print("[bold]Initializing:[/bold]")

        manifest = ProjectManifest(
            name=norm_name,
            display_name=display_name,
            description=f"Workline Engineering Project: {display_name}",
            domain="robotics",
            budget=BudgetConfig(amount=20000.0, currency="INR"),
            timeline=TimelineConfig(target_days=56),
            complexity="medium",
            target_platform=TargetPlatformConfig(controller="ESP32-S3"),
        )

        # 1. Workspace directory and lifecycle subdirs
        try:
            proj_dir = create_project(manifest)
            console.print("[green]✓ Project manifest[/green]")
            console.print("[green]✓ Local workspace[/green]")
        except FileExistsError:
            proj_dir = (get_workspace_dir() / norm_name).resolve()
            console.print("[green]✓ Project manifest (existing)[/green]")
            console.print("[green]✓ Local workspace (existing)[/green]")

        # 2. Local Git repository + .gitignore + .workline/project.toon + initial commit
        git_repo = project_repo_manager.init_project_git(
            project_path=proj_dir,
            project_id=norm_name,
            project_name=display_name,
            default_branch="main",
            project_version="0.1.0",
            schema_version=1,
        )
        console.print("[green]✓ Git repository[/green]")
        console.print("[green]✓ .gitignore[/green]")
        console.print("[green]✓ Workline metadata[/green]\n")

        console.print(f"[bold]Initial commit:[/bold]\ncreated ({git_repo.current_commit[:7] if git_repo.current_commit else 'initial'})\n")
        console.print("[bold green]Project ready.[/bold green]\n")

        set_active_project_name(norm_name)
    else:
        # Workspace Initialization
        ws_path = Path(workspace).expanduser().resolve() if workspace else None
        actual_path, already_initialized = init_workspace(ws_path)

        if already_initialized:
            print_success("Workline workspace already initialized")
        else:
            print_success(f"Workline workspace initialized at {actual_path}")

