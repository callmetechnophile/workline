"""Procurement search and multi-vendor optimization CLI commands."""

import asyncio
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from backend.workline.procurement.engine import procurement_engine
from backend.workline.procurement.models import ComponentRequirement
from cli.wline.core.paths import get_active_project_name
from cli.wline.ui.output import print_error, print_info, print_success, print_warning

procurement_app = typer.Typer(name="procurement", help="Procurement optimization and landed cost analysis.")
console = Console()


@procurement_app.command("search")
def procurement_search(
    query: Optional[str] = typer.Argument(None, help="Query string or active project requirements"),
) -> None:
    """Execute vendor sourcing across active project requirements."""
    active_name = get_active_project_name()
    q = query or "ESP32-S3 microcontroller and BME280 sensor"

    console.print(f"\n[bold cyan]PROCUREMENT SOURCING RUN[/bold cyan]\n")
    print_info(f"Target: {q}")

    async def _run():
        reqs = [
            ComponentRequirement(requirement_id="req_mcu", category="Microcontroller", quantity=1),
            ComponentRequirement(requirement_id="req_sensor", category="Sensors & Environmental", quantity=1),
        ]
        return await procurement_engine.generate_project_bom(active_name or "default_project", reqs)

    bom, plan = asyncio.run(_run())
    rec = plan.recommended_option

    console.print(f"\n[bold green]Recommended Sourcing Strategy:[/bold green] {rec.name}")
    console.print(f"[bold white]Selected Vendors:[/bold white] {', '.join(rec.selected_vendors)} ({rec.vendor_count} vendors)")
    console.print(f"[bold white]Component Cost:[/bold white]   INR {rec.total_component_cost}")
    console.print(f"[bold white]Est. Shipping:[/bold white]    INR {rec.estimated_shipping} (ESTIMATED)")
    console.print(f"[bold white]Landed Total:[/bold white]     [bold green]INR {rec.estimated_landed_total}[/bold green]")
    console.print(f"[bold white]Lead Time:[/bold white]        ~{rec.max_lead_time_days} business days\n")


@procurement_app.command("optimize")
def procurement_optimize() -> None:
    """Compare multi-vendor sourcing options and landed cost tradeoffs."""
    active_name = get_active_project_name() or "autonomous-rover"
    console.print(f"\n[bold cyan]PROCUREMENT OPTIMIZER TRADEOFFS ({active_name})[/bold cyan]\n")

    reqs = [
        ComponentRequirement(requirement_id="req_mcu", category="Microcontroller", quantity=1),
        ComponentRequirement(requirement_id="req_sensor", category="Sensors & Environmental", quantity=1),
        ComponentRequirement(requirement_id="req_reg", category="Power Management / Voltage Regulator", quantity=2),
    ]

    _, plan = asyncio.run(procurement_engine.generate_project_bom(active_name, reqs))

    table = Table(title="SOURCING OPTIONS COMPARISON", box=None)
    table.add_column("Option Strategy", style="bold cyan")
    table.add_column("Vendors", style="white")
    table.add_column("Components", style="white")
    table.add_column("Shipping", style="yellow")
    table.add_column("Landed Total", style="bold green")
    table.add_column("Max Lead Time", style="magenta")

    for opt in [plan.recommended_option] + plan.alternative_options:
        table.add_row(
            opt.name,
            str(opt.vendor_count),
            f"INR {opt.total_component_cost}",
            f"INR {opt.estimated_shipping}",
            f"INR {opt.estimated_landed_total}",
            f"{opt.max_lead_time_days} days",
        )

    console.print(table)
    console.print()
