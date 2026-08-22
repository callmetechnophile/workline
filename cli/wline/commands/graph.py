"""CLI commands for Graph queries and evidence inspection."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import typer
from backend.workline.knowledge.graph.service import knowledge_graph_service

app = typer.Typer(name="graph", help="Traverse relationships and inspect evidence chains in the knowledge graph.")
console = Console()


@app.command("related")
def related_entities_cmd(
    entity_id: str = typer.Argument(..., help="Source entity ID"),
    depth: int = typer.Option(2, "--depth", "-d", help="Max traversal depth"),
):
    """View 1-hop and 2-hop related entities in the graph."""
    graph_data = knowledge_graph_service.get_related(entity_id, max_depth=depth)
    if not graph_data:
        console.print(f"[red]Error: Entity '{entity_id}' not found in graph[/red]")
        raise typer.Exit(1)

    table = Table(title=f"GRAPH RELATIONSHIPS FOR {entity_id}", border_style="cyan")
    table.add_column("From", style="bold")
    table.add_column("Edge Type", style="yellow")
    table.add_column("To", style="bold cyan")
    table.add_column("Source Type")

    for r in graph_data.get("relationships", []):
        table.add_row(r["from_entity"], r["relationship_type"], r["to_entity"], r["source_type"])

    console.print(table)


@app.command("evidence")
def inspect_evidence_cmd(
    entity_id: str = typer.Argument(..., help="Entity ID to inspect evidence for"),
):
    """Inspect full provenance and document evidence supporting an entity."""
    specs = knowledge_graph_service.get_specifications(entity_id)
    if not specs:
        console.print(f"[yellow]No evidence-backed specifications found for '{entity_id}'[/yellow]")
        return

    table = Table(title=f"EVIDENCE CHAIN FOR {entity_id}", border_style="green")
    table.add_column("Property", style="bold")
    table.add_column("Value", style="green")
    table.add_column("Document", style="cyan")
    table.add_column("Page")
    table.add_column("Section")
    table.add_column("Confidence")

    for s in specs:
        table.add_row(
            s.property,
            s.value,
            s.source_document,
            str(s.page),
            s.section,
            f"{int(s.confidence * 100)}%",
        )

    console.print(table)
