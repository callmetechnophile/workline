"""Lesson management CLI commands."""

import secrets
from typing import Optional
from rich.console import Console
from rich.panel import Panel
import typer

from backend.workline.knowledge import (
    Actor,
    ActorType,
    EngineeringLesson,
    knowledge_service,
)
from cli.wline.core.paths import get_active_project_name

lesson_app = typer.Typer(name="lesson", help="Manage engineering lessons learned and design recommendations.")
console = Console()


@lesson_app.command("create")
def create_lesson_cmd(
    title: str = typer.Option(..., "--title", "-t", help="Lesson title."),
    context: str = typer.Option(..., "--context", help="Engineering context (e.g. PCB thermal analysis)."),
    cause: str = typer.Option(..., "--cause", help="Identified root cause."),
    impact: str = typer.Option(..., "--impact", help="Observed impact."),
    recommendation: str = typer.Option(..., "--recommendation", "-r", help="Actionable future recommendation."),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project ID."),
) -> None:
    """Record an engineering lesson learned."""
    target_project = project or get_active_project_name() or "default_project"
    lid = f"LES-{secrets.token_hex(2).upper()}"

    lesson = EngineeringLesson(
        lesson_id=lid,
        project_id=target_project,
        title=title,
        description=recommendation,
        context=context,
        cause=cause,
        impact=impact,
        recommendation=recommendation,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="cli_user"),
    )

    created = knowledge_service.create_lesson(lesson)
    console.print(f"\n[bold green][OK] Lesson learned recorded:[/bold green] [bold cyan]{created.lesson_id}[/bold cyan] ({created.title})\n")


@lesson_app.command("list")
def list_lessons_cmd(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project ID."),
) -> None:
    """List recorded engineering lessons."""
    target_project = project or get_active_project_name() or "default_project"
    lessons = knowledge_service.list_lessons(target_project)

    if not lessons:
        console.print(f"\n[dim]No lessons recorded for project '{target_project}'.[/dim]\n")
        return

    for l in lessons:
        console.print(Panel(f"Context: {l.context}\nRecommendation: {l.recommendation}", title=f"{l.lesson_id} - {l.title}"))
