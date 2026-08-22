"""Status convenience command."""

from typing import Optional
import typer

from cli.wline.commands.project import project_status


def status_command(
    name: Optional[str] = typer.Argument(None, help="Project name (defaults to active project)")
) -> None:
    """Display engineering lifecycle status for a project."""
    project_status(name)
