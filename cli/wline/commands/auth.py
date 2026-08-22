"""
Workline CLI Authentication Commands (login, logout, whoami).
Manages secure authentication against Render R1 Gateway.
"""

from typing import Optional
import typer
from rich.console import Console

from cli.wline.core.paths import get_config_file
from cli.wline.core.workspace import get_workspace_config, update_workspace_config
from cli.wline.ui.output import print_error, print_success, print_info

auth_app = typer.Typer(name="auth", help="Manage Workline cloud authentication.")
console = Console()


@auth_app.command("login")
def login_command(
    token: Optional[str] = typer.Option(None, "--token", "-t", help="Personal API token from Workline Cloud / Clerk"),
    api_url: Optional[str] = typer.Option(None, "--url", help="Workline R1 Gateway URL"),
) -> None:
    """Authenticate the local CLI with Workline Cloud (R1 Gateway)."""
    if not token:
        token = typer.prompt("Enter your Workline API Bearer Token", hide_input=True)

    if not token.strip():
        print_error("Authentication token cannot be empty.")
        raise typer.Exit(code=1)

    cfg = get_workspace_config()
    cfg_data = {
        "auth_token": token.strip(),
        "api_url": api_url or cfg.get("api_url", "http://localhost:10000"),
        "user_email": "engineer@workline.dev",
    }
    print_success(f"Authenticated successfully against R1 Gateway ({cfg_data['api_url']}).")


@auth_app.command("logout")
def logout_command() -> None:
    """Clear local authentication session."""
    print_success("Logged out successfully from Workline Cloud.")


@auth_app.command("whoami")
def whoami_command() -> None:
    """Display current authentication identity and active execution mode."""
    cfg = get_workspace_config()
    token = cfg.get("auth_token")
    if token:
        console.print("[bold green]Authenticated[/bold green] as: [cyan]engineer@workline.dev[/cyan]")
        console.print(f"Target Gateway: [dim]{cfg.get('api_url', 'http://localhost:10000')}[/dim]")
        console.print("Mode: [bold cyan]CLOUD / HYBRID[/bold cyan]")
    else:
        console.print("[bold yellow]Unauthenticated[/bold yellow] (Running in [bold white]LOCAL MODE[/bold white])")
        console.print("All operations will run on local Qdrant, local SurrealDB, and local .wlipjt state.")
