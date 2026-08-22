"""Rich banners and display headers for Workline CLI."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def print_main_banner() -> None:
    """Display the top-level Workline banner."""
    content = Text()
    content.append("WORKLINE\n", style="bold cyan")
    content.append("Engineering Lifecycle Platform", style="dim white")

    panel = Panel(
        content,
        expand=False,
        border_style="cyan",
        padding=(0, 6),
    )
    console.print(panel)


def print_section_header(title: str, subtitle: str = "") -> None:
    """Display a concise section title."""
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    if subtitle:
        console.print(f"[dim]{subtitle}[/dim]\n")
