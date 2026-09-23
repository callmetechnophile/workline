"""
Primary entry point for the WORKLINE CLI (wg).
Operates over the portable WORKLINE .wl filesystem with local Moss semantic retrieval.
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

from cli.workline import __version__
from cli.workline.commands.init import init_project_command
from cli.workline.commands.project_ops import open_command, inspect_command, check_command
from cli.workline.commands.doctor import doctor_command
from cli.workline.commands.index import index_app
from cli.workline.commands.search import search_command
from cli.workline.commands.context import context_command
from cli.workline.commands.ask import ask_command
from cli.workline.commands.voice import voice_command
from cli.workline.commands.modules import (
    requirements_command,
    architecture_command,
    components_command,
    bom_command,
    tasks_command,
    decisions_command,
    research_command,
    documents_command,
    analysis_command,
    agents_command,
    team_command,
)
from cli.workline.commands.transfer import (
    export_command,
    import_command,
    sync_command,
    git_app,
)

app = typer.Typer(
    name="wg",
    help="WORKLINE CLI - Engineering Project & Local Moss Retrieval Platform",
    no_args_is_help=False,
    add_completion=False,
)
console = Console()

# ── Primary commands ──────────────────────────────────────────────────────────
app.command("init")(init_project_command)
app.command("open")(open_command)
app.command("inspect")(inspect_command)
app.command("check")(check_command)
app.command("doctor")(doctor_command)

# ── Retrieval & AI commands ───────────────────────────────────────────────────
app.command("search")(search_command)
app.command("context")(context_command)
app.command("ask")(ask_command)
app.add_typer(index_app, name="index")
app.command("voice")(voice_command)

# ── Modular domain commands ───────────────────────────────────────────────────
app.command("requirements")(requirements_command)
app.command("architecture")(architecture_command)
app.command("components")(components_command)
app.command("bom")(bom_command)
app.command("tasks")(tasks_command)
app.command("decisions")(decisions_command)
app.command("research")(research_command)
app.command("documents")(documents_command)
app.command("analysis")(analysis_command)
app.command("agents")(agents_command)
app.command("team")(team_command)

# ── Transfer & version control ────────────────────────────────────────────────
app.command("export")(export_command)
app.command("import")(import_command)
app.command("sync")(sync_command)
app.add_typer(git_app, name="git")


def version_callback(value: bool) -> None:
    if value:
        console.print(f"WORKLINE CLI ([bold cyan]wg[/bold cyan]) version [bold white]{__version__}[/bold white]")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show WORKLINE CLI version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
    offline: bool = typer.Option(
        False,
        "--offline",
        help="Enforce local-only mode with zero external network connectivity.",
    ),
) -> None:
    """WORKLINE CLI - Engineering Lifecycle Platform with Local Moss Semantic Retrieval."""
    if offline:
        os.environ["WORKLINE_OFFLINE"] = "1"
        
    if ctx.invoked_subcommand is None:
        console.print("\n[bold white]WORKLINE CLI ([bold cyan]wg[/bold cyan])[/bold white]")
        console.print("[dim]Local Engineering Project & Moss Semantic Retrieval Platform[/dim]\n")
        console.print("[bold white]Core Commands:[/bold white]")
        console.print("  [cyan]init[/cyan]         Initialize a new portable .wl engineering project")
        console.print("  [cyan]open[/cyan]         Detect and open the active WORKLINE project")
        console.print("  [cyan]inspect[/cyan]      Inspect project resources and Moss index status")
        console.print("  [cyan]check[/cyan]        Validate project filesystem, manifest, and zero-secrets")
        console.print("  [cyan]doctor[/cyan]       Run comprehensive workspace & local Moss diagnostics\n")
        console.print("[bold white]Retrieval & AI Commands:[/bold white]")
        console.print("  [cyan]index[/cyan]        Build or update the local Moss retrieval index (--incremental, --rebuild, --watch)")
        console.print("  [cyan]search[/cyan]       Local hybrid semantic + keyword search (--type)")
        console.print("  [cyan]context[/cyan]      Retrieve structured multi-domain context bundle")
        console.print("  [cyan]ask[/cyan]          Ask AI engineering questions with file citations")
        console.print("  [cyan]voice[/cyan]        LiveKit realtime conversational session (--text)\n")
        console.print("[bold white]Project Resources:[/bold white]")
        console.print("  [dim]requirements | architecture | components | bom | research | documents | analysis | tasks | decisions | agents | team[/dim]\n")
        console.print("[bold white]Packaging & Transfer:[/bold white]")
        console.print("  [dim]export | import | sync | git[/dim]\n")
        console.print("[dim]Run 'wg <command> --help' for detailed usage.[/dim]\n")


def main() -> None:
    """Executable entry point."""
    app()


if __name__ == "__main__":
    main()
