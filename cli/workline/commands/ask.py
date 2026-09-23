"""
Implementation of `wg ask "<question>"` command.
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from cli.workline.agent.runtime import WorklineAgent
from cli.workline.project.filesystem import find_project_root

console = Console()


def ask_command(
    question: str = typer.Argument(..., help="Engineering question to answer based on local project context"),
    sources: bool = typer.Option(True, "--sources/--no-sources", help="Print verified project file citations"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """Ask the WORKLINE AI Agent an engineering question grounded in local .wl files."""
    target_dir = Path(path).resolve() if path else Path.cwd()
    root = find_project_root(target_dir)
    if not root:
        console.print(f"[bold red]Error:[/bold red] '{target_dir}' is not a WORKLINE project.")
        raise typer.Exit(code=1)

    agent = WorklineAgent(root)
    result = agent.ask(question)

    console.print(f"\n[bold white]WORKLINE AI[/bold white]\n")
    console.print(f"[bold]Question:[/bold] {question}\n")
    console.print(f"[bold]Answer:[/bold]\n{result.answer}\n")
    
    if sources and result.sources:
        console.print("[bold]Sources:[/bold]")
        for s in result.sources:
            console.print(f"  • [cyan]{s}[/cyan]")
        console.print()
        
    console.print(f"[bold]Confidence:[/bold]\n[green]{result.confidence}[/green]\n")
