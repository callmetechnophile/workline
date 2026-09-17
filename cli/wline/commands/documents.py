"""
wline documents - Technical documentation generation, listing, and review.

Routes to agent.27 (TechDocAgent) via the AgentControlFabric.
Capabilities used: create_document, review_document, publish_document.
"""

import asyncio
import json
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cli.wline.ui.output import print_error, print_info

documents_app = typer.Typer(
    name="documents",
    help="Generate, list, and review technical documentation via agent.27.",
)
console = Console()


def _fabric():
    from armourflow.fabric.fabric import get_control_fabric
    return get_control_fabric()


def _db():
    from armourflow.data.client import get_database_client
    return get_database_client()


@documents_app.command("generate")
def documents_generate(
    title: str = typer.Option("Untitled Document", "--title", "-t", help="Document title"),
    doc_type: str = typer.Option("technical_report", "--type", help="Document type (e.g. technical_report, sop, design_spec)"),
    project: str = typer.Option("default", "--project", "-p", help="Project identifier"),
    payload: str = typer.Option("{}", "--payload", help="Additional generation parameters as JSON"),
):
    """Generate a technical document via agent.27 (TechDocAgent)."""
    try:
        extra = json.loads(payload)
    except json.JSONDecodeError:
        print_error("--payload must be valid JSON.")
        raise typer.Exit(1)

    data = {"title": title, "document_type": doc_type, **extra}
    console.print(f"[bold cyan]Document Generation[/] → agent.27")
    console.print(f"  Title: [bold white]{title}[/]  Type: [dim]{doc_type}[/]")

    fabric = _fabric()
    task = asyncio.run(
        fabric.submit_task(
            payload=data,
            target_agent_id="agent.27",
            target_capability="create_document",
            project_id=project,
        )
    )

    color = "green" if task.state.value == "COMPLETED" else "yellow"
    console.print(f"Task: [bold cyan]{task.task_id}[/]  State: [{color}]{task.state.value}[/]")
    if task.error:
        console.print(f"[bold red]Error:[/] {task.error}")
    elif task.result:
        console.print(Panel(json.dumps(task.result, indent=2, default=str), title="Generated Document", border_style="green"))


@documents_app.command("list")
def documents_list(
    project: str = typer.Option("default", "--project", "-p", help="Project identifier"),
    limit: int = typer.Option(20, "--limit", "-n", help="Maximum documents to show"),
):
    """List technical documents stored in the state layer."""
    db = _db()
    try:
        docs = asyncio.run(db.list_by_table("document"))[:limit]
    except Exception:
        docs = []

    if not docs:
        print_info(f"No documents found for project '{project}'.")
        print_info("Run: wline documents generate --title 'My Report'")
        return

    table = Table(title=f"Documents – project '{project}' ({len(docs)} found)", border_style="cyan")
    table.add_column("Document ID", style="bold cyan", no_wrap=True)
    table.add_column("Title", style="bold white")
    table.add_column("Type", style="dim")
    table.add_column("Status", justify="center")
    table.add_column("Created", style="dim")

    for d in docs:
        status = d.get("status", "DRAFT")
        color = "green" if status == "PUBLISHED" else "yellow"
        table.add_row(
            d.get("id", "?"),
            d.get("title", "Untitled")[:40],
            d.get("document_type", "unknown"),
            f"[{color}]{status}[/]",
            str(d.get("created_at", ""))[:19],
        )

    console.print(table)


@documents_app.command("review")
def documents_review(
    document_id: str = typer.Argument(..., help="Document ID to review"),
    project: str = typer.Option("default", "--project", "-p", help="Project identifier"),
):
    """Submit a document for peer review via agent.27 (review_document capability)."""
    console.print(f"[bold cyan]Document Review[/] → agent.27  (ID: {document_id})")

    fabric = _fabric()
    task = asyncio.run(
        fabric.submit_task(
            payload={"document_id": document_id},
            target_agent_id="agent.27",
            target_capability="review_document",
            project_id=project,
        )
    )

    color = "green" if task.state.value == "COMPLETED" else "yellow"
    console.print(f"Task: [bold cyan]{task.task_id}[/]  State: [{color}]{task.state.value}[/]")
    if task.error:
        console.print(f"[bold red]Error:[/] {task.error}")
    elif task.result:
        console.print(Panel(json.dumps(task.result, indent=2, default=str), title="Review Report", border_style="green"))
