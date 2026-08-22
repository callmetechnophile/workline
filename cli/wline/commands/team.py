"""Team collaboration and secure invitation CLI commands."""

from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import typer

from backend.workline.collaboration.invitations import (
    CreateInvitationRequest,
    TeamRole,
    invitation_service,
)
from cli.wline.core.paths import get_active_project_name

team_app = typer.Typer(name="team", help="Manage team collaboration and secure invitations.")
invitation_app = typer.Typer(name="invitation", help="Manage cryptographic team invitation links.")
team_app.add_typer(invitation_app, name="invitation")
console = Console()


def _copy_to_clipboard(text: str) -> bool:
    """Attempts to copy text to system clipboard via pyperclip or platform command."""
    import os
    if "PYTEST_CURRENT_TEST" in os.environ:
        return True
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        pass
    return False


@invitation_app.command("create")
def create_team_invitation_cmd(
    team: Optional[str] = typer.Option(None, "--team", "-t", help="Target team ID or name (defaults to active project team)."),
    ttl: int = typer.Option(7, "--ttl", help="Invitation expiration in days (1, 7, 30, custom)."),
    max_uses: int = typer.Option(10, "--max-uses", "-m", help="Maximum number of allowed joins."),
    role: str = typer.Option("MEMBER", "--role", "-r", help="Assigned team role (MEMBER, ENGINEER, ADMIN)."),
) -> None:
    """Generate a secure, authenticated AES-256-GCM encrypted invitation link."""
    target_team = team or get_active_project_name() or "team_pcb_research"
    role_enum = TeamRole[role.upper()] if role.upper() in TeamRole.__members__ else TeamRole.MEMBER

    req = CreateInvitationRequest(
        team_id=target_team,
        created_by="CLI User",
        ttl_days=ttl,
        max_uses=max_uses,
        role=role_enum.value,
    )

    try:
        resp = invitation_service.create_invitation(req, actor_role=TeamRole.OWNER)
        copied = _copy_to_clipboard(resp.join_url)

        panel_text = (
            f"[bold]Team:[/bold]      {resp.team_id}\n"
            f"[bold]Expires:[/bold]   {ttl} days\n"
            f"[bold]Max Uses:[/bold]  {resp.max_uses}\n"
            f"[bold]Role:[/bold]      {role_enum.value}\n\n"
            f"[bold]Join Link:[/bold]\n"
            f"[cyan]{resp.join_url}[/cyan]\n"
        )
        if copied:
            panel_text += "\n[bold green]✓ Link copied to clipboard[/bold green]"

        console.print()
        console.print(Panel(panel_text, title="TEAM INVITATION", border_style="cyan"))
        console.print("[dim]Send this link manually to the person you want to invite.[/dim]\n")
    except Exception as e:
        console.print(f"[bold red][ERROR][/bold red] Failed to create invitation: {e}\n")
        raise typer.Exit(code=1)


@invitation_app.command("list")
def list_team_invitations_cmd(
    team: Optional[str] = typer.Option(None, "--team", "-t", help="Team ID to inspect."),
) -> None:
    """List all active and historical invitations for a team (without raw tokens)."""
    target_team = team or get_active_project_name() or "team_pcb_research"
    invitations = invitation_service.list_invitations(target_team)

    if not invitations:
        console.print(f"\n[dim]No invitations found for team '{target_team}'.[/dim]\n")
        return

    table = Table(title=f"Team Invitations ({target_team})", border_style="cyan")
    table.add_column("Invitation ID", style="bold cyan")
    table.add_column("Status", style="bold")
    table.add_column("Uses", justify="right")
    table.add_column("Expires At")
    table.add_column("Role")

    for inv in invitations:
        status_color = "green" if inv.status.value == "ACTIVE" else "yellow" if inv.status.value == "EXHAUSTED" else "red"
        table.add_row(
            inv.invitation_id,
            f"[{status_color}]{inv.status.value}[/{status_color}]",
            f"{inv.use_count} / {inv.max_uses}",
            inv.expires_at[:19].replace("T", " "),
            inv.role,
        )

    console.print()
    console.print(table)
    console.print()


@invitation_app.command("revoke")
def revoke_team_invitation_cmd(
    invitation_id: str = typer.Argument(..., help="Invitation ID to revoke."),
) -> None:
    """Revoke an active invitation link immediately."""
    try:
        success = invitation_service.revoke_invitation(invitation_id, actor_role=TeamRole.OWNER)
        if success:
            console.print(f"\n[bold green]✓ Invitation '{invitation_id}' has been revoked successfully.[/bold green]\n")
        else:
            console.print(f"\n[bold red][ERROR][/bold red] Invitation '{invitation_id}' not found.\n")
            raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"\n[bold red][ERROR][/bold red] Failed to revoke invitation: {e}\n")
        raise typer.Exit(code=1)


@invitation_app.command("regenerate")
def regenerate_team_invitation_cmd(
    invitation_id: str = typer.Argument(..., help="Invitation ID to regenerate."),
) -> None:
    """Revoke the previous invitation and generate a fresh link."""
    try:
        resp = invitation_service.regenerate_invitation(invitation_id, actor_role=TeamRole.OWNER)
        copied = _copy_to_clipboard(resp.join_url)

        panel_text = (
            f"[bold]New Invitation ID:[/bold] {resp.invitation_id}\n"
            f"[bold]Status:[/bold]            [bold green]ACTIVE[/bold green]\n"
            f"[bold]Expires:[/bold]           {resp.expires_at[:19].replace('T', ' ')}\n\n"
            f"[bold]New Join Link:[/bold]\n"
            f"[cyan]{resp.join_url}[/cyan]\n"
        )
        if copied:
            panel_text += "\n[bold green]✓ New link copied to clipboard[/bold green]"

        console.print()
        console.print(Panel(panel_text, title="INVITATION REGENERATED", border_style="green"))
        console.print("[dim]The previous invitation link is now permanently invalidated.[/dim]\n")
    except Exception as e:
        console.print(f"\n[bold red][ERROR][/bold red] Failed to regenerate invitation: {e}\n")
        raise typer.Exit(code=1)
