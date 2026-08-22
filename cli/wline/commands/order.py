"""CLI commands for Workline Item Ordering, preview, approval, and lifecycle tracking."""

import asyncio
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cli.wline.core.paths import get_active_project_name
from backend.workline.orders.models import OrderStatus, PaymentStatus
from backend.workline.orders.service import order_service

order_app = typer.Typer(name="order", help="Item ordering, approvals, payment authorization, and status tracking.")
console = Console()


@order_app.command("create")
def order_create(
    bom_id: str = typer.Argument(..., help="BOM ID or Project name to construct Order Plan from."),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name."),
):
    """Generate an itemized Order Plan and draft Orders from an approved BOM."""
    proj_name = project or get_active_project_name() or bom_id

    async def _run():
        console.print(f"\n[bold cyan]CREATING ORDER PLAN FROM BOM:[/bold cyan] {bom_id}\n")
        try:
            plan = await order_service.create_order_plan(proj_name, bom_id)
            orders = await order_service.create_orders_from_plan(plan, user_role="ENGINEER")

            console.print(f"[bold green][OK] Order Plan Created ({plan.plan_id})[/bold green] — {len(orders)} Vendor Order(s)\n")

            for ord in orders:
                panel_text = (
                    f"[bold]Order ID:[/bold]       {ord.order_id}\n"
                    f"[bold]Vendor:[/bold]         {ord.vendor}\n"
                    f"[bold]Execution Mode:[/bold] {ord.execution_mode.value}\n"
                    f"[bold]Status:[/bold]         [yellow]{ord.status.value}[/yellow]\n"
                    f"[bold]Subtotal:[/bold]       {ord.currency} {ord.subtotal:.2f}\n"
                    f"[bold]Shipping:[/bold]       {ord.currency} {ord.shipping_cost:.2f}\n"
                    f"[bold]Tax (GST):[/bold]     {ord.currency} {ord.tax:.2f}\n"
                    f"[bold green]TOTAL:[/bold green]          [bold green]{ord.currency} {ord.total:.2f}[/bold green]\n"
                    f"[bold]Line Items:[/bold]     {len(ord.items)}"
                )
                console.print(Panel(panel_text, title=f"Draft Order: {ord.order_id}", border_style="cyan"))

            console.print("[dim]Next steps: Run 'wline order preview <order-id>' and 'wline order approve <order-id>'.[/dim]\n")
        except Exception as exc:
            console.print(f"[bold red][ERROR][/bold red] Order creation failed: {str(exc)}\n")

    asyncio.run(_run())


@order_app.command("preview")
def order_preview(
    order_id: str = typer.Argument(..., help="Order ID to preview (e.g. WL-ORD-XXXXXX)."),
):
    """Display comprehensive financial breakdown, items, and live revalidated prices."""
    async def _run():
        order = await order_service.get_order(order_id)
        if not order:
            console.print(f"[yellow]Warning: Order '{order_id}' not found.[/yellow]\n")
            return

        _, report = await order_service.revalidate_order(order_id)

        console.print(f"\n[bold cyan]ORDER PREVIEW:[/bold cyan] {order.order_id}\n")

        table = Table(title=f"Line Items for {order.vendor}")
        table.add_column("Component / MPN", style="white")
        table.add_column("Qty", style="cyan", justify="right")
        table.add_column("Unit Price", style="green", justify="right")
        table.add_column("Ext. Price", style="green", justify="right")
        table.add_column("Stock Check", style="magenta")

        for item in order.items:
            rev_match = next((r for r in report.items if r.mpn == item.mpn), None)
            stock_str = "AVAILABLE" if (rev_match and rev_match.is_available) else "CHECK"
            table.add_row(
                f"{item.manufacturer} {item.mpn}",
                str(item.quantity),
                f"{item.currency} {item.unit_price:.2f}",
                f"{item.currency} {item.extended_price:.2f}",
                stock_str,
            )

        console.print(table)

        summary_text = (
            f"[bold]Subtotal:[/bold]       {order.currency} {order.subtotal:.2f}\n"
            f"[bold]Shipping:[/bold]       {order.currency} {order.shipping_cost:.2f} (ESTIMATED)\n"
            f"[bold]Tax (18%):[/bold]      {order.currency} {order.tax:.2f}\n"
            f"[bold green]TOTAL:[/bold green]          [bold green]{order.currency} {order.total:.2f}[/bold green]\n"
            f"[bold]Status:[/bold]         {order.status.value}\n"
            f"[bold]Price Changes:[/bold]  {report.price_changes_count}\n"
            f"[bold]Stock Changes:[/bold]  {report.stock_changes_count}"
        )
        console.print(Panel(summary_text, title="Order Financials & Revalidation", border_style="green"))

    asyncio.run(_run())


