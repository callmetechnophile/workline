"""Engineering Decision management CLI commands."""

import secrets
from typing import Optional
from rich.console import Console
import typer

from backend.workline.knowledge import (
    Actor,
    ActorType,
    DecisionAlternative,
    DecisionCategory,
    DecisionEvidence,
    DecisionStatus,
    EngineeringDecision,
    EvidenceSourceType,
    knowledge_service,
)
from cli.wline.core.paths import get_active_project_name

decision_app = typer.Typer(name="decision", help="Manage engineering decisions, rationale, and approvals.")
console = Console()


@decision_app.command("create")
def create_decision_cmd(
    title: str = typer.Option(..., "--title", "-t", help="Title of the decision."),
    selected: str = typer.Option(..., "--selected", "-s", help="Chosen option / component / architecture."),
    rationale: str = typer.Option(..., "--rationale", "-r", help="Why this option was chosen."),
    problem: str = typer.Option("", "--problem", help="Engineering problem statement."),
    category: str = typer.Option("SYSTEM_ARCHITECTURE", "--category", "-c", help="Decision domain category."),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project ID."),
) -> None:
    """Create a new engineering decision."""
    target_project = project or get_active_project_name() or "default_project"
    cat_enum = DecisionCategory[category.upper()] if category.upper() in DecisionCategory.__members__ else DecisionCategory.SYSTEM_ARCHITECTURE
    dec_id = f"DEC-{secrets.token_hex(3).upper()}"

    decision = EngineeringDecision(
        decision_id=dec_id,
        project_id=target_project,
        title=title,
        description=rationale,
        category=cat_enum,
        status=DecisionStatus.APPROVED,
        created_by=Actor(actor_type=ActorType.HUMAN, actor_id="cli_user"),
        problem=problem or title,
        rationale=rationale,
        selected_option=selected,
    )

    created = knowledge_service.create_decision(decision)
    console.print(f"\n[bold green][OK] Decision created successfully:[/bold green] [bold cyan]{created.decision_id}[/bold cyan] ({created.title})\n")


@decision_app.command("approve")
def approve_decision_cmd(
    decision_id: str = typer.Argument(..., help="Decision ID to approve (e.g. DEC-101)."),
) -> None:
    """Approve a proposed engineering decision."""
    try:
        actor = Actor(actor_type=ActorType.HUMAN, actor_id="cli_approver")
        dec = knowledge_service.approve_decision(decision_id, actor=actor)
        console.print(f"\n[bold green][OK] Decision '{decision_id}' approved successfully.[/bold green]\n")
    except Exception as e:
        console.print(f"\n[bold red][ERROR][/bold red] Failed to approve decision: {e}\n")
        raise typer.Exit(code=1)


@decision_app.command("reject")
def reject_decision_cmd(
    decision_id: str = typer.Argument(..., help="Decision ID to reject."),
    reason: str = typer.Option("Rejected by user via CLI", "--reason", "-r", help="Reason for rejection."),
) -> None:
    """Reject an engineering decision."""
    try:
        actor = Actor(actor_type=ActorType.HUMAN, actor_id="cli_user")
        dec = knowledge_service.reject_decision(decision_id, actor=actor, reason=reason)
        console.print(f"\n[bold yellow][OK] Decision '{decision_id}' rejected.[/bold yellow]\n")
    except Exception as e:
        console.print(f"\n[bold red][ERROR][/bold red] Failed to reject decision: {e}\n")
        raise typer.Exit(code=1)


@decision_app.command("supersede")
def supersede_decision_cmd(
    old_decision_id: str = typer.Argument(..., help="Existing decision ID to supersede."),
    title: str = typer.Option(..., "--title", "-t", help="New decision title."),
    selected: str = typer.Option(..., "--selected", "-s", help="New chosen option."),
    rationale: str = typer.Option(..., "--rationale", "-r", help="Rationale for superseding."),
) -> None:
    """Supersede an existing decision with a new engineering decision."""
    try:
        old_dec = knowledge_service.get_decision(old_decision_id)
        if not old_dec:
            console.print(f"\n[bold red][ERROR][/bold red] Decision '{old_decision_id}' not found.\n")
            raise typer.Exit(code=1)

        new_id = f"DEC-{secrets.token_hex(3).upper()}"
        new_dec = EngineeringDecision(
            decision_id=new_id,
            project_id=old_dec.project_id,
            title=title,
            description=rationale,
            category=old_dec.category,
            status=DecisionStatus.APPROVED,
            created_by=Actor(actor_type=ActorType.HUMAN, actor_id="cli_user"),
            problem=old_dec.problem,
            rationale=rationale,
            selected_option=selected,
        )

        old, new = knowledge_service.supersede_decision(old_decision_id, new_dec, actor=Actor(actor_type=ActorType.HUMAN, actor_id="cli_user"))
        console.print(f"\n[bold green][OK] Decision '{old_decision_id}' superseded by '{new.decision_id}'.[/bold green]\n")
    except Exception as e:
        console.print(f"\n[bold red][ERROR][/bold red] Failed to supersede decision: {e}\n")
        raise typer.Exit(code=1)
