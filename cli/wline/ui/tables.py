"""Table and status views for Workline CLI."""

from typing import List
from rich.console import Console
from rich.table import Table
from rich import box

from cli.wline.core.lifecycle import (
    ORDERED_LIFECYCLE_STAGES,
    StageStatus,
    calculate_progress,
)
from cli.wline.core.manifest import ProjectManifest

console = Console()


def render_project_list(projects: List[ProjectManifest]) -> None:
    """Render the discovered project roster in a clean Rich table."""
    if not projects:
        console.print("[dim]No Workline projects found in workspace.[/dim]")
        return

    table = Table(
        title="WORKLINE PROJECTS",
        title_style="bold cyan",
        box=box.ROUNDED,
        header_style="bold white",
        expand=False,
    )
    table.add_column("Project", style="cyan", no_wrap=True)
    table.add_column("Stage", style="white")
    table.add_column("Status", style="bold")

    for p in projects:
        # Determine human-friendly current stage name
        curr_stage_id = p.lifecycle.current_stage
        stage_state = p.lifecycle.stages.get(curr_stage_id)
        if stage_state:
            stage_display = stage_state.name.title()
            status_val = stage_state.status.value.replace("_", " ")
        else:
            stage_display = curr_stage_id.replace("_", " ").title()
            status_val = p.lifecycle.status.replace("_", " ").upper()

        if "COMPLETED" in status_val:
            status_styled = f"[green]{status_val}[/green]"
        elif "IN PROGRESS" in status_val:
            status_styled = f"[cyan]{status_val}[/cyan]"
        elif "BLOCKED" in status_val or "FAILED" in status_val:
            status_styled = f"[red]{status_val}[/red]"
        else:
            status_styled = f"[dim]{status_val}[/dim]"

        table.add_row(p.name, stage_display, status_styled)

    console.print(table)


def render_lifecycle_status(manifest: ProjectManifest) -> None:
    """Render the engineering lifecycle breakdown with live status dots and progress."""
    console.print(f"\n[bold white]{manifest.display_name.upper()}[/bold white]\n")
    console.print("[bold cyan]Engineering Lifecycle[/bold cyan]")
    console.print("[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]")

    for stage_id, stage_name in ORDERED_LIFECYCLE_STAGES:
        stage_state = manifest.lifecycle.stages.get(stage_id)
        status = stage_state.status if stage_state else StageStatus.NOT_STARTED

        # Format label
        label = stage_name.title()
        padding = " " * max(1, 26 - len(label))

        if status == StageStatus.COMPLETED:
            symbol = "[bold green]●[/bold green]"
            status_text = "[green]COMPLETED[/green]"
        elif status == StageStatus.IN_PROGRESS:
            symbol = "[bold cyan]●[/bold cyan]"
            status_text = "[cyan]IN PROGRESS[/cyan]"
        elif status == StageStatus.BLOCKED:
            symbol = "[bold red]▲[/bold red]"
            status_text = "[red]BLOCKED[/red]"
        elif status == StageStatus.FAILED:
            symbol = "[bold red]✖[/bold red]"
            status_text = "[red]FAILED[/red]"
        else:
            symbol = "[dim]○[/dim]"
            status_text = "[dim]NOT STARTED[/dim]"

        console.print(f"{label}{padding}{symbol} {status_text}")

    progress = calculate_progress(manifest.lifecycle)
    progress_str = f"{int(progress)}%" if progress.is_integer() else f"{progress}%"
    console.print(f"\n[bold white]Progress:[/bold white] [bold cyan]{progress_str}[/bold cyan]\n")
