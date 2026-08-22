"""CLI commands for Entity management and resolution."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import typer
from backend.workline.knowledge.graph.models import EntityMention, EntityType
from backend.workline.knowledge.graph.resolver import EntityResolver
from backend.workline.knowledge.graph.service import knowledge_graph_service

app = typer.Typer(name="entity", help="Find, inspect, resolve, and audit engineering entities.")
console = Console()


@app.command("find")
def find_entity_cmd(
    query: str = typer.Argument(..., help="Entity name, MPN, or alias to search"),
    project_id: str = typer.Option(None, "--project", "-p", help="Target project ID"),
):
    """Search canonical entities in the Engineering Knowledge Graph."""
    entities = knowledge_graph_service.search_entities(query, project_id=project_id)
    if not entities:
        console.print(f"[yellow]No entities found matching '{query}'[/yellow]")
        return

    for ent in entities:
        console.print(
            Panel.fit(
                f"[bold cyan]Canonical:[/bold cyan] {ent.canonical_name}\n"
                f"[bold]Type:[/bold] {ent.entity_type.value}\n"
                f"[bold]Manufacturer:[/bold] {ent.manufacturer or 'N/A'}\n"
                f"[bold]Aliases:[/bold] {', '.join(ent.aliases) if ent.aliases else 'None'}\n"
                f"[bold]Status:[/bold] {ent.status.value}\n"
                f"[bold]Confidence:[/bold] {int(ent.confidence * 100)}%",
                title=f"Entity: {ent.entity_id}",
                border_style="cyan",
            )
        )


@app.command("inspect")
def inspect_entity_cmd(
    entity_id: str = typer.Argument(..., help="Entity ID to inspect"),
):
    """View specifications, relationships, and conflicts for a canonical entity."""
    graph_data = knowledge_graph_service.get_related(entity_id)
    if not graph_data:
        console.print(f"[red]Error: Entity '{entity_id}' not found[/red]")
        raise typer.Exit(1)

    ent = graph_data["entity"]
    console.print(
        Panel.fit(
            f"[bold cyan]ID:[/bold cyan] {ent['entity_id']}\n"
            f"[bold]Name:[/bold] {ent['canonical_name']}\n"
            f"[bold]Type:[/bold] {ent['entity_type']}\n"
            f"[bold]Manufacturer:[/bold] {ent.get('manufacturer') or 'N/A'}",
            title="Canonical Entity",
            border_style="cyan",
        )
    )

    specs = graph_data.get("specifications", [])
    if specs:
        table = Table(title="SPECIFICATIONS", border_style="green")
        table.add_column("Property", style="bold")
        table.add_column("Value", style="green")
        table.add_column("Document")
        table.add_column("Page")
        for s in specs:
            table.add_row(s["property"], s["value"], s["source_document"], str(s["page"]))
        console.print(table)


@app.command("resolve")
def resolve_mention_cmd(
    mention_text: str = typer.Argument(..., help="Mentioned part number or text"),
    doc_id: str = typer.Option("DOC-MANUAL", "--doc", help="Source document ID"),
    mfr: str = typer.Option(None, "--mfr", help="Manufacturer context hint"),
):
    """Run prioritized resolution on an entity mention."""
    mention = EntityMention(
        mention_id=f"MNT-{int(hash(mention_text)) % 100000}",
        document_id=doc_id,
        entity_type=EntityType.COMPONENT,
        original_text=mention_text,
        normalized_text=mention_text.strip().upper(),
        source_span=f"Referenced {mention_text} in document.",
    )

    existing = knowledge_graph_service.search_entities("")
    result = EntityResolver.resolve_mention(mention, existing, manufacturer_context=mfr)

    console.print(
        Panel.fit(
            f"[bold cyan]Mention:[/bold cyan] {mention_text}\n"
            f"[bold]Status:[/bold] {result.status}\n"
            f"[bold]Canonical ID:[/bold] {result.canonical_entity_id or 'None'}\n"
            f"[bold]Confidence:[/bold] {int(result.confidence * 100)}%\n"
            f"[bold]Strategy:[/bold] {result.strategy}\n"
            f"[bold]Reason:[/bold] {result.reason}",
            title="Entity Resolution Result",
            border_style="green" if result.status == "RESOLVED" else "yellow",
        )
    )


@app.command("conflicts")
def list_conflicts_cmd(
    project_id: str = typer.Option(None, "--project", "-p", help="Filter by project ID"),
):
    """Audit all open specification conflicts across documents."""
    conflicts = knowledge_graph_service.list_conflicts(project_id)
    if not conflicts:
        console.print("[green]✓ No specification conflicts detected across documents.[/green]")
        return

    table = Table(title="SPECIFICATION CONFLICTS", border_style="red")
    table.add_column("Conflict ID", style="bold cyan")
    table.add_column("Entity ID")
    table.add_column("Property", style="yellow")
    table.add_column("Value A (Source A)", style="green")
    table.add_column("Value B (Source B)", style="red")
    table.add_column("Status")

    for c in conflicts:
        table.add_row(
            c.conflict_id,
            c.entity_id,
            c.property,
            f"{c.value_a} ({c.source_a})",
            f"{c.value_b} ({c.source_b})",
            c.status,
        )

    console.print(table)
