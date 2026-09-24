"""
Implementation of `wline --apis` interactive API Configuration Manager.

Configures external integrations into machine-local secure storage (~/.workline/credentials.json)
without storing secrets inside portable .wl project files.
"""

from typing import Dict, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich import box

from cli.wline.core.credentials import (
    APICredentialManager,
    APIProviderDescriptor,
    REGISTERED_PROVIDERS,
)

console = Console()


def apis_status_command(profile: Optional[str] = None) -> None:
    """Show status of all registered API providers without exposing secrets."""
    prof = profile or APICredentialManager.get_active_profile()
    console.print(f"\n[bold white]WORKLINE API STATUS[/bold white] [dim](Profile: [bold cyan]{prof}[/bold cyan])[/dim]\n")

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    table.add_column("Provider", width=22)
    table.add_column("Category", width=14, style="dim")
    table.add_column("Status", width=16)
    table.add_column("Details", style="dim")

    for pid, desc in REGISTERED_PROVIDERS.items():
        res = APICredentialManager.check_provider_status(pid, prof)
        status = res["status"]
        if status == "READY":
            s_color = "green"
        elif status == "INCOMPLETE":
            s_color = "yellow"
        else:
            s_color = "dim"

        table.add_row(
            desc.name,
            desc.category,
            f"[{s_color}]{status}[/{s_color}]",
            res.get("detail", ""),
        )

    console.print(table)
    console.print("[dim]Secrets are stored securely in ~/.workline/credentials.json and never exported into .wl files.[/dim]\n")


