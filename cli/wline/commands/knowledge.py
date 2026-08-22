"""Knowledge CLI commands for search and memory inspection."""

from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import typer

from backend.workline.knowledge import (
    DecisionCategory,
    DecisionStatus,
    EngineeringDecision,
    EngineeringFinding,
    EngineeringLesson,
    EngineeringRequirement,
    knowledge_service,
    knowledge_summarizer,
)
from cli.wline.core.paths import get_active_project_name

knowledge_app = typer.Typer(name="knowledge", help="Manage and search engineering decisions and memory.")
console = Console()


@knowledge_app.command("search")
def search_knowledge_cmd(
    query: str = typer.Argument(..., help="Search query for engineering decisions, requirements, or lessons."),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project ID."),
) -> None:
    """Semantic search across project engineering decisions, requirements, findings, and lessons."""
    target_project = project or get_active_project_name() or "default_project"
    results = knowledge_service.search_knowledge(target_project, query)

    if not results:
        console.print(f"\n[dim]No matching knowledge entries found for query '{query}' in project '{target_project}'.[/dim]\n")
        return

    console.print(f"\n[bold cyan]ENGINEERING KNOWLEDGE SEARCH RESULTS[/bold cyan] ([dim]Project: {target_project}[/dim])\n")
    for r in results:
        status_color = "green" if r.status in ("APPROVED", "VALIDATED", "VERIFIED") else "yellow" if r.status == "PROPOSED" else "red" if r.status == "SUPERSEDED" else "white"
        authority_tag = "[CURRENT AUTHORITY]" if r.is_current_authority else f"[SUPERSEDED by {r.superseded_by or 'newer decision'}]"

        panel_content = (
            f"[bold]ID:[/bold]        {r.object_id}\n"
            f"[bold]Type:[/bold]      {r.object_type}\n"
            f"[bold]Category:[/bold]  {r.category}\n"
            f"[bold]Status:[/bold]    [{status_color}]{r.status}[/{status_color}] • {authority_tag}\n"
            f"[bold]Summary:[/bold]   {r.summary}\n"
        )
        border = "cyan" if r.is_current_authority else "yellow"
        console.print(Panel(panel_content, title=r.title, border_style=border))
    console.print()


@knowledge_app.command("decisions")
def list_decisions_cmd(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project ID."),
) -> None:
    """List all engineering decisions for active project."""
    target_project = project or get_active_project_name() or "default_project"
    decisions = knowledge_service.list_decisions(target_project)

    if not decisions:
        console.print(f"\n[dim]No engineering decisions recorded for project '{target_project}'.[/dim]\n")
        return

    table = Table(title=f"Engineering Decisions ({target_project})", border_style="cyan")
    table.add_column("Decision ID", style="bold cyan")
    table.add_column("Title")
    table.add_column("Category")
    table.add_column("Selected Option", style="bold")
    table.add_column("Status")
    table.add_column("Version")

    for d in decisions:
        status_color = "green" if d.status.value in ("APPROVED", "VALIDATED", "IMPLEMENTED") else "yellow" if d.status.value == "PROPOSED" else "red"
        table.add_row(
            d.decision_id,
            d.title,
            d.category.value,
            d.selected_option,
            f"[{status_color}]{d.status.value}[/{status_color}]",
            d.project_version or "N/A",
        )

    console.print()
    console.print(table)
    console.print()


@knowledge_app.command("requirements")
def list_requirements_cmd(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project ID."),
) -> None:
    """List engineering requirements for active project."""
    target_project = project or get_active_project_name() or "default_project"
    reqs = knowledge_service.list_requirements(target_project)

    if not reqs:
        console.print(f"\n[dim]No requirements recorded for project '{target_project}'.[/dim]\n")
        return

    table = Table(title=f"Engineering Requirements ({target_project})", border_style="cyan")
    table.add_column("Req ID", style="bold cyan")
    table.add_column("Title")
    table.add_column("Category")
    table.add_column("Target Value")
    table.add_column("Status")

    for r in reqs:
        status_color = "green" if r.status.value == "VERIFIED" else "yellow" if r.status.value == "PROPOSED" else "cyan"
        val_str = f"{r.value} {r.unit}" if r.value else "N/A"
        table.add_row(
            r.requirement_id,
            r.title,
            r.category.value,
            val_str,
            f"[{status_color}]{r.status.value}[/{status_color}]",
        )

    console.print()
    console.print(table)
    console.print()


@knowledge_app.command("findings")
def list_findings_cmd(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project ID."),
) -> None:
    """List engineering findings and failure records."""
    target_project = project or get_active_project_name() or "default_project"
    findings = knowledge_service.list_findings(target_project)

    if not findings:
        console.print(f"\n[dim]No findings recorded for project '{target_project}'.[/dim]\n")
        return

    table = Table(title=f"Engineering Findings ({target_project})", border_style="yellow")
    table.add_column("Finding ID", style="bold yellow")
    table.add_column("Title")
    table.add_column("Category")
    table.add_column("Severity")
    table.add_column("Status")

    for f in findings:
        table.add_row(
            f.finding_id,
            f.title,
            f.category,
            f.severity.value,
            f.status.value,
        )

    console.print()
    console.print(table)
    console.print()


@knowledge_app.command("lessons")
def list_lessons_cmd(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project ID."),
) -> None:
    """List engineering lessons learned and recommendations."""
    target_project = project or get_active_project_name() or "default_project"
    lessons = knowledge_service.list_lessons(target_project)

    if not lessons:
        console.print(f"\n[dim]No lessons recorded for project '{target_project}'.[/dim]\n")
        return

    console.print(f"\n[bold green]LESSONS LEARNED[/bold green] ({target_project})\n")
    for l in lessons:
        panel_text = (
            f"[bold]Context:[/bold]        {l.context}\n"
            f"[bold]Cause:[/bold]          {l.cause}\n"
            f"[bold]Impact:[/bold]         {l.impact}\n"
            f"[bold green]Recommendation:[/bold green] {l.recommendation}\n"
        )
        console.print(Panel(panel_text, title=f"{l.lesson_id} - {l.title}", border_style="green"))
    console.print()
