"""Component search and side-by-side comparison CLI commands."""

import asyncio
from typing import List, Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from backend.workline.procurement.engine import procurement_engine
from cli.wline.ui.output import print_error, print_info, print_success, print_warning

component_app = typer.Typer(name="component", help="Search and compare hardware components across vendor catalogs.")
console = Console()


@component_app.command("search")
def component_search(
    query: str = typer.Argument(..., help="Search query (e.g. '3.3V 2A buck regulator' or 'ESP32')"),
    limit: int = typer.Option(5, "--limit", "-l", help="Max candidates per vendor"),
) -> None:
    """Search components across DigiKey, Mouser, Robu, and Robocraze."""
    console.print(f"\n[bold cyan]COMPONENT SEARCH:[/bold cyan] [bold white]'{query}'[/bold white]\n")

    async def _search():
        return await procurement_engine.search_engine.search_vendors(query, limit_per_source=limit)

    candidates = asyncio.run(_search())
    if not candidates:
        print_warning(f"No components found matching '{query}'.")
        return

    for idx, c in enumerate(candidates, 1):
        for l in c.listings:
            procurement_engine._components[c.component_id] = c

        best_listing = c.listings[0] if c.listings else None
        ds_status = c.datasheet.verification_status.value if c.datasheet else "NO_DATASHEET"
        ds_color = "green" if ds_status == "VERIFIED" else "yellow"

        console.print(f"[bold cyan]{idx}. {c.manufacturer_part_number}[/bold cyan] ({c.product_name})")
        console.print(f"   [bold white]Manufacturer:[/bold white] {c.manufacturer}")
        if best_listing:
            stock_str = f"{best_listing.stock} units" if best_listing.stock else ("In Stock" if best_listing.in_stock else "Out of Stock")
            console.print(f"   [bold white]Best Vendor:[/bold white]  {best_listing.vendor_name} ({best_listing.location})")
            console.print(f"   [bold white]Price:[/bold white]        {best_listing.currency} {best_listing.unit_price}")
            console.print(f"   [bold white]Stock:[/bold white]        {stock_str}")
        console.print(f"   [bold white]Datasheet:[/bold white]    [{ds_color}]{ds_status}[/{ds_color}]")
        console.print(f"   [dim]ID: {c.component_id}[/dim]\n")


@component_app.command("compare")
def component_compare(
    id1: str = typer.Argument(..., help="First component ID or MPN"),
    id2: str = typer.Argument(..., help="Second component ID or MPN"),
) -> None:
    """Compare two components side-by-side."""
    console.print(f"\n[bold cyan]COMPONENT COMPARISON:[/bold cyan] [white]{id1}[/white] vs [white]{id2}[/white]\n")

    c1 = procurement_engine.get_component(id1)
    c2 = procurement_engine.get_component(id2)

    table = Table(box=None)
    table.add_column("Specification", style="bold white")
    table.add_column(id1, style="cyan")
    table.add_column(id2, style="yellow")

    if c1 and c2:
        table.add_row("Manufacturer", c1.manufacturer, c2.manufacturer)
        table.add_row("MPN", c1.manufacturer_part_number, c2.manufacturer_part_number)
        table.add_row("Category", c1.category, c2.category)
        table.add_row("Nominal Voltage", f"{c1.electrical.nominal_voltage or 'N/A'}V", f"{c2.electrical.nominal_voltage or 'N/A'}V")
        table.add_row("Max Current", f"{c1.electrical.current_max or 'N/A'}A", f"{c2.electrical.current_max or 'N/A'}A")
        table.add_row("Package", c1.physical.package or "N/A", c2.physical.package or "N/A")
        table.add_row("Vendors Available", str(len(c1.listings)), str(len(c2.listings)))
    else:
        table.add_row("Status", "Cached / Available" if c1 else "Run search first", "Cached / Available" if c2 else "Run search first")

    console.print(table)
    console.print()
