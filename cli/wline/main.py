"""
Main entry point for the WORKLINE CLI (wline).

All operations begin with:
    wline <command>

Environment activation is bootstrapped via:
    workline --activate
"""

import os
from pathlib import Path
import sys
from typing import Optional

# Ensure repository root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import typer
from rich.console import Console

from cli.wline import __version__
from cli.wline.core.credentials import APICredentialManager
from cli.wline.core.session import EnvironmentSessionManager

# ── Unified Core Command Implementations ──────────────────────────────────────
from cli.workline.commands.new import new_project_command
from cli.workline.commands.open import open_command
from cli.workline.commands.inspect import inspect_command
from cli.workline.commands.backup import backup_command
from cli.workline.commands.restore import restore_command
from cli.workline.commands.sync import sync_command
from cli.workline.commands.doctor import doctor_command
from cli.workline.commands.status import status_command
from cli.workline.commands.start_stop import start_command, stop_command, logs_command
from cli.wline.commands.apis import apis_interactive_manager, apis_status_command, apis_reset_command
from cli.wline.commands.drive import drive_command

app = typer.Typer(
    name="wline",
    help="WORKLINE — Local Engineering Intelligence Runtime & Platform Gateway",
    no_args_is_help=False,
    add_completion=False,
)
console = Console()

# ── Runtime Sub-App ───────────────────────────────────────────────────────────
runtime_app = typer.Typer(
    name="runtime",
    help="Developer & diagnostic commands for internal services",
    no_args_is_help=False,
)
runtime_app.command("status")(status_command)
runtime_app.command("start")(start_command)
runtime_app.command("stop")(stop_command)
runtime_app.command("restart")(start_command)
runtime_app.command("logs")(logs_command)

# ── Core Commands ─────────────────────────────────────────────────────────────
app.command("new")(new_project_command)
app.command("open")(open_command)
app.command("inspect")(inspect_command)
app.command("status")(status_command)
app.command("doctor")(doctor_command)
app.command("backup")(backup_command)
app.command("restore")(restore_command)
app.command("sync")(sync_command)
app.command("drive")(drive_command)
app.add_typer(runtime_app, name="runtime")


# ── Version Command ───────────────────────────────────────────────────────────
def version_callback(value: bool) -> None:
    if value:
        console.print(
            f"WORKLINE ([bold cyan]wline[/bold cyan]) "
            f"version [bold white]{__version__}[/bold white]"
        )
        raise typer.Exit()


@app.command("version")
def version_command() -> None:
    """Show WORKLINE version."""
    console.print(
        f"WORKLINE ([bold cyan]wline[/bold cyan]) "
        f"version [bold white]{__version__}[/bold white]"
    )


# ── APIs Subcommand Dispatcher (wline apis) ───────────────────────────────────
apis_app = typer.Typer(
    name="apis",
    help="Configure and manage external API integrations (Bedrock, GitHub, LiveKit, etc.)",
    invoke_without_command=True,
)


@apis_app.callback(invoke_without_command=True)
def apis_default(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        apis_interactive_manager()


apis_app.command("status")(apis_status_command)
apis_app.command("reset")(apis_reset_command)
app.add_typer(apis_app, name="apis")


# ── Main Entry Callback (Handles wline with no args & wline --apis) ───────────
@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
    apis: bool = typer.Option(
        False,
        "--apis",
        help="Open API Configuration Manager (or use 'wline apis').",
    ),
) -> None:
    """WORKLINE — Engineering Lifecycle Platform & Local Intelligence Runtime."""
    # Inject stored credentials to environment on any wline invocation
    APICredentialManager.inject_credentials_to_env()

    if apis and ctx.invoked_subcommand is None:
        apis_interactive_manager()
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        state = EnvironmentSessionManager.load_state()
        active_proj = state.active_project_name or "None"
        env_status = state.status

        status_color = "green" if env_status == "ACTIVE" else ("yellow" if env_status == "DEGRADED" else "dim")

        console.print(f"\n[bold white]WORKLINE[/bold white]")
        console.print("------------------------------------------")
        console.print(f"[bold]Project:[/bold] {active_proj}")
        console.print(f"[bold]State:[/bold]   [{status_color}]{env_status}[/{status_color}]\n")

        console.print("[bold]Project Control:[/bold]")
        console.print("  [cyan]new[/cyan]        Create a new WORKLINE engineering project")
        console.print("  [cyan]open[/cyan]       Open/select a WORKLINE project")
        console.print("  [cyan]inspect[/cyan]    Inspect project intelligence & manifest state")
        console.print("  [cyan]status[/cyan]     Show current WORKLINE environment status\n")

        console.print("[bold]Project Data & Storage:[/bold]")
        console.print("  [cyan]backup[/cyan]     Create a portable .wlipjt backup package")
        console.print("  [cyan]restore[/cyan]    Restore a WORKLINE project")
        console.print("  [cyan]sync[/cyan]       Synchronize with configured project storage")
        console.print("  [cyan]drive[/cyan]      Google Drive browser-agent backup & restore\n")

        console.print("[bold]System & Integrations:[/bold]")
        console.print("  [cyan]doctor[/cyan]     Diagnose the local WORKLINE environment")
        console.print("  [cyan]runtime[/cyan]    Internal runtime controls (status, start, stop, logs)")
        console.print("  [cyan]apis[/cyan]       Manage external API integrations (--apis)\n")

        if env_status == "INACTIVE":
            console.print("[dim]Note: WORKLINE is not activated. Run [bold]workline --activate[/bold] to initialize.[/dim]\n")
        else:
            console.print("[dim]Run [bold]wline <command> --help[/bold] for details.[/dim]\n")


def main() -> None:
    """Executable entry point for wline."""
    app()


if __name__ == "__main__":
    main()
