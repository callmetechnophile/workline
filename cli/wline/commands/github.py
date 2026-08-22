"""Workline CLI GitHub subcommands for auth, initialization, connecting remotes, and push."""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel

from backend.workline.git.errors import (
    GitHubAuthError,
    GitHubRepoExistsError,
    GitError,
    RepositoryNotFoundError,
)
from backend.workline.git.github.auth import check_github_auth
from backend.workline.git.github.repository import github_repo_service
from backend.workline.git.service import git_service
from cli.wline.core.paths import get_active_project_name, get_workspace_dir
from cli.wline.core.workspace import find_project

github_app = typer.Typer(name="github", help="GitHub remote repository management and synchronization.")
console = Console()
github_auth_app = typer.Typer(name="auth", help="Inspect and manage GitHub authentication.")
github_app.add_typer(github_auth_app, name="auth")


def _resolve_project_dir(project_name: Optional[str] = None) -> Path:
    """Resolve local working directory for target project."""
    target = project_name if isinstance(project_name, str) and project_name.strip() else get_active_project_name()
    if not target:
        cwd = Path.cwd().resolve()
        if git_service.is_repository(cwd):
            return cwd
        console.print("[bold red][ERROR][/bold red] No active project selected. Run 'wline project open <name>' first.\n")
        raise typer.Exit(code=1)

    proj_info = find_project(target)
    if proj_info:
        return proj_info[0]

    ws_dir = get_workspace_dir() / target
    if ws_dir.exists():
        return ws_dir
    console.print(f"[bold red][ERROR][/bold red] Project '{target}' not found.\n")
    raise typer.Exit(code=1)


@github_auth_app.callback(invoke_without_command=True)
def github_auth_default(ctx: typer.Context) -> None:
    """Check GitHub authentication status."""
    if ctx.invoked_subcommand is not None:
        return
    github_auth_status_cmd()


@github_auth_app.command("status")
def github_auth_status_cmd() -> None:
    """Check and display GitHub authentication status."""
    auth = check_github_auth()
    if auth.authenticated:
        panel_text = (
            f"[bold]GitHub:[/bold] [bold green]Authenticated[/bold green]\n"
            f"[bold]User:[/bold]   [cyan]{auth.username}[/cyan]\n"
            f"[bold]Method:[/bold] {auth.auth_method.upper()}"
        )
        console.print(Panel(panel_text, title="GITHUB AUTHENTICATION", border_style="green"))
    else:
        panel_text = (
            f"[bold]GitHub:[/bold] [bold red]Not authenticated[/bold red]\n\n"
            f"[bold]Action:[/bold] {auth.error_message or 'Run gh auth login'}"
        )
        console.print(Panel(panel_text, title="GITHUB AUTHENTICATION", border_style="red"))
    console.print()


@github_app.command("init")
def github_init_cmd(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="GitHub repository name."),
    private: bool = typer.Option(True, "--private/--public", help="Repository visibility (private by default)."),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Repository description."),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name."),
    no_push: bool = typer.Option(False, "--no-push", help="Skip initial push to GitHub."),
) -> None:
    """Create a new GitHub repository, configure remote 'origin', and push initial commit."""
    proj_dir = _resolve_project_dir(project)

    console.print("\n[bold cyan]WORKLINE GITHUB PROJECT INITIALIZATION[/bold cyan]\n")
    console.print(f"[bold]Project:[/bold]    {proj_dir.name}")

    target_name = name or proj_dir.name
    desc_str = description or f"Workline Engineering Project: {proj_dir.name}"
    vis_str = "private" if private else "public"

    console.print(f"[bold]Repository:[/bold] {target_name}")
    console.print(f"[bold]Visibility:[/bold] {vis_str}\n")

    try:
        gh_repo, push_res = github_repo_service.initialize_github_repository(
            project_path=proj_dir,
            repo_name=target_name,
            private=private,
            description=desc_str,
            auto_push=not no_push,
        )
        console.print(f"[bold green]✓ GitHub authentication verified[/bold green]")
        console.print(f"[bold green]✓ Repository created:[/bold green] {gh_repo.full_name}")
        console.print(f"[bold green]✓ Remote 'origin' configured:[/bold green] {gh_repo.clone_url}")

        if not no_push and push_res and push_res.success:
            console.print(f"[bold green]✓ Initial commit pushed to origin[/bold green]")

        console.print(f"\n[bold]Repository URL:[/bold] [link={gh_repo.html_url}]{gh_repo.html_url}[/link]\n")
    except GitHubRepoExistsError as exc:
        console.print(f"\n[bold yellow]Repository already exists:[/bold yellow] {exc.repo_name}")
        console.print(f"[dim]Use 'wline github connect {exc.repo_name}' to link existing repository.[/dim]\n")
        raise typer.Exit(code=1)
    except GitHubAuthError as exc:
        console.print(f"\n[bold red][AUTH ERROR][/bold red] {str(exc)}\n")
        raise typer.Exit(code=1)
    except Exception as exc:
        console.print(f"\n[bold red][ERROR][/bold red] GitHub initialization failed: {str(exc)}\n")
        raise typer.Exit(code=1)


@github_app.command("connect")
def github_connect_cmd(
    repo: str = typer.Argument(..., help="GitHub repository specifier (e.g. 'owner/repo' or clone URL)."),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name."),
) -> None:
    """Connect an existing GitHub repository to this local project."""
    proj_dir = _resolve_project_dir(project)
    try:
        gh_repo = github_repo_service.connect_existing_repository(proj_dir, repo)
        console.print(f"\n[bold green]✓ Connected to existing GitHub repository:[/bold green] {gh_repo.full_name}")
        console.print(f"[bold green]✓ Remote 'origin' updated:[/bold green] {gh_repo.clone_url}\n")
    except Exception as exc:
        console.print(f"\n[bold red][ERROR][/bold red] Failed to connect repository: {str(exc)}\n")
        raise typer.Exit(code=1)


@github_app.command("remote")
def github_remote_cmd(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name."),
) -> None:
    """Display configured GitHub remote URL and tracking information."""
    proj_dir = _resolve_project_dir(project)
    remote_url = git_service.get_remote(proj_dir, "origin")
    if remote_url:
        console.print(f"\n[bold]Remote (origin):[/bold] [cyan]{remote_url}[/cyan]\n")
    else:
        console.print("\n[yellow]No GitHub remote configured. Run 'wline github init' or 'wline github connect'.[/yellow]\n")


@github_app.command("push")
def github_push_cmd(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name."),
    branch: Optional[str] = typer.Option(None, "--branch", "-b", help="Branch name."),
) -> None:
    """Push local commits to the configured GitHub repository."""
    proj_dir = _resolve_project_dir(project)
    curr_branch = branch or git_service.get_current_branch(proj_dir) or "main"
    remote_url = git_service.get_remote(proj_dir, "origin")

    if not remote_url:
        console.print("[bold red][ERROR][/bold red] No GitHub remote configured. Run 'wline github init' first.\n")
        raise typer.Exit(code=1)

    console.print(f"\n[bold]Pushing to GitHub:[/bold] {remote_url} ({curr_branch})...")
    res = git_service.push(proj_dir, remote="origin", branch=curr_branch, set_upstream=True)
    if res.success:
        console.print(f"[bold green]✓ GitHub push completed successfully.[/bold green]\n")
    else:
        console.print(f"[bold red]GitHub push failed:[/bold red] {res.stderr or res.stdout}\n")
        raise typer.Exit(code=1)
