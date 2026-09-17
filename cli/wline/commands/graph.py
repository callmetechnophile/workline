"""CLI commands for Graph queries, SurrealQL execution, and evidence inspection."""

import asyncio
import json
from typing import Optional

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


@app.command("query")
def graph_query(
    surql: str = typer.Argument(..., help="SurrealQL query to execute against the platform graph DB"),
    raw: bool = typer.Option(False, "--raw", help="Output raw JSON instead of a formatted panel"),
):
    """Execute a raw SurrealQL query against the platform graph database."""
    from armourflow.data.client import get_database_client

    db = get_database_client()
    console.print(f"[bold cyan]Graph Query:[/] {surql}")
    try:
        result = asyncio.run(db.execute_raw(surql))
    except AttributeError:
        # Fallback: execute via list_by_table for simple SELECT queries
        try:
            table_name = surql.strip().split()[-1].strip(";")
            result = asyncio.run(db.list_by_table(table_name))
        except Exception as exc:
            console.print(f"[bold red]Error:[/] Query failed: {exc}")
            raise typer.Exit(1)
    except Exception as exc:
        console.print(f"[bold red]Error:[/] Query failed: {exc}")
        raise typer.Exit(1)

    if raw:
        console.print(Panel(json.dumps(result, indent=2, default=str), title="Query Result (raw)", border_style="cyan"))
        return

    if isinstance(result, list):
        from rich.table import Table as RTable
        if result and isinstance(result[0], dict):
            tbl = RTable(title=f"Query Result ({len(result)} rows)", border_style="cyan")
            cols = list(result[0].keys())
            for col in cols:
                tbl.add_column(col, style="white")
            for row in result:
                tbl.add_row(*[str(row.get(c, ""))[:60] for c in cols])
            console.print(tbl)
        else:
            console.print(Panel(json.dumps(result, indent=2, default=str), title="Query Result", border_style="cyan"))
    else:
        console.print(Panel(json.dumps(result, indent=2, default=str), title="Query Result", border_style="cyan"))


@app.command("traverse")
def graph_traverse(
    from_entity: str = typer.Argument(..., help="Starting entity ID"),
    depth: int = typer.Option(2, "--depth", "-d", help="Max traversal depth"),
    direction: str = typer.Option("both", "--direction", help="Traversal direction: in | out | both"),
):
    """Traverse the platform knowledge graph from an entity node."""
    from armourflow.data.client import get_database_client

    db = get_database_client()
    console.print(f"[bold cyan]Graph Traversal:[/] from=[bold white]{from_entity}[/]  depth={depth}  direction={direction}")

    # Build a SurrealQL graph traversal expression
    if direction == "out":
        arrow = "->"
    elif direction == "in":
        arrow = "<-"
    else:
        arrow = "<->"

    surql = f"SELECT * FROM {from_entity}{arrow}({depth}) LIMIT 100;"
    try:
        result = asyncio.run(db.execute_raw(surql))
    except AttributeError:
        result = []
    except Exception as exc:
        console.print(f"[bold red]Error:[/] Traversal failed: {exc}")
        raise typer.Exit(1)

    if not result:
        console.print(f"[yellow]No connected nodes found from '{from_entity}' at depth {depth}.[/yellow]")
        return

    console.print(Panel(json.dumps(result, indent=2, default=str), title=f"Traversal from {from_entity}", border_style="green"))
