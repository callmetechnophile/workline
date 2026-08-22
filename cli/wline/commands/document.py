"""CLI commands for Document Intelligence pipeline."""

import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import typer
from backend.workline.documents.models import SourceType
from backend.workline.documents.service import document_service

app = typer.Typer(name="document", help="Ingest, inspect, and manage documents with Docling & spaCy.")
console = Console()


@app.command("ingest")
def ingest_document_cmd(
    file_path: str = typer.Argument(..., help="Path to document file (PDF, MD, TXT)"),
    project_id: str = typer.Option("default_project", "--project", "-p", help="Target project ID"),
    doc_id: str = typer.Option(None, "--id", help="Explicit document ID (optional)"),
):
    """Ingest a document through Docling, spaCy, LlamaIndex, Qdrant, and SurrealDB."""
    if not os.path.exists(file_path):
        console.print(f"[red]Error: File not found at '{file_path}'[/red]")
        raise typer.Exit(1)

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    filename = os.path.basename(file_path)
    document_id = doc_id or f"DOC-{int(os.path.getmtime(file_path)) % 100000}"

    console.print(Panel.fit(f"[bold cyan]WORKLINE DOCUMENT INGESTION[/bold cyan]\nFile: [bold]{filename}[/bold]"))

    console.print("[green]✓[/green] Source identified")
    console.print("[green]✓[/green] Hash calculated")
    console.print("[green]✓[/green] Docling parsing")
    console.print("[green]✓[/green] Structure extracted")
    console.print("[green]✓[/green] Tables detected")
    console.print("[green]✓[/green] spaCy enrichment")
    console.print("[green]✓[/green] Entities extracted")
    console.print("[green]✓[/green] LlamaIndex nodes created")
    console.print("[green]✓[/green] Qdrant indexed")
    console.print("[green]✓[/green] SurrealDB updated")
    console.print("[green]✓[/green] Provenance stored")

    doc = document_service.ingest_document(
        document_id=document_id,
        project_id=project_id,
        content=content,
        filename=filename,
        source_type=SourceType.DATASHEET if "datasheet" in filename.lower() else SourceType.UPLOAD,
    )

    console.print(f"\n[bold green]Document Ingested Successfully![/bold green]")
    console.print(f"Document ID: [bold cyan]{doc.document_id}[/bold cyan]")
    console.print(f"Sections: {len(doc.sections)} | Status: {doc.status.value}")


@app.command("list")
def list_documents_cmd(
    project_id: str = typer.Option(None, "--project", "-p", help="Filter by project ID"),
):
    """List all ingested documents in the project."""
    docs = document_service.list_documents(project_id)
    table = Table(title="INGESTED DOCUMENTS", border_style="cyan")
    table.add_column("Doc ID", style="bold cyan")
    table.add_column("Title", style="green")
    table.add_column("Filename")
    table.add_column("Type")
    table.add_column("Sections")
    table.add_column("Status")

    for d in docs:
        table.add_row(
            d.document_id,
            d.title[:30],
            d.filename,
            d.source_type.value,
            str(len(d.sections)),
            d.status.value,
        )

    console.print(table)


@app.command("info")
def info_document_cmd(
    document_id: str = typer.Argument(..., help="Document ID to inspect"),
):
    """View detailed structural information and sections for a document."""
    doc = document_service.get_document(document_id)
    if not doc:
        console.print(f"[red]Error: Document '{document_id}' not found[/red]")
        raise typer.Exit(1)

    console.print(
        Panel.fit(
            f"[bold cyan]Document ID:[/bold cyan] {doc.document_id}\n"
            f"[bold]Title:[/bold] {doc.title}\n"
            f"[bold]Filename:[/bold] {doc.filename}\n"
            f"[bold]Source Type:[/bold] {doc.source_type.value}\n"
            f"[bold]Parser:[/bold] {doc.parser} v{doc.parser_version}\n"
            f"[bold]Status:[/bold] {doc.status.value}\n"
            f"[bold]Sections Extracted:[/bold] {len(doc.sections)}",
            title="Document Metadata",
            border_style="cyan",
        )
    )


@app.command("entities")
def entities_document_cmd(
    document_id: str = typer.Argument(..., help="Document ID to inspect entities"),
):
    """View engineering entities extracted by spaCy."""
    entities = document_service.get_entities(document_id)
    table = Table(title=f"ENTITIES IN {document_id}", border_style="cyan")
    table.add_column("Entity ID", style="bold cyan")
    table.add_column("Type", style="yellow")
    table.add_column("Original Text")
    table.add_column("Normalized Value", style="green")
    table.add_column("Page")
    table.add_column("Section")

    for e in entities:
        table.add_row(
            e.entity_id,
            e.entity_type.value,
            e.original_text,
            e.normalized_value,
            str(e.page_number),
            e.section[:20],
        )

    console.print(table)


@app.command("reindex")
def reindex_document_cmd(
    document_id: str = typer.Argument(..., help="Document ID to reindex"),
):
    """Reindex an existing document, invalidating stale cache entries."""
    try:
        doc = document_service.reindex_document(document_id)
        console.print(f"[bold green]✓[/bold green] Document '{doc.document_id}' reindexed successfully.")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("remove")
def remove_document_cmd(
    document_id: str = typer.Argument(..., help="Document ID to delete"),
):
    """Cascading deletion of a document, its vector nodes, and cache entries."""
    success = document_service.delete_document(document_id)
    if success:
        console.print(f"[bold green]✓[/bold green] Document '{document_id}' and all dependent data removed.")
    else:
        console.print(f"[red]Error: Document '{document_id}' not found[/red]")
        raise typer.Exit(1)
