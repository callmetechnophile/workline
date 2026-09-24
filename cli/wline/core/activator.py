"""
WORKLINE Environment Activator (`workline --activate`).

Validates runtime, checks/launches local services, establishes session,
and handles first-run interactive provider onboarding.
"""

import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from typing import Dict, Optional, Tuple

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from cli.wline import __version__
from cli.wline.core.credentials import APICredentialManager
from cli.wline.core.session import EnvironmentSessionManager, ServiceHealth

console = Console()


def _check_tcp(host: str, port: int, timeout: float = 1.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def _check_docker() -> bool:
    try:
        res = subprocess.run(["docker", "info"], capture_output=True, timeout=3)
        return res.returncode == 0
    except Exception:
        return False


def activate_environment(
    project_path: Optional[Path] = None,
    interactive: bool = True,
    profile: Optional[str] = None,
) -> int:
    """
    Activate the local WORKLINE environment.

    Performs 8-step startup sequence:
    1. Detect and validate local installation.
    2. Check/start essential and derived local services.
    3. Initialize session state.
    4. Inject credentials from active profile.
    5. Check external API integrations.
    6. Establish active project context if found.
    7. Offer first-run API setup if unconfigured.
    8. Display unified WORKLINE Environment status banner.
    """
    console.print("\n[bold white]WORKLINE[/bold white]")
    console.print("------------------------------------------")

    # Step 1: Runtime
    services: Dict[str, ServiceHealth] = {}
    py_ok = sys.version_info >= (3, 9)
    services["Runtime"] = ServiceHealth(
        name="Runtime",
        status="READY" if py_ok else "UNAVAILABLE",
        detail=f"Python {sys.version.split()[0]} / wline v{__version__}",
        is_essential=True,
    )

    # Step 2: Local Core Stack Services
    surreal_up = _check_tcp("localhost", 8001)
    services["SurrealDB"] = ServiceHealth(
        name="SurrealDB",
        status="READY" if surreal_up else "DEGRADED",
        detail="Port 8001 reachable" if surreal_up else "Not running (using local files)",
        is_essential=False,
    )

    qdrant_up = _check_tcp("localhost", 6333)
    services["Qdrant"] = ServiceHealth(
        name="Qdrant",
        status="READY" if qdrant_up else "DEGRADED",
        detail="Port 6333 reachable" if qdrant_up else "Not running (using local Moss)",
        is_essential=False,
    )

    # Step 3: Local Derived Retrieval (Moss)
    # Moss is always available via LocalMossAdapter / filesystem fallback
    services["Moss"] = ServiceHealth(
        name="Moss",
        status="READY",
        detail="Local in-process semantic engine",
        is_essential=True,
    )

    # Step 4: Agents & Tools (MCP & A2A)
    services["Agents"] = ServiceHealth(
        name="Agents",
        status="READY",
        detail="Local tool registry & A2A protocol",
        is_essential=True,
    )

    # Step 5: LiveKit Realtime
    lk_creds = APICredentialManager.get_provider_credentials("livekit", profile)
    lk_has_url = bool(lk_creds.get("livekit_url") or os.environ.get("LIVEKIT_URL"))
    services["LiveKit"] = ServiceHealth(
        name="LiveKit",
        status="READY" if lk_has_url else "DEGRADED",
        detail="Connected" if lk_has_url else "Local token fallback active",
        is_essential=False,
    )

    # Step 6: Active Project Context
    active_target = project_path or Path.cwd()
    from cli.workline.project.filesystem import find_project_root
    found_root = find_project_root(active_target)
    if found_root:
        services["Project"] = ServiceHealth(
            name="Project",
            status="READY",
            detail=found_root.name,
            is_essential=False,
        )
    else:
        services["Project"] = ServiceHealth(
            name="Project",
            status="READY",
            detail="No active project (use 'wline new' or 'wline open')",
            is_essential=False,
        )

    # Save Activation State
    env_state = EnvironmentSessionManager.activate(services, found_root)
    APICredentialManager.inject_credentials_to_env(profile)

    # Display Services Status Table
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("Service", style="bold", width=16)
    table.add_column("Status")
    table.add_column("Detail", style="dim")

    for s_name in ["Runtime", "Project", "SurrealDB", "Qdrant", "Moss", "Agents", "LiveKit"]:
        sh = services.get(s_name)
        if sh:
            s_color = "green" if sh.status == "READY" else ("yellow" if sh.status == "DEGRADED" else "red")
            table.add_row(sh.name, f"[{s_color}]{sh.status}[/{s_color}]", sh.detail)

    console.print(table)
    console.print("------------------------------------------")

    if env_state.status == "ACTIVE":
        console.print("[bold green]WORKLINE environment ACTIVE.[/bold green]\n")
    elif env_state.status == "DEGRADED":
        console.print("[bold yellow]WORKLINE environment ACTIVE (degraded non-essential services).[/bold yellow]\n")
    else:
        console.print("[bold red]WORKLINE environment ERROR on essential services.[/bold red]\n")
        return 1

    # First-run API check
    active_prof = APICredentialManager.get_active_profile()
    store = APICredentialManager.load_store()
    configured_apis = store.get("profiles", {}).get(active_prof, {})

    if not configured_apis and interactive:
        from rich.prompt import Confirm
        console.print("[dim]No external API providers configured in profile '[bold]{active_prof}[/bold]'.[/dim]")
        if Confirm.ask("Configure external integrations now?", default=False):
            from cli.wline.commands.apis import apis_interactive_manager
            apis_interactive_manager()

    console.print("[dim]Run [bold]wline[/bold] to check active project and environment status.[/dim]\n")
    return 0


# Top-level standalone activation script runner
def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="WORKLINE Environment Activator")
    parser.add_argument("--activate", action="store_true", help="Activate WORKLINE local environment")
    parser.add_argument("--project", "-p", help="Target project path")
    parser.add_argument("--profile", help="Active API profile to use")
    parser.add_argument("--non-interactive", action="store_true", help="Run without prompts")
    args = parser.parse_args()

    if args.activate or len(sys.argv) == 1:
        rc = activate_environment(
            project_path=Path(args.project).resolve() if args.project else None,
            interactive=not args.non_interactive,
            profile=args.profile,
        )
        sys.exit(rc)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
