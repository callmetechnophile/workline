"""Requirement management CLI commands."""

import secrets
from typing import Optional
from rich.console import Console
import typer

from backend.workline.knowledge import (
    Actor,
    ActorType,
    EngineeringRequirement,
    RequirementCategory,
    RequirementPriority,
    RequirementStatus,
    knowledge_service,
)
from cli.wline.core.paths import get_active_project_name

requirement_app = typer.Typer(name="requirement", help="Manage engineering requirements and traceability.")
console = Console()


@requirement_app.command("create")
def create_requirement_cmd(
    title: str = typer.Option(..., "--title", "-t", help="Requirement statement."),
    category: str = typer.Option("ELECTRICAL", "--category", "-c", help="Domain category (ELECTRICAL, THERMAL, etc.)."),
    value: Optional[str] = typer.Option(None, "--value", "-v", help="Target quantitative metric value."),
    unit: Optional[str] = typer.Option(None, "--unit", "-u", help="Metric unit (e.g. V, A, °C)."),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project ID."),
) -> None:
    """Create a new formal engineering requirement."""
    target_project = project or get_active_project_name() or "default_project"
    cat_enum = RequirementCategory[category.upper()] if category.upper() in RequirementCategory.__members__ else RequirementCategory.FUNCTIONAL
    req_id = f"REQ-{secrets.token_hex(2).upper()}"

    req = EngineeringRequirement(
        requirement_id=req_id,
        project_id=target_project,
        title=title,
        description=title,
        category=cat_enum,
        priority=RequirementPriority.HIGH,
        value=value,
        unit=unit,
        status=RequirementStatus.PROPOSED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="cli_user"),
    )

    created = knowledge_service.create_requirement(req)
    console.print(f"\n[bold green][OK] Requirement created:[/bold green] [bold cyan]{created.requirement_id}[/bold cyan] ({created.title})\n")


@requirement_app.command("verify")
def verify_requirement_cmd(
    requirement_id: str = typer.Argument(..., help="Requirement ID to verify (e.g. REQ-01)."),
    validation_id: str = typer.Option("VAL-CLI", "--validation", help="Validation run reference ID."),
    passed: bool = typer.Option(True, "--pass/--fail", help="Whether verification passed."),
) -> None:
    """Record verification outcome for an engineering requirement."""
    try:
        actor = Actor(actor_type=ActorType.HUMAN, actor_id="cli_user")
        req = knowledge_service.verify_requirement(requirement_id, validation_id, passed=passed, actor=actor)
        status_color = "green" if passed else "red"
        console.print(f"\n[bold {status_color}][OK] Requirement '{requirement_id}' status updated to {req.status.value}.[/bold {status_color}]\n")
    except Exception as e:
        console.print(f"\n[bold red][ERROR][/bold red] Failed to verify requirement: {e}\n")
        raise typer.Exit(code=1)