@order_app.command("approve")
def order_approve(
    order_id: str = typer.Argument(..., help="Order ID to approve."),
    by: str = typer.Option("Lead Systems Engineer", "--by", help="Name/Title of approving engineer."),
    role: str = typer.Option("OWNER", "--role", help="Approver role (OWNER, ADMIN, LEAD_ENGINEER)."),
):
    """Human approval action transitioning order from READY_FOR_APPROVAL to APPROVED."""
    async def _run():
        ok, order, err = await order_service.approve_order(
            order_id=order_id,
            user_role=role,
            approved_by=by,
            is_agent=False,
        )
        if not ok:
            console.print(f"[bold red][APPROVAL REJECTED][/bold red] {err}\n")
            return

        console.print(f"\n[bold green][OK] Order '{order.order_id}' has been APPROVED by {by}![/bold green]")
        console.print(f"Status:         [yellow]{order.status.value}[/yellow]")
        console.print(f"Payment Status: [cyan]{order.payment_status.value}[/cyan]")
        console.print(f"Next action:    Run 'wline order pay {order.order_id}' to generate x402 payment challenge.\n")

    asyncio.run(_run())


@order_app.command("pay")
def order_pay(
    order_id: str = typer.Argument(..., help="Order ID to pay."),
    simulate_success: bool = typer.Option(True, "--simulate-success/--no-simulate", help="Simulate wallet authorization proof."),
):
    """Generate x402 payment challenge and authorize payment for an approved order."""
    async def _run():
        order = await order_service.get_order(order_id)
        if not order:
            console.print(f"[yellow]Order '{order_id}' not found.[/yellow]\n")
            return

        # 1. Create Payment Request
        ok_req, pay_req, req_err = await order_service.create_payment_request(order_id)
        if not ok_req or not pay_req:
            console.print(f"[bold red][ERROR][/bold red] Could not create payment request: {req_err}\n")
            return

        console.print(f"\n[bold cyan]x402 PAYMENT REQUIRED[/bold cyan]")
        challenge_text = (
            f"[bold]Order ID:[/bold]       {pay_req.order_id}\n"
            f"[bold]Amount:[/bold]         ${pay_req.amount:.2f} {pay_req.asset}\n"
            f"[bold]Network:[/bold]        {pay_req.network}\n"
            f"[bold]Recipient:[/bold]      {pay_req.recipient}\n"
            f"[bold]Expires At:[/bold]     {pay_req.expires_at}\n"
            f"[bold]Idempotency Key:[/bold] {pay_req.idempotency_key}"
        )
        console.print(Panel(challenge_text, title="Cryptographic Payment Challenge", border_style="yellow"))

        if simulate_success:
            console.print("[dim]Simulating wallet cryptographic proof signature...[/dim]")
            proof = {"tx_hash": f"0xSimulatedProof_{order_id}_402Auth"}
            ok_pay, updated_order, receipt, err = await order_service.verify_payment_and_execute(
                order_id=order_id,
                payment_id=pay_req.payment_request_id,
                signed_proof=proof,
            )
            if not ok_pay:
                console.print(f"[bold red][PAYMENT / ORDER FAILED][/bold red] {err}\n")
                return

            console.print(f"[bold green][OK] Payment Verified & Authorized![/bold green]")
            console.print(f"Order Status:   [bold green]{updated_order.status.value}[/bold green]")
            if updated_order.external_order_id:
                console.print(f"Vendor Order:   {updated_order.external_order_id}")
            if receipt:
                console.print(f"Receipt ID:     {receipt.receipt_id}")
            console.print()

    asyncio.run(_run())


