"""Main entry point for the Workline CLI (wline)."""

from typing import Optional
import typer
from rich.console import Console

from cli.wline import __version__
from cli.wline.commands.agent import agent_app
from cli.wline.commands.bom import bom_app
from cli.wline.commands.component import component_app
from cli.wline.commands.config import config_app
from cli.wline.commands.database import database_app
from cli.wline.commands.finding import finding_app
from cli.wline.commands.git import git_app
from cli.wline.commands.github import github_app
from cli.wline.commands.init import init_command
from cli.wline.commands.knowledge import knowledge_app
from cli.wline.commands.lesson import lesson_app
from cli.wline.commands.order import order_app
from cli.wline.commands.payment import payment_app
from cli.wline.commands.pcb import pcb_app
from cli.wline.commands.procurement import procurement_app
from cli.wline.commands.project import project_app
from cli.wline.commands.requirement import requirement_app
from cli.wline.commands.status import status_command
from cli.wline.commands.team import team_app
from cli.wline.commands.version import release_command, snapshot_command, version_command
from cli.wline.commands.decision import decision_app
from cli.wline.commands.generate import app as generate_app
from cli.wline.commands.cache import app as cache_app
from cli.wline.commands.document import app as document_app
from cli.wline.commands.entity import app as entity_app
from cli.wline.commands.graph import app as graph_app
from cli.wline.commands.requirement import app as requirement_app
from cli.wline.commands.doctor import doctor_app
from cli.wline.ui.banner import print_main_banner

app = typer.Typer(
    name="wline",
    help="Workline - Engineering Lifecycle Platform CLI",
    no_args_is_help=False,
    add_completion=False,
)
console = Console()

# Mount sub-apps and direct commands
app.command("init")(init_command)
app.add_typer(project_app, name="project")
app.add_typer(knowledge_app, name="knowledge")
app.add_typer(decision_app, name="decision")
app.add_typer(requirement_app, name="requirement")
app.add_typer(finding_app, name="finding")
app.add_typer(lesson_app, name="lesson")
app.add_typer(team_app, name="team")
app.add_typer(git_app, name="git")
app.add_typer(github_app, name="github")
app.add_typer(agent_app, name="agent")
app.add_typer(component_app, name="component")
app.add_typer(procurement_app, name="procurement")
app.add_typer(bom_app, name="bom")
app.add_typer(order_app, name="order")
app.add_typer(payment_app, name="payment")
app.add_typer(pcb_app, name="pcb")
app.add_typer(generate_app, name="generate")
app.add_typer(cache_app, name="cache")
app.add_typer(document_app, name="document")
app.add_typer(entity_app, name="entity")
app.add_typer(graph_app, name="graph")
app.add_typer(config_app, name="config")
app.add_typer(database_app, name="database")
app.add_typer(doctor_app, name="doctor")
app.command("status")(status_command)
app.command("version")(version_command)
app.command("snapshot")(snapshot_command)
app.command("release")(release_command)


def version_callback(value: bool) -> None:
    if value:
        version_command()
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show Workline version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Workline main CLI callback handler."""
    if ctx.invoked_subcommand is None:
        print_main_banner()
        console.print("\n[bold white]Usage:[/bold white]\n  wline <command>\n")
        console.print("[bold white]Available commands:[/bold white]\n")
        console.print("  [cyan]init[/cyan]      Initialize local project workspace & Git repository")
        console.print("  [cyan]git[/cyan]       Local Git version control (status, commit, log, push, pull, branch, tag)")
        console.print("  [cyan]github[/cyan]    GitHub remote management (auth, init, connect, remote, push)")
        console.print("  [cyan]version[/cyan]   Display Workline CLI, active project, Git, and schema version")
        console.print("  [cyan]snapshot[/cyan]  Create deterministic project state snapshot")
        console.print("  [cyan]release[/cyan]   Create formal project version release and Git tag")
        console.print("  [cyan]project[/cyan]   Manage engineering projects (create, list, open, status, delete)")
        console.print("  [cyan]agent[/cyan]     Manage Multi-Agent Engine (run, status, approve, history)")
        console.print("  [cyan]database[/cyan]  Manage SurrealDB and Qdrant data layers (status, migrate, validate)")
        console.print("  [cyan]config[/cyan]    Manage workspace configuration\n")


def main() -> None:
    """Executable entry point."""
    app()


if __name__ == "__main__":
    main()
