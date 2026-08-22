"""Workline CLI Git subcommands for status, commits, logs, branches, tags, push, and pull."""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from backend.workline.git.errors import (
    GitError,
    RepositoryNotFoundError,
    SecretDetectedError,
    UncommittedChangesError,
)
from backend.workline.git.service import git_service
from cli.wline.core.paths import get_active_project_name, get_workspace_dir
from cli.wline.core.workspace import find_project

git_app = typer.Typer(name="git", help="Local Git repository version control commands.")
console = Console()
branch_app = typer.Typer(name="branch", help="Manage Git branches.")
git_app.add_typer(branch_app, name="branch")


def _resolve_project_dir(project_name: Optional[str] = None) -> Path:
    """Resolve local working directory for target project."""
    target = project_name if isinstance(project_name, str) and project_name.strip() else get_active_project_name()
    if not target:
        # Check current working directory
        cwd = Path.cwd().resolve()
        if git_service.is_repository(cwd):
            return cwd
        console.print("[bold red][ERROR][/bold red] No active project selected. Run 'wline project open <name>' first.\n")
        raise typer.Exit(code=1)

    proj_info = find_project(target)
    if proj_info:
        return proj_info[0]

    # Check in workspace dir
    ws_dir = get_workspace_dir() / target
    if ws_dir.exists():
        return ws_dir
    console.print(f"[bold red][ERROR][/bold red] Project '{target}' not found.\n")
    raise typer.Exit(code=1)


@git_app.command("status")
def git_status_cmd(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name."),
) -> None:
    """Inspect local working tree, branch, commit, and remote synchronization status."""
    proj_dir = _resolve_project_dir(project)
    try:
        status = git_service.get_status(proj_dir)
    except RepositoryNotFoundError:
        console.print(f"[yellow]Directory '{proj_dir.name}' is not a Git repository. Run 'wline init {proj_dir.name}' first.[/yellow]\n")
        return

    working_tree_str = "[bold green]CLEAN[/bold green]" if status.is_clean else "[bold yellow]MODIFIED[/bold yellow]"
    sync_str = f"[bold green]{status.sync_status.value}[/bold green]" if status.sync_status.value == "UP_TO_DATE" else f"[bold yellow]{status.sync_status.value}[/bold yellow]"
    remote_str = status.remote_url or "NO REMOTE CONFIGURED"

    details = (
        f"[bold]Project:[/bold]      {proj_dir.name}\n"
        f"[bold]Branch:[/bold]       {status.branch}\n"
        f"[bold]Commit:[/bold]       {status.short_commit or 'None'}\n"
        f"[bold]Working tree:[/bold] {working_tree_str}\n"
        f"[bold]Remote:[/bold]       {remote_str}\n"
        f"[bold]Sync:[/bold]         {sync_str}"
    )
    console.print(Panel(details, title="WORKLINE GIT STATUS", border_style="cyan"))

    if status.staged_files:
        console.print("\n[bold green]Staged changes:[/bold green]")
        for f in status.staged_files:
            console.print(f"  [green]+ {f}[/green]")

    if status.modified_files:
        console.print("\n[bold yellow]Unstaged changes:[/bold yellow]")
        for f in status.modified_files:
            console.print(f"  [yellow]M {f}[/yellow]")

    if status.untracked_files:
        console.print("\n[bold red]Untracked files:[/bold red]")
        for f in status.untracked_files:
            console.print(f"  [dim red]? {f}[/dim red]")
    console.print()


@git_app.command("commit")
def git_commit_cmd(
    message: str = typer.Option(..., "--message", "-m", help="Commit message."),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name."),
    author: str = typer.Option("Workline Engineer", "--author", help="Author name."),
    email: str = typer.Option("engineer@workline.dev", "--email", help="Author email."),
) -> None:
    """Create a validated Git commit with automatic secret and credential scanning."""
    proj_dir = _resolve_project_dir(project)

    try:
        commit = git_service.create_commit(
            path=proj_dir,
            message=message,
            author_name=author,
            author_email=email,
            stage_all=True,
            scan_secrets=True,
        )
        console.print(f"\n[bold green]✓ Commit created:[/bold green] [cyan]{commit.short_hash}[/cyan] - {commit.message}")
        console.print(f"[dim]Author: {commit.author} <{commit.email}> | Branch: {commit.branch}[/dim]\n")
    except SecretDetectedError as exc:
        console.print("\n[bold red]COMMIT BLOCKED: Potential secret detected[/bold red]")
        console.print(f"[red]{str(exc)}[/red]\n")
        raise typer.Exit(code=1)
    except GitError as exc:
        console.print(f"\n[bold red][ERROR][/bold red] {str(exc)}\n")
        raise typer.Exit(code=1)


@git_app.command("log")
def git_log_cmd(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name."),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of commits to display."),
) -> None:
    """Display concise project commit history."""
    proj_dir = _resolve_project_dir(project)
    commits = git_service.get_log(proj_dir, limit=limit)
    if not commits:
        console.print("[dim]No commit history found.[/dim]\n")
        return

    table = Table(title=f"Git Log: {proj_dir.name} (last {len(commits)} commits)")
    table.add_column("Commit", style="bold cyan")
    table.add_column("Author", style="white")
    table.add_column("Date", style="magenta")
    table.add_column("Message", style="green")

    for c in commits:
        table.add_row(c.short_hash, c.author, c.timestamp[:19].replace("T", " "), c.message)
    console.print(table)
    console.print()


