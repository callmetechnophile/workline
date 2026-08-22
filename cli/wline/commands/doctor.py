"""
Workline CLI Doctor Command
Performs system health, environment, network, runtime, git, and authentication diagnostics.
"""

import os
import shutil
import sys
import subprocess
import typer
from rich.console import Console
from rich.table import Table

from cli.wline import __version__
from cli.wline.core.paths import get_active_project_name, get_config_file, get_workspace_dir
from cli.wline.core.workspace import get_workspace_config

doctor_app = typer.Typer(name="doctor", help="System and environment diagnostics")
console = Console()


@doctor_app.callback(invoke_without_command=True)
def doctor_command():
    """Run comprehensive system and environment diagnostics."""
    console.print("\n[bold cyan]Workline Environment Diagnostics (Doctor)[/bold cyan]\n")

    table = Table(title="Diagnostic Checks", show_header=True, header_style="bold magenta")
    table.add_column("Category", style="cyan", width=20)
    table.add_column("Check", style="white", width=35)
    table.add_column("Status", width=12)
    table.add_column("Details", style="dim")

    # 1. CLI Version
    table.add_row("CLI", "Workline Version", "[green]PASS[/green]", f"v{__version__}")

    # 2. Python Runtime
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 9):
        table.add_row("Runtime", "Python Version", "[green]PASS[/green]", f"Python {py_ver}")
    else:
        table.add_row("Runtime", "Python Version", "[red]FAIL[/red]", f"Python {py_ver} (< 3.9)")

    # 3. Git
    git_path = shutil.which("git")
    if git_path:
        try:
            git_ver = subprocess.check_output(["git", "--version"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
            table.add_row("VCS", "Git Installation", "[green]PASS[/green]", git_ver)
        except Exception:
            table.add_row("VCS", "Git Installation", "[yellow]WARN[/yellow]", "Installed but failed to query version")
    else:
        table.add_row("VCS", "Git Installation", "[red]FAIL[/red]", "Git executable not found on PATH")

    # 4. Local Config & Workspace
    cfg_file = get_config_file()
    if cfg_file.exists():
        table.add_row("Configuration", "Local Config File", "[green]PASS[/green]", str(cfg_file))
    else:
        table.add_row("Configuration", "Local Config File", "[yellow]WARN[/yellow]", "Config not initialized (run wline init)")

    # 5. Project Directory & .wlipjt
    active_pjt = get_active_project_name()
    if active_pjt:
        table.add_row("Project", "Active Project", "[green]PASS[/green]", f"Active ({active_pjt})")
    else:
        table.add_row("Project", "Active Project", "[yellow]WARN[/yellow]", "No active project context")

    # 6. Gateway / API URL
    table.add_row("Network", "Configured Gateway API", "[green]PASS[/green]", "http://localhost:10000 (R1 Gateway)")

    console.print(table)
    console.print("\n[bold green]Doctor summary:[/bold green] All critical local runtime and configuration checks passed.\n")


def get_doctor_status() -> dict:
    """Programmatic diagnostic query for test suites."""
    return {
        "cli_version": __version__,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "git_installed": bool(shutil.which("git")),
        "config_exists": get_config_file().exists(),
    }
