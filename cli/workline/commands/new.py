"""Implementation of `wg new` — interactive project creation wizard."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm

console = Console()

_PROJECT_TYPES = [
    "hardware",
    "firmware",
    "robotics",
    "power-electronics",
    "iot",
    "embedded",
    "pcb",
    "systems",
    "other",
]


def new_project_command(
    name: Optional[str] = typer.Argument(None, help="Project name (prompted if omitted)"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Parent directory (defaults to cwd)"),
    project_type: Optional[str] = typer.Option(None, "--type", "-t", help="Project type"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Short description"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts"),
) -> None:
    """Create a new WORKLINE engineering project interactively."""
    console.print("\n[bold white]WORKLINE — New Project[/bold white]\n")

    # Gather inputs
    project_name = name or Prompt.ask("[bold]Project name[/bold]")
    if not project_name.strip():
        console.print("[red]Error:[/red] Project name cannot be empty.")
        raise typer.Exit(code=1)

    proj_desc = description
    if not proj_desc:
        proj_desc = Prompt.ask(
            "[bold]Description[/bold] [dim](optional, press Enter to skip)[/dim]",
            default="",
        )

    proj_type = project_type
    if not proj_type:
        console.print(f"\n[bold]Project type[/bold] [dim]({', '.join(_PROJECT_TYPES)})[/dim]")
        proj_type = Prompt.ask("Type", default="hardware")
        if proj_type not in _PROJECT_TYPES:
            proj_type = "hardware"

    parent_dir = Path(path).resolve() if path else Path.cwd()
    target_dir = parent_dir / project_name.lower().replace(" ", "-").replace("_", "-")

    # Confirm
    console.print(f"\n[bold]Project:[/bold]     {project_name}")
    console.print(f"[bold]Type:[/bold]        {proj_type}")
    console.print(f"[bold]Description:[/bold] {proj_desc or '—'}")
    console.print(f"[bold]Directory:[/bold]   {target_dir}")

    if not yes:
        confirmed = Confirm.ask("\nCreate this project?")
        if not confirmed:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit()

    # Delegate to init
    console.print()
    from cli.workline.commands.init import _do_init
    _do_init(
        name=project_name,
        target_dir=target_dir,
        description=proj_desc,
        domain=proj_type,
    )
