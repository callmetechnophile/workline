"""Implementation of `wg open` — discovers project, starts stack, opens WORKLINE."""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

_WORKLINE_URL = "http://localhost:3000"
_API_URL = "http://localhost:8000"
_COMPOSE_FILE_CANDIDATES = [
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
]


def _find_compose_file(repo_root: Path) -> Optional[Path]:
    for name in _COMPOSE_FILE_CANDIDATES:
        f = repo_root / name
        if f.exists():
            return f
    return None


def _find_repo_root(start: Path) -> Optional[Path]:
    """Walk up to find the repository root (contains docker-compose.yml)."""
    current = start.resolve()
    for _ in range(8):
        for name in _COMPOSE_FILE_CANDIDATES:
            if (current / name).exists():
                return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _docker_available() -> bool:
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _stack_running() -> bool:
    """Check if the WORKLINE API is already up."""
    try:
        import urllib.request
        urllib.request.urlopen(_API_URL + "/health", timeout=2)
        return True
    except Exception:
        return False


def _start_stack(compose_file: Path) -> bool:
    """Run docker-compose up -d. Returns True if successful."""
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "up", "-d"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            # Fallback to docker-compose (v1)
            result = subprocess.run(
                ["docker-compose", "-f", str(compose_file), "up", "-d"],
                capture_output=True,
                text=True,
                timeout=120,
            )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _wait_for_api(timeout: int = 60) -> bool:
    """Poll API health until ready or timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _stack_running():
            return True
        time.sleep(2)
    return False


def open_command(
    path: Optional[str] = typer.Argument(None, help="Project path (defaults to current directory)"),
    no_browser: bool = typer.Option(False, "--no-browser", help="Start the stack but do not open the browser"),
    url: str = typer.Option(_WORKLINE_URL, "--url", help="WORKLINE frontend URL"),
    skip_start: bool = typer.Option(False, "--skip-start", help="Skip starting the stack; just open the browser"),
) -> None:
    """Open the active project in WORKLINE (starts stack if not running)."""
    console.print("\n[bold white]WORKLINE[/bold white]\n")

    target = Path(path).resolve() if path else Path.cwd()

    # 1. Discover project
    from cli.workline.project.filesystem import find_project_root
    root = find_project_root(target)
    if root:
        console.print(f"[bold green]✓[/bold green] Project: [dim]{root.name}[/dim]")
    else:
        console.print(f"[yellow]⚠[/yellow] No .wl project found at [dim]{target}[/dim] — opening WORKLINE without a project context")
        root = target

    # 2. Check stack
    if skip_start:
        console.print("[dim]--skip-start: skipping stack launch[/dim]")
    elif _stack_running():
        console.print("[bold green]✓[/bold green] WORKLINE stack is already running")
    else:
        # Find docker-compose file
        repo_root = _find_repo_root(root)
        compose_file = _find_compose_file(repo_root) if repo_root else None

        if not _docker_available():
            console.print("[yellow]⚠[/yellow] Docker is not available — cannot start the local stack")
            console.print("[dim]  Install Docker Desktop or run the WORKLINE stack manually.[/dim]")
        elif not compose_file:
            console.print("[yellow]⚠[/yellow] docker-compose.yml not found — cannot start the local stack")
        else:
            console.print(f"[dim]Starting WORKLINE stack via {compose_file.name}...[/dim]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[dim]{task.description}[/dim]"),
                transient=True,
                console=console,
            ) as progress:
                task = progress.add_task("Starting services...", total=None)
                started = _start_stack(compose_file)

            if started:
                console.print("[bold green]✓[/bold green] Stack started — waiting for API to be ready...")
                ready = _wait_for_api(timeout=60)
                if ready:
                    console.print("[bold green]✓[/bold green] WORKLINE API is ready")
                else:
                    console.print("[yellow]⚠[/yellow] API is taking longer than expected — check [bold]wg logs api[/bold]")
            else:
                console.print("[red]✗[/red] Failed to start the stack — check Docker is running")

    # 3. Open browser
    if not no_browser:
        console.print(f"[bold green]→[/bold green] Opening [cyan]{url}[/cyan]")
        try:
            webbrowser.open(url)
        except Exception:
            console.print(f"[dim]Could not open browser automatically. Navigate to: {url}[/dim]")
    else:
        console.print(f"[dim]Browser suppressed. Navigate to: {url}[/dim]")

    console.print()
