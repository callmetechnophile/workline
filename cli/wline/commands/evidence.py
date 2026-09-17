"""
wline evidence - Evidence research and inspection commands.

Search uses the CentralTavilyClient (real-time web research).
Inspection queries the SurrealDB/in-memory state layer for stored evidence.
"""

import asyncio
import json
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cli.wline.ui.output import print_error, print_info

evidence_app = typer.Typer(
    name="evidence",
    help="Search for technical evidence and inspect stored evidence records.",
)
console = Console()


def _tavily():
    from armourflow.external.tavily import CentralTavilyClient
    return CentralTavilyClient()


def _db():
    from armourflow.data.client import get_database_client
    return get_database_client()


@evidence_app.command("search")
def evidence_search(
    query: str = typer.Argument(..., help="Research query to send to the Tavily evidence engine"),
    max_results: int = typer.Option(5, "--max-results", "-n", help="Maximum search results to display"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Restrict results to a specific domain (e.g. nasa.gov)"),
    raw: bool = typer.Option(False, "--raw", help="Print raw JSON instead of formatted table"),
):
    """Search for engineering evidence via the Tavily research service."""
    console.print(f"[bold cyan]Evidence Search:[/] {query}")
    client = _tavily()
    try:
        results = asyncio.run(client.search(query=query, max_results=max_results, include_domain=domain))
    except Exception as exc:
        print_error(f"Tavily search failed: {exc}")
        raise typer.Exit(1)

    if not results:
        print_info("No results found.")
        return

    if raw:
        console.print(Panel(json.dumps(results, indent=2, default=str), title="Raw Results", border_style="cyan"))
        return

    table = Table(title=f"Evidence Results ({len(results)} found)", border_style="cyan")
    table.add_column("Title", style="bold white", max_width=50)
    table.add_column("URL", style="cyan", max_width=50)
    table.add_column("Score", justify="center", style="yellow")

    for r in results:
        table.add_row(
            r.get("title", "Untitled")[:48],
            r.get("url", "")[:48],
            f"{r.get('score', 0.0):.2f}",
        )

    console.print(table)


@evidence_app.command("inspect")
def evidence_inspect(
    evidence_id: str = typer.Argument(..., help="Evidence record ID from SurrealDB / in-memory state"),
    raw: bool = typer.Option(False, "--raw", help="Print raw JSON record"),
):
    """Inspect a stored evidence record by ID."""
    db = _db()
    try:
        record = asyncio.run(db.get("evidence", evidence_id))
    except Exception as exc:
        print_error(f"Database lookup failed: {exc}")
        raise typer.Exit(1)

    if not record:
        print_error(f"Evidence record '{evidence_id}' not found.")
        raise typer.Exit(1)

    if raw:
        console.print(Panel(json.dumps(record, indent=2, default=str), title=f"Evidence: {evidence_id}", border_style="cyan"))
        return

    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(style="bold cyan", justify="right")
    grid.add_column(style="white")

    for key, val in record.items():
        grid.add_row(f"{key}:", str(val))

    console.print(Panel(grid, title=f"[bold green]Evidence Record: {evidence_id}[/]", border_style="cyan"))