@git_app.command("push")
def git_push_cmd(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name."),
    remote: str = typer.Option("origin", "--remote", "-r", help="Remote name."),
    branch: Optional[str] = typer.Option(None, "--branch", "-b", help="Branch name to push."),
    tags: bool = typer.Option(False, "--tags", help="Push all tags."),
) -> None:
    """Push local commits and tags to remote repository."""
    proj_dir = _resolve_project_dir(project)
    curr_branch = branch or git_service.get_current_branch(proj_dir) or "main"
    remote_url = git_service.get_remote(proj_dir, remote)

    if not remote_url:
        console.print(f"[bold red][ERROR][/bold red] Remote '{remote}' is not configured. Run 'wline github init' or 'wline github connect' first.\n")
        raise typer.Exit(code=1)

    console.print(f"\n[bold]Branch:[/bold]  {curr_branch}")
    console.print(f"[bold]Remote:[/bold]  {remote} ({remote_url})\n")

    res = git_service.push(proj_dir, remote=remote, branch=curr_branch, set_upstream=True, tags=tags)
    if res.success:
        console.print(f"[bold green]✓ Push completed successfully to {remote}/{curr_branch}[/bold green]\n")
    else:
        console.print(f"[bold red]Push failed:[/bold red] {res.stderr or res.stdout}\n")
        raise typer.Exit(code=1)


@git_app.command("pull")
def git_pull_cmd(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name."),
    remote: str = typer.Option("origin", "--remote", "-r", help="Remote name."),
    branch: Optional[str] = typer.Option(None, "--branch", "-b", help="Branch name."),
) -> None:
    """Pull latest updates from remote repository."""
    proj_dir = _resolve_project_dir(project)
    try:
        res = git_service.pull(proj_dir, remote=remote, branch=branch)
        if res.success:
            console.print(f"[bold green]✓ Pull completed successfully from {remote}[/bold green]\n")
        else:
            console.print(f"[bold red]Pull failed:[/bold red] {res.stderr or res.stdout}\n")
            raise typer.Exit(code=1)
    except UncommittedChangesError as exc:
        console.print(f"[bold red][BLOCK][/bold red] {str(exc)}\n")
        raise typer.Exit(code=1)


@git_app.command("checkout")
def git_checkout_cmd(
    name: str = typer.Argument(..., help="Branch name to switch to."),
    create: bool = typer.Option(False, "--create", "-b", help="Create new branch if it does not exist."),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name."),
) -> None:
    """Switch branches or create and switch."""
    proj_dir = _resolve_project_dir(project)
    res = git_service.switch_branch(proj_dir, name, create=create)
    if res.success:
        console.print(f"[bold green]✓ Switched to branch '{name}'[/bold green]\n")
    else:
        console.print(f"[bold red]Checkout failed:[/bold red] {res.stderr or res.stdout}\n")
        raise typer.Exit(code=1)


@branch_app.callback(invoke_without_command=True)
def branch_list_cmd(
    ctx: typer.Context,
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name."),
) -> None:
    """List all local Git branches."""
    if ctx.invoked_subcommand is not None:
        return
    proj_dir = _resolve_project_dir(project)
    branches = git_service.list_branches(proj_dir)
    if not branches:
        console.print("[dim]No branches found.[/dim]\n")
        return

    table = Table(title=f"Branches for {proj_dir.name}")
    table.add_column("Branch", style="bold cyan")
    table.add_column("Current", style="green", justify="center")
    table.add_column("Latest Commit", style="white")

    for b in branches:
        table.add_row(b.name, "✓" if b.is_current else "", b.commit_hash[:7] if b.commit_hash else "")
    console.print(table)
    console.print()


@branch_app.command("create")
def branch_create_cmd(
    name: str = typer.Argument(..., help="New branch name."),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name."),
) -> None:
    """Create a new Git branch."""
    proj_dir = _resolve_project_dir(project)
    res = git_service.create_branch(proj_dir, name)
    if res.success:
        console.print(f"[bold green]✓ Branch '{name}' created.[/bold green]\n")
    else:
        console.print(f"[bold red]Branch creation failed:[/bold red] {res.stderr or res.stdout}\n")
        raise typer.Exit(code=1)


@branch_app.command("delete")
def branch_delete_cmd(
    name: str = typer.Argument(..., help="Branch name to delete."),
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion (-D)."),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name."),
) -> None:
    """Delete a local Git branch."""
    proj_dir = _resolve_project_dir(project)
    res = git_service.delete_branch(proj_dir, name, force=force)
    if res.success:
        console.print(f"[bold green]✓ Branch '{name}' deleted.[/bold green]\n")
    else:
        console.print(f"[bold red]Branch deletion failed:[/bold red] {res.stderr or res.stdout}\n")
        raise typer.Exit(code=1)


@git_app.command("tag")
def git_tag_cmd(
    version: str = typer.Argument(..., help="Tag name (e.g. v0.1.0)."),
    message: Optional[str] = typer.Option(None, "--message", "-m", help="Tag annotation message."),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name."),
) -> None:
    """Create a Git tag for the current commit."""
    proj_dir = _resolve_project_dir(project)
    try:
        tag = git_service.create_tag(proj_dir, version, message=message)
        console.print(f"\n[bold green]✓ Git tag created:[/bold green] [bold cyan]{tag.name}[/bold cyan] -> {tag.commit_hash[:7]}\n")
    except GitError as exc:
        console.print(f"[bold red]Tag creation failed:[/bold red] {str(exc)}\n")
        raise typer.Exit(code=1)
