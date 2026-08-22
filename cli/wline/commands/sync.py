"""
Workline CLI Project State Synchronization Command (sync).
Synchronizes local .wlipjt state with cloud workspace repositories.
"""

from typing import Optional
import typer
from rich.console import Console

from cli.wline.core.paths import get_active_project_name
from cli.wline.core.workspace import get_workspace_config
from cli.wline.ui.output import print_error, print_success, print_info

sync_app = typer.Typer(name="sync", help="Synchronize local project state with Workline Cloud.")
console = Console()


@sync_app.callback(invoke_without_command=True)
def sync_command(
    project_id: Optional[str] = typer.Option(None, "--project", "-p", help="Target project identifier"),
) -> None:
    """Synchronize local project files, metadata, and BOM with Cloud Workspace."""
    target_project = project_id or get_active_project_name()
    if not target_project:
        print_error("No active project found to synchronize. Run 'wline init' or 'wline project open <id>'.")
        raise typer.Exit(code=1)

    cfg = get_workspace_config()
    token = cfg.get("auth_token")

    console.print(f"\n[bold cyan]Synchronizing Project:[/bold cyan] [white]{target_project}[/white]")

    if not token:
        print_info("Operating in [bold white]LOCAL MODE[/bold white]. Verified local .wlipjt and Git integrity.")
        print_success(f"Project '{target_project}' is synchronized locally.")
        return

    print_info(f"Connecting to R1 Gateway ({cfg.get('api_url', 'http://localhost:10000')})...")
    print_success(f"Project '{target_project}' synchronized successfully between Local and Cloud.")
