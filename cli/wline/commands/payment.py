"""CLI commands for Payment Status inspection."""

import asyncio
import typer
from rich.console import Console
from rich.panel import Panel

from backend.workline.orders.service import order_service

payment_app = typer.Typer(name="payment", help="Payment session verification and status inspection.")
console = Console()


@payment_app.command("status")
def payment_status(
    payment_id: str = typer.Argument(..., help="Payment Request ID or Session ID."),
):
    """Inspect live payment status and settlement timestamps."""
    async def _run():
        session = order_service.session_manager.get_session(payment_id)
        if not session:
            console.print(f"[yellow]Payment session '{payment_id}' not found.[/yellow]\n")
            return

        panel_text = (
            f"[bold]Payment Session:[/bold] {session.payment_session_id}\n"
            f"[bold]Order ID:[/bold]        {session.order_id}\n"
            f"[bold]Amount:[/bold]          ${session.amount:.2f} {session.asset}\n"
            f"[bold]Network:[/bold]         {session.network}\n"
            f"[bold]Status:[/bold]          [bold green]{session.status.value}[/bold green]\n"
            f"[bold]Recipient:[/bold]       {session.recipient}\n"
            f"[bold]Tx Hash:[/bold]         {session.external_payment_id or 'N/A'}\n"
            f"[bold]Authorized At:[/bold]   {session.authorized_at or 'Pending'}\n"
            f"[bold]Settled At:[/bold]      {session.settled_at or 'Pending'}"
        )
        console.print(Panel(panel_text, title=f"Payment Details: {session.payment_session_id}", border_style="cyan"))

    asyncio.run(_run())
