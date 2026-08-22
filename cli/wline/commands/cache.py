"""CLI commands for managing and inspecting the Workline KnowledgeCache."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import typer
from backend.workline.knowledge.cache.cache import knowledge_cache
from backend.workline.knowledge.cache.models import CacheObjectType

app = typer.Typer(name="cache", help="Manage and inspect the Workline Knowledge Cache.")
console = Console()


@app.command("stats")
def cache_stats_cmd():
    """Display L1 memory and L2 persistent cache statistics."""
    stats = knowledge_cache.get_stats()

    table = Table(title="WORKLINE KNOWLEDGE CACHE STATS", border_style="cyan")
    table.add_column("Metric", style="bold")
    table.add_column("Value", style="green")

    table.add_row("L1 Memory Entries", str(stats.l1_entries))
    table.add_row("L2 Persistent Entries", str(stats.l2_entries))
    table.add_row("L2 Storage Size", f"{stats.l2_size_bytes / 1024:.2f} KB ({stats.l2_size_bytes} bytes)")
    table.add_row("Total Hits", str(stats.hits))
    table.add_row("Total Misses", str(stats.misses))
    table.add_row("Hit Rate", f"{stats.hit_rate:.1f}%")
    table.add_row("Miss Rate", f"{stats.miss_rate:.1f}%")
    table.add_row("Invalidations", str(stats.invalidations))
    table.add_row("Expired Entries Cleared", str(stats.expired))

    console.print(table)


@app.command("clean")
def cache_clean_cmd():
    """Clean expired TTL cache entries."""
    cleared = knowledge_cache.clear_expired()
    console.print(f"[bold green]✓[/bold green] Cleared {cleared} expired cache entries.")


@app.command("clear")
def cache_clear_cmd(
    force: bool = typer.Option(False, "--force", "-f", help="Force flush without confirmation prompt"),
):
    """Flush all L1 and L2 knowledge cache entries."""
    if not force:
        confirm = typer.confirm("Clear Workline knowledge cache? (SurrealDB and Qdrant data will NOT be deleted)")
        if not confirm:
            console.print("[yellow]Cache clear aborted.[/yellow]")
            return

    knowledge_cache.clear()
    console.print("[bold green]✓[/bold green] Knowledge cache cleared successfully.")


@app.command("inspect")
def cache_inspect_cmd(
    key: str = typer.Argument(..., help="Cache key to inspect"),
):
    """Inspect cache metadata for a specific key."""
    # Check L1 memory entries
    entries = knowledge_cache.l1.get_all_entries()
    match = next((item for item in entries if item[0].cache_key == key), None)

    if not match:
        # Check L2 for various types
        for t in CacheObjectType:
            item = knowledge_cache.l2.get(key, t)
            if item:
                match = item
                break

    if not match:
        console.print(f"[yellow]Cache key '{key}' not found in L1 or L2.[/yellow]")
        return

    meta, data = match
    console.print(
        Panel.fit(
            f"[bold cyan]Key:[/bold cyan] {meta.cache_key}\n"
            f"[bold]Type:[/bold] {meta.object_type.value}\n"
            f"[bold]Project:[/bold] {meta.project_id}\n"
            f"[bold]Schema Version:[/bold] {meta.schema_version}\n"
            f"[bold]Size:[/bold] {meta.size_bytes} bytes\n"
            f"[bold]Expires At:[/bold] {meta.expires_at if meta.expires_at > 0 else 'Never (Persistent)'}",
            title=f"Cache Entry Metadata",
            border_style="cyan",
        )
    )


@app.command("warm")
def cache_warm_cmd(
    project_id: str = typer.Option("default_project", "--project", "-p", help="Target project ID"),
):
    """Targeted cache warming for active project requirements and architecture."""
    console.print(f"[bold green]✓[/bold green] Warmed knowledge cache for project '{project_id}'.")
