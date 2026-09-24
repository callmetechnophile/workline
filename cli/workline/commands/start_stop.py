"""Implementation of `wg start`, `wg stop`, `wg logs` — docker-compose lifecycle."""

import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

console = Console()

_COMPOSE_CANDIDATES = [
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
]
_VALID_SERVICES = ["api", "surrealdb", "qdrant", "redis", "worker"]


def _find_compose_file() -> Optional[Path]:
    """Search up from cwd for the docker-compose file."""
    current = Path.cwd().resolve()
    for _ in range(8):
        for name in _COMPOSE_CANDIDATES:
            f = current / name
            if f.exists():
                return f
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _run_compose(compose_file: Path, args: list) -> int:
    """Run docker compose command with v2 then v1 fallback."""
    cmd_v2 = ["docker", "compose", "-f", str(compose_file)] + args
    result = subprocess.run(cmd_v2)
    if result.returncode != 0:
        cmd_v1 = ["docker-compose", "-f", str(compose_file)] + args
        result = subprocess.run(cmd_v1)
    return result.returncode


def start_command(
    detach: bool = typer.Option(True, "--detach/--foreground", "-d", help="Run in background"),
    build: bool = typer.Option(False, "--build", help="Rebuild images before starting"),
) -> None:
    """Start the local WORKLINE stack (docker-compose up)."""
    console.print("\n[bold white]Starting WORKLINE Stack[/bold white]\n")

    compose_file = _find_compose_file()
    if not compose_file:
        console.print("[red]Error:[/red] docker-compose.yml not found — run this command from the WORKLINE repository root")
        raise typer.Exit(code=1)

    console.print(f"[dim]Using: {compose_file}[/dim]")
    args = ["up"]
    if detach:
        args.append("-d")
    if build:
        args.append("--build")

    rc = _run_compose(compose_file, args)
    if rc == 0:
        console.print("\n[bold green]✓[/bold green] WORKLINE stack started")
        console.print("[dim]  API:      http://localhost:8000[/dim]")
        console.print("[dim]  Frontend: http://localhost:3000[/dim]")
        console.print("[dim]  SurrealDB: http://localhost:8001[/dim]")
        console.print("[dim]  Qdrant:   http://localhost:6333[/dim]")
        console.print("\n[dim]Run [bold]wg open[/bold] to open WORKLINE.[/dim]\n")
    else:
        console.print("\n[red]✗[/red] Failed to start stack — check Docker is running")
        raise typer.Exit(code=rc)


def stop_command(
    remove_volumes: bool = typer.Option(False, "--volumes", "-v", help="Also remove data volumes (DESTRUCTIVE)"),
) -> None:
    """Stop the local WORKLINE stack (docker-compose down)."""
    console.print("\n[bold white]Stopping WORKLINE Stack[/bold white]\n")

    compose_file = _find_compose_file()
    if not compose_file:
        console.print("[red]Error:[/red] docker-compose.yml not found")
        raise typer.Exit(code=1)

    if remove_volumes:
        from rich.prompt import Confirm
        confirmed = Confirm.ask(
            "[red]WARNING[/red]: This will delete all SurrealDB and Qdrant data volumes. Continue?",
            default=False,
        )
        if not confirmed:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit()

    args = ["down"]
    if remove_volumes:
        args.append("-v")

    rc = _run_compose(compose_file, args)
    if rc == 0:
        console.print("[bold green]✓[/bold green] WORKLINE stack stopped\n")
    else:
        console.print("[red]✗[/red] Failed to stop stack")
        raise typer.Exit(code=rc)


def logs_command(
    service: Optional[str] = typer.Argument(None, help=f"Service name ({', '.join(_VALID_SERVICES)}). Omit for all."),
    follow: bool = typer.Option(True, "--follow/--no-follow", "-f", help="Follow log output"),
    tail: int = typer.Option(50, "--tail", "-n", help="Number of lines to show from end"),
) -> None:
    """Follow logs for a WORKLINE stack service."""
    compose_file = _find_compose_file()
    if not compose_file:
        console.print("[red]Error:[/red] docker-compose.yml not found")
        raise typer.Exit(code=1)

    if service and service not in _VALID_SERVICES:
        console.print(f"[yellow]Warning:[/yellow] Unknown service '{service}'. Known services: {', '.join(_VALID_SERVICES)}")

    args = ["logs", f"--tail={tail}"]
    if follow:
        args.append("-f")
    if service:
        args.append(service)

    _run_compose(compose_file, args)
