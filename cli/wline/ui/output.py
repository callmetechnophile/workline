"""Console output and formatting helpers for Workline CLI."""

import sys
from rich.console import Console

console = Console()


def is_unicode_supported() -> bool:
    """Check if stdout supports unicode symbols."""
    try:
        enc = getattr(sys.stdout, "encoding", "") or ""
        return "utf" in enc.lower()
    except Exception:
        return False


def print_success(message: str) -> None:
    """Print success message with checkmark."""
    symbol = "✓" if is_unicode_supported() else "[OK]"
    console.print(f"[bold green]{symbol}[/bold green] {message}")


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[bold yellow]Warning:[/bold yellow] {message}")


def print_info(message: str) -> None:
    """Print neutral info message."""
    symbol = "•" if is_unicode_supported() else "*"
    console.print(f"[cyan]{symbol}[/cyan] {message}")
