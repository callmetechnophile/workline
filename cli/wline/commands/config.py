"""Configuration management commands for Workline."""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

from cli.wline.core.paths import get_active_project_name, get_config_file, get_workspace_dir
from cli.wline.core.workspace import get_workspace_config, update_workspace_config
from cli.wline.ui.output import print_error, print_success

config_app = typer.Typer(name="config", help="Manage Workline configuration and workspace settings.")
console = Console()


@config_app.command("show")
def show_config() -> None:
    """Display current Workline configuration."""
    cfg = get_workspace_config()
    active = get_active_project_name()

    table = Table(title="WORKLINE CONFIGURATION", box=None)
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    table.add_row("Workspace", str(get_workspace_dir()))
    table.add_row("Config File", str(get_config_file()))
    table.add_row("Active Project", active if active else "[dim]None[/dim]")

    console.print(table)


@config_app.command("set")
def set_config(
    key: str = typer.Argument(..., help="Configuration key (e.g. 'workspace')"),
    value: str = typer.Argument(..., help="New value for the configuration key"),
) -> None:
    """Update a Workline configuration setting."""
    if key.lower() == "workspace":
        target = Path(value).expanduser()
        try:
            target.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print_error(f"Cannot access or create target workspace directory: {e}")
            raise typer.Exit(code=1)

        update_workspace_config(target)
        print_success(f"Workspace path updated to: {target.resolve()}")
    else:
        print_error(f"Unknown configuration key: '{key}'. Supported keys: 'workspace'")
        raise typer.Exit(code=1)
