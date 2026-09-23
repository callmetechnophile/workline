"""
Implementation of `wg search "<query>"` command.
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from cli.workline.project.filesystem import find_project_root
from cli.workline.retrieval.retriever import ProjectRetriever

console = Console()


def search_command(
    query: str = typer.Argument(..., help="Search query (semantic or technical keyword)"),
    type: Optional[str] = typer.Option(None, "--type", "-t", help="Resource type filter (e.g. component, requirement, architecture, decision, task)"),
    top_k: int = typer.Option(8, "--top-k", "-k", help="Maximum number of results to return"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """Perform local hybrid semantic search over WORKLINE project files."""
    target_dir = Path(path).resolve() if path else Path.cwd()
    root = find_project_root(target_dir)
    if not root:
        console.print(f"[bold red]Error:[/bold red] '{target_dir}' is not a WORKLINE project.")
        raise typer.Exit(code=1)

    console.print(f"\n[dim]Searching WORKLINE project '{root.name}'...[/dim]")
    retriever = ProjectRetriever(root)
    
    results = retriever.retrieve(
        query=query,
        top_k=top_k,
        resource_types=[type] if type else None,
    )

    if not results:
        console.print(f"[yellow]No matching project files found for query:[/yellow] '{query}'\n")
        return

    console.print(f"\n[bold white]Moss retrieval: {len(results)} results[/bold white]\n")
    
    for idx, r in enumerate(results, 1):
        type_tag = f"[{r.resource_type.upper()}]"
        console.print(f"[bold cyan]{type_tag}[/bold cyan] [bold white]{r.title}[/bold white]")
        console.print(f"  [dim]score:[/dim] [yellow]{r.score:.2f}[/yellow]  [dim]path:[/dim] [cyan]{r.path}[/cyan]")
        
        # Display short snippet of content
        lines = [l.strip() for l in r.content.splitlines() if l.strip() and not l.strip().startswith("=")]
        snippet = " ".join(lines[:2])
        if len(snippet) > 160:
            snippet = snippet[:160] + "..."
        if snippet:
            console.print(f"  [dim]{snippet}[/dim]")
        console.print()
