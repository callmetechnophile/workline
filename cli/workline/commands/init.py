"""
Implementation of `wg init <name>` command.
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from cli.workline.project.manager import ProjectManager

console = Console()

_WORKLINE_YAML_TEMPLATE = """\
name: {name}
display_name: {display_name}
version: 1.0.0
domain: {domain}
description: {description}
status: active
created_at: {created_at}
"""


def _do_init(
    name: str,
    target_dir: Optional[Path] = None,
    description: str = "",
    domain: str = "Hardware Systems & Power Engineering",
) -> None:
    """
    Core project initialisation logic shared by `wg init` and `wg new`.

    Creates the standard .wl filesystem layout via ProjectManager and also
    writes a ``workline.yaml`` file in the project root for `wline` CLI
    compatibility.
    """
    from datetime import datetime, timezone

    mgr = ProjectManager()

    root = mgr.init_project(
        name=name,
        target_dir=target_dir,
        description=description,
        domain=domain,
    )

    # --- workline.yaml (wline CLI compatibility) ----------------------------
    slug = name.lower().replace(" ", "-").replace("_", "-")
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    yaml_content = _WORKLINE_YAML_TEMPLATE.format(
        name=slug,
        display_name=name,
        domain=domain,
        description=description,
        created_at=created_at,
    )

    yaml_path = root / "workline.yaml"
    yaml_path.write_text(yaml_content, encoding="utf-8")
    # -----------------------------------------------------------------------

    console.print(f"\n[bold green]✓ Initialized WORKLINE project:[/bold green] [bold white]{name}[/bold white]")
    console.print(f"  Location: [cyan]{root}[/cyan]")
    console.print("  Filesystem: [dim]README.wl, .wl/manifest.wl, standard modules[/dim]")
    console.print(f"  Manifest:  [dim]workline.yaml[/dim]")
    console.print("\n[dim]Run 'wg open' or 'wg index' inside the project directory to begin.[/dim]\n")


def init_project_command(
    name: str = typer.Argument(..., help="Name of the WORKLINE engineering project to create"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Target directory for project"),
    domain: str = typer.Option("Hardware Systems & Power Engineering", "--domain", "-d", help="Engineering domain"),
    description: str = typer.Option("", "--description", help="Project description"),
) -> None:
    """Initialize a new portable WORKLINE .wl project directory."""
    target_dir = Path(path).resolve() if path else None

    try:
        _do_init(
            name=name,
            target_dir=target_dir,
            description=description,
            domain=domain,
        )
    except Exception as e:
        console.print(f"[bold red]Error initializing project:[/bold red] {e}")
        raise typer.Exit(code=1)
