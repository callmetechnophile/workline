"""Main entry point for the Workline CLI (wline)."""

from pathlib import Path
import sys
from typing import Optional

# Ensure repository root is on sys.path so armourflow, backend, and research_agents are importable
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

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
from cli.wline.commands.auth import auth_app, login_command, logout_command, whoami_command
from cli.wline.commands.sync import sync_app
from cli.wline.ui.banner import print_main_banner

# ── New ArmourFlow-integrated command sub-apps ────────────────────────────────
from cli.wline.commands.agents import agents_app
from cli.wline.commands.task import task_app
from cli.wline.commands.workflow import workflow_app
from cli.wline.commands.engineering import engineering_app
from cli.wline.commands.evidence import evidence_app
from cli.wline.commands.documents import documents_app
from cli.wline.commands.security import security_app
from cli.wline.commands.eval import eval_app
from cli.wline.commands.system import system_app

app = typer.Typer(
    name="wline",
    help="WORKLINE – Engineering Lifecycle Platform CLI",
    no_args_is_help=False,
    add_completion=False,
)
console = Console()

# ── Existing command mounts ───────────────────────────────────────────────────
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
app.add_typer(agent_app, name="agent")          # wline agent (singular) – internal runtime
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
app.add_typer(graph_app, name="graph")          # wline graph (related / evidence / query / traverse)
app.add_typer(config_app, name="config")
app.add_typer(database_app, name="database")
app.add_typer(doctor_app, name="doctor")
app.add_typer(auth_app, name="auth")
app.add_typer(sync_app, name="sync")
app.command("login")(login_command)
app.command("logout")(logout_command)
app.command("whoami")(whoami_command)
app.command("status")(status_command)
app.command("version")(version_command)
app.command("snapshot")(snapshot_command)
app.command("release")(release_command)

# ── ArmourFlow Control Fabric – integrated command mounts ─────────────────────
app.add_typer(agents_app, name="agents")        # wline agents (plural) – domain agent registry
app.add_typer(task_app, name="task")            # wline task – Control Fabric task lifecycle
app.add_typer(workflow_app, name="workflow")    # wline workflow – named workflow dispatch
app.add_typer(engineering_app, name="engineering")  # wline engineering – sim/optimize/dfm
app.add_typer(evidence_app, name="evidence")    # wline evidence – Tavily research + DB
app.add_typer(documents_app, name="documents")  # wline documents – TechDocAgent (agent.27)
app.add_typer(security_app, name="security")    # wline security – ArmorIQ + agent.22
app.add_typer(eval_app, name="eval")            # wline eval – UniversalEvaluationHarness
app.add_typer(system_app, name="system")        # wline system – platform health/diagnostics


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
    """WORKLINE Engineering Lifecycle Platform."""
    if ctx.invoked_subcommand is None:
        print_main_banner()
        console.print("\n[bold white]Usage:[/bold white]\n  wline <command>\n")
        console.print("[bold white]Platform commands (Workline Control Fabric):[/bold white]\n")
        console.print("  [bold cyan]agents[/bold cyan]      List / inspect / health-check the 27 domain agents")
        console.print("  [bold cyan]task[/bold cyan]        Submit, list, inspect, and cancel Control Fabric tasks")
        console.print("  [bold cyan]workflow[/bold cyan]    Dispatch named engineering workflows")
        console.print("  [bold cyan]engineering[/bold cyan] Simulation, Pareto optimization, and DFM analysis")
        console.print("  [bold cyan]evidence[/bold cyan]    Research evidence search (Tavily) and inspection")
        console.print("  [bold cyan]documents[/bold cyan]   Generate, list, and review technical documentation")
        console.print("  [bold cyan]graph[/bold cyan]       SurrealQL queries and graph traversal")
        console.print("  [bold cyan]security[/bold cyan]    Security audit and threat scanning (ArmorIQ + agent.22)")
        console.print("  [bold cyan]eval[/bold cyan]        Run evaluation benchmarks and view reports")
        console.print("  [bold cyan]system[/bold cyan]      Platform health, status, and diagnostics\n")
        console.print("[bold white]Workspace commands:[/bold white]\n")
        console.print("  [cyan]init[/cyan]        Initialize local project workspace & Git repository")
        console.print("  [cyan]project[/cyan]     Manage engineering projects (create, list, open, status)")
        console.print("  [cyan]git[/cyan]         Local Git version control (status, commit, log, push)")
        console.print("  [cyan]github[/cyan]      GitHub remote management (auth, init, connect, push)")
        console.print("  [cyan]agent[/cyan]       Internal Workline agent runtime (run, status, approve)")
        console.print("  [cyan]database[/cyan]    Manage SurrealDB and Qdrant data layers")
        console.print("  [cyan]config[/cyan]      Manage workspace configuration")
        console.print("  [cyan]version[/cyan]     Display Workline CLI and project version\n")
        console.print("[dim]Run 'wline <command> --help' for detailed usage.[/dim]\n")


def main() -> None:
    """Executable entry point."""
    app()


if __name__ == "__main__":
    main()