def apis_reset_command(
    provider: Optional[str] = typer.Argument(None, help="Provider ID to reset"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Profile name"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Remove local configuration for a provider after confirmation."""
    prof = profile or APICredentialManager.get_active_profile()
    target = provider

    if not target:
        console.print("\n[bold]Select provider to remove local configuration:[/bold]")
        p_list = list(REGISTERED_PROVIDERS.keys())
        for idx, pid in enumerate(p_list, 1):
            console.print(f"  [{idx}] {REGISTERED_PROVIDERS[pid].name} ({pid})")
        sel = Prompt.ask("\nEnter number or provider ID", default="1")
        if sel.isdigit() and 1 <= int(sel) <= len(p_list):
            target = p_list[int(sel) - 1]
        elif sel in REGISTERED_PROVIDERS:
            target = sel
        else:
            console.print("[red]Invalid selection.[/red]")
            return

    desc = REGISTERED_PROVIDERS.get(target)
    name = desc.name if desc else target

    if not yes:
        confirmed = Confirm.ask(
            f"Remove local configuration for [bold red]{name}[/bold red] in profile '{prof}'?",
            default=False,
        )
        if not confirmed:
            console.print("[yellow]Cancelled.[/yellow]")
            return

    removed = APICredentialManager.remove_provider_credentials(target, prof)
    if removed:
        console.print(f"[bold green]✓[/bold green] Removed local configuration for {name}.")
    else:
        console.print(f"[dim]No configuration found for {name} to remove.[/dim]")


def apis_interactive_manager(profile: Optional[str] = None) -> None:
    """Interactive menu-driven API configuration manager."""
    prof = profile or APICredentialManager.get_active_profile()

    while True:
        console.print("\n[bold white]WORKLINE API CONFIGURATION[/bold white]")
        console.print(f"Profile: [bold cyan]{prof}[/bold cyan]")
        console.print("------------------------------------------")
        console.print("Configure external integrations.\n")
        console.print("  [1] AI / Model Providers (Bedrock, NVIDIA NIM, OpenAI, Anthropic)")
        console.print("  [2] Research APIs (Tavily)")
        console.print("  [3] Engineering / Component Data (Nexar / Octopart)")
        console.print("  [4] Git Providers (GitHub)")
        console.print("  [5] Realtime Services (LiveKit)")
        console.print("  [6] Switch / Manage Profiles")
        console.print("  [7] Review Configuration Status")
        console.print("  [8] Reset a Provider")
        console.print("  [0] Exit")

        choice = Prompt.ask("\nSelect option", default="7")

        if choice == "0":
            break
        elif choice == "1":
            _configure_category("model", prof)
        elif choice == "2":
            _configure_category("research", prof)
        elif choice == "3":
            _configure_category("engineering", prof)
        elif choice == "4":
            _configure_category("git", prof)
        elif choice == "5":
            _configure_category("realtime", prof)
        elif choice == "6":
            _manage_profiles()
            prof = APICredentialManager.get_active_profile()
        elif choice == "7":
            apis_status_command(prof)
        elif choice == "8":
            apis_reset_command(profile=prof)
        else:
            console.print("[red]Invalid selection.[/red]")


def _configure_category(category: str, profile: str) -> None:
    providers = [p for p in REGISTERED_PROVIDERS.values() if p.category == category]
    if not providers:
        console.print("[dim]No providers in this category.[/dim]")
        return

    console.print(f"\n[bold]{category.title()} Providers:[/bold]")
    for idx, p in enumerate(providers, 1):
        status = APICredentialManager.check_provider_status(p.id, profile)["status"]
        s_color = "green" if status == "READY" else "dim"
        console.print(f"  [{idx}] {p.name} [{s_color}]({status})[/{s_color}] — {p.description}")

    sel = Prompt.ask("Select provider to configure (or press Enter to return)", default="")
    if not sel.strip():
        return

    target: Optional[APIProviderDescriptor] = None
    if sel.isdigit() and 1 <= int(sel) <= len(providers):
        target = providers[int(sel) - 1]
    else:
        for p in providers:
            if p.id.lower() == sel.lower() or p.name.lower() == sel.lower():
                target = p
                break

    if not target:
        console.print("[red]Invalid choice.[/red]")
        return

    _prompt_and_save_provider(target, profile)


def _prompt_and_save_provider(desc: APIProviderDescriptor, profile: str) -> None:
    console.print(f"\n[bold]Configure {desc.name}[/bold]")
    console.print(f"[dim]{desc.description}[/dim]\n")

    current = APICredentialManager.get_provider_credentials(desc.id, profile)
    new_creds: Dict[str, str] = {}

    for field_name in desc.fields:
        default_val = current.get(field_name, "")
        prompt_label = field_name.replace("_", " ").title()
        is_password = any(k in field_name.lower() for k in ("key", "secret", "token", "password"))

        if default_val and is_password:
            display_default = default_val[:4] + "..." + default_val[-4:] if len(default_val) > 8 else "****"
            console.print(f"Current {prompt_label}: [dim]{display_default}[/dim]")

        val = Prompt.ask(
            f"Enter {prompt_label}",
            default=default_val if not is_password else "",
            password=is_password,
        )

        if not val and default_val:
            new_creds[field_name] = default_val
        elif val:
            new_creds[field_name] = val.strip()

    if new_creds:
        APICredentialManager.set_provider_credentials(desc.id, new_creds, profile)
        console.print(f"[bold green]✓[/bold green] Saved credentials for [bold]{desc.name}[/bold] in profile '{profile}'.")
    else:
        console.print("[dim]No changes made.[/dim]")


def _manage_profiles() -> None:
    console.print("\n[bold]Profile Manager[/bold]")
    profiles = APICredentialManager.list_profiles()
    active = APICredentialManager.get_active_profile()

    for idx, p in enumerate(profiles, 1):
        mark = "[bold green]*[/bold green]" if p == active else " "
        console.print(f"  {mark} [{idx}] {p}")

    console.print("\nOptions: [1..N] Switch profile | [N] Create new profile | [Enter] Back")
    inp = Prompt.ask("Action", default="")
    if not inp.strip():
        return

    if inp.isdigit() and 1 <= int(inp) <= len(profiles):
        chosen = profiles[int(inp) - 1]
        APICredentialManager.set_active_profile(chosen)
        console.print(f"[bold green]✓[/bold green] Active profile switched to '{chosen}'.")
    else:
        new_name = inp.strip().lower().replace(" ", "-")
        APICredentialManager.set_active_profile(new_name)
        console.print(f"[bold green]✓[/bold green] Created and activated profile '{new_name}'.")
