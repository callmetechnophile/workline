"""
Implementation of `wg context "<query>"` command.
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from cli.workline.project.filesystem import find_project_root
from cli.workline.retrieval.context import ContextBuilder
from cli.workline.retrieval.retriever import ProjectRetriever

console = Console()


def context_command(
    query: str = typer.Argument(..., help="Topic or query to construct project context for"),
    budget: int = typer.Option(3500, "--budget", "-b", help="Token budget for context bundle"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """Retrieve and format a structured context bundle with file provenance for an engineering query."""
    target_dir = Path(path).resolve() if path else Path.cwd()
    root = find_project_root(target_dir)
    if not root:
        console.print(f"[bold red]Error:[/bold red] '{target_dir}' is not a WORKLINE project.")
        raise typer.Exit(code=1)

    retriever = ProjectRetriever(root)
    builder = ContextBuilder(default_token_budget=budget)
    bundle = builder.build_context(retriever, query=query, token_budget=budget)

    console.print(f"\n[bold white]PROJECT CONTEXT BUNDLE[/bold white] for [cyan]'{query}'[/cyan]")
    console.print(f"[dim]Estimated Tokens: {bundle.estimated_tokens} | Sources: {len(bundle.sources)}[/dim]\n")

    for sec_name, entries in bundle.sections.items():
        console.print(f"[bold yellow]{sec_name}[/bold yellow] ({len(entries)} items)")
        for entry in entries[:2]:
            lines = entry.splitlines()
            header = lines[0] if lines else ""
            content_sample = " ".join(l.strip() for l in lines[1:4])[:140]
            console.print(f"  [cyan]{header}[/cyan] [dim]{content_sample}...[/dim]")
        console.print()

    console.print("[bold]Context sources:[/bold]")
    for s in bundle.sources:
        console.print(f"  • [cyan]{s}[/cyan]")
    console.print()