@order_app.command("status")
def order_status(
    order_id: str = typer.Argument(..., help="Order ID to inspect."),
):
    """Display live order status, external vendor references, and execution milestones."""
    async def _run():
        order = await order_service.get_order(order_id)
        if not order:
            console.print(f"[yellow]Order '{order_id}' not found.[/yellow]\n")
            return

        panel_text = (
            f"[bold]Order ID:[/bold]          {order.order_id}\n"
            f"[bold]Project:[/bold]           {order.project_id}\n"
            f"[bold]Vendor:[/bold]            {order.vendor}\n"
            f"[bold]Execution Mode:[/bold]    {order.execution_mode.value}\n"
            f"[bold]Order Status:[/bold]      [bold green]{order.status.value}[/bold green]\n"
            f"[bold]Payment Status:[/bold]    [cyan]{order.payment_status.value}[/cyan]\n"
            f"[bold]Approval Status:[/bold]   {order.approval_status.value} ({order.approved_by or 'Pending'})\n"
            f"[bold]Total Cost:[/bold]        {order.currency} {order.total:.2f}\n"
            f"[bold]External Order ID:[/bold] {order.external_order_id or 'N/A'}\n"
            f"[bold]Receipt ID:[/bold]        {order.receipt_id or 'N/A'}\n"
            f"[bold]Created:[/bold]           {order.created_at}"
        )
        console.print(Panel(panel_text, title=f"Order Status: {order.order_id}", border_style="cyan"))

    asyncio.run(_run())


@order_app.command("receipt")
def order_receipt(
    order_id: str = typer.Argument(..., help="Order ID to retrieve receipt for."),
):
    """Display official invoice and verified purchase receipt."""
    async def _run():
        receipt = order_service.receipt_service.get_receipt(order_id)
        if not receipt:
            console.print(f"[yellow]No receipt found for order '{order_id}'.[/yellow]\n")
            return

        panel_text = (
            f"[bold]Receipt ID:[/bold]        {receipt.receipt_id}\n"
            f"[bold]Order ID:[/bold]          {receipt.order_id}\n"
            f"[bold]Vendor:[/bold]            {receipt.vendor}\n"
            f"[bold]External Order ID:[/bold] {receipt.external_order_id or 'N/A'}\n"
            f"[bold]Subtotal:[/bold]          {receipt.currency} {receipt.subtotal:.2f}\n"
            f"[bold]Shipping:[/bold]          {receipt.currency} {receipt.shipping:.2f}\n"
            f"[bold green]TOTAL PAID:[/bold green]        [bold green]{receipt.currency} {receipt.total:.2f}[/bold green]\n"
            f"[bold]Verification:[/bold]      [bold green]{receipt.verification_status.value}[/bold green]\n"
            f"[bold]Issued At:[/bold]         {receipt.issued_at}"
        )
        console.print(Panel(panel_text, title=f"Purchase Receipt: {receipt.receipt_id}", border_style="green"))

    asyncio.run(_run())


@order_app.command("cancel")
def order_cancel(
    order_id: str = typer.Argument(..., help="Order ID to cancel."),
    reason: str = typer.Option("User requested cancellation", "--reason", "-r", help="Reason for cancellation."),
):
    """Cancel an active draft, pending, or unfulfilled order."""
    async def _run():
        ok, order, err = await order_service.cancel_order(order_id, reason=reason)
        if not ok:
            console.print(f"[bold red][CANCEL FAILED][/bold red] {err}\n")
            return

        console.print(f"[bold green][OK] Order '{order.order_id}' has been CANCELLED.[/bold green]\n")

    asyncio.run(_run())
