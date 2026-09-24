"""Package transfer commands for wg: export and import .wlipjt packages."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

console = Console()


def export_command(
    path: Optional[str] = typer.Argument(None, help="Project path (defaults to current directory)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    include_git: bool = typer.Option(False, "--git", help="Include git history in package"),
    include_vectors: bool = typer.Option(False, "--vectors", help="Include Qdrant vectors in package"),
    force: bool = typer.Option(False, "--force", help="Export even if validation fails"),
) -> None:
    """Export the project to a portable .wlipjt archive. Alias for `wg backup`."""
    from cli.workline.commands.backup import backup_command
    backup_command(
        path=path,
        output=output,
        include_git=include_git,
        include_vectors=include_vectors,
        force=force,
    )


def import_command(
    package: str = typer.Argument(..., help="Path to the .wlipjt package file"),
    target: Optional[str] = typer.Option(None, "--target", "-t", help="Restore target directory"),
    strategy: str = typer.Option("restore", "--strategy", "-s", help="Import strategy: restore, merge, new"),
) -> None:
    """Import / restore a project from a .wlipjt archive. Alias for `wg restore`."""
    from cli.workline.commands.restore import restore_command
    restore_command(package=package, target=target, strategy=strategy)
