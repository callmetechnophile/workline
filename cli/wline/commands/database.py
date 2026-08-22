"""Database status, validation, and migration commands for Workline CLI."""

import asyncio
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from backend.workline.database.migration.sqlite_export import export_sqlite_data
from backend.workline.database.migration.surreal_import import import_data_to_surreal
from backend.workline.database.migration.validator import validate_migration_counts
from backend.workline.database.repositories import (
    CollaborationRepository,
    GraphRepository,
    ProjectRepository,
)
from backend.workline.database.surrealdb import surreal_db
from backend.workline.retrieval.qdrant import qdrant_manager
from cli.wline.ui.output import print_error, print_info, print_success

database_app = typer.Typer(name="database", help="Manage Workline SurrealDB and Qdrant database services.")
console = Console()


@database_app.command("status")
def database_status() -> None:
    """Inspect SurrealDB and Qdrant service connectivity."""
    console.print("\n[bold cyan]WORKLINE DATABASE[/bold cyan]\n")

    # Check SurrealDB
    surreal_ok = asyncio.run(surreal_db.is_connected())
    surreal_status = "[bold green]CONNECTED[/bold green]" if surreal_ok else "[bold yellow]STANDBY / IN-MEMORY[/bold yellow]"

    # Check Qdrant
    qdrant_ok = qdrant_manager.is_connected()
    qdrant_status = "[bold green]CONNECTED[/bold green]" if qdrant_ok else "[bold yellow]STANDBY / IN-MEMORY[/bold yellow]"

    console.print(f"SurrealDB: {surreal_status}")
    console.print(f"Qdrant:    {qdrant_status}\n")


@database_app.command("migrate")
def database_migrate() -> None:
    """Migrate legacy SQLite database records into SurrealDB and establish engineering graph links."""
    console.print("\n[bold cyan]Starting SQLite -> SurrealDB Migration...[/bold cyan]\n")

    sqlite_data = export_sqlite_data()
    project_repo = ProjectRepository(surreal_db)
    collab_repo = CollaborationRepository(surreal_db)
    graph_repo = GraphRepository(surreal_db)

    counts = asyncio.run(import_data_to_surreal(sqlite_data, project_repo, collab_repo, graph_repo))

    print_success(f"Projects imported:      {counts['projects']}")
    print_success(f"Teams imported:         {counts['teams']}")
    print_success(f"Members imported:       {counts['members']}")
    print_success(f"Bundles imported:       {counts['bundles']}")
    print_success(f"Graph nodes generated:  {counts['graph_nodes']}")
    print_success(f"Graph edges generated:  {counts['graph_edges']}")
    console.print("\n[bold green]Migration complete![/bold green]\n")


@database_app.command("validate")
def database_validate() -> None:
    """Compare source SQLite counts with SurrealDB destination records and graph edges."""
    console.print("\n[bold cyan]WORKLINE DATABASE VALIDATION[/bold cyan]\n")

    sqlite_data = export_sqlite_data()
    project_repo = ProjectRepository(surreal_db)
    collab_repo = CollaborationRepository(surreal_db)
    graph_repo = GraphRepository(surreal_db)

    # First ensure migration is executed so destination is populated
    asyncio.run(import_data_to_surreal(sqlite_data, project_repo, collab_repo, graph_repo))

    val = asyncio.run(validate_migration_counts(sqlite_data, project_repo, collab_repo, graph_repo))

    table = Table(title="DATA RECORD VALIDATION", box=None)
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("SQLite (Source)", style="white")
    table.add_column("SurrealDB (Target)", style="bold green")

    table.add_row("Projects", str(val["sqlite"]["projects"]), str(val["surrealdb"]["projects"]))
    table.add_row("Teams", str(val["sqlite"]["teams"]), str(len(collab_repo._teams)))
    table.add_row("Members", str(val["sqlite"]["members"]), str(len(collab_repo._members)))
    table.add_row("Bundles", str(val["sqlite"]["bundles"]), str(val["surrealdb"]["bundles"]))
    table.add_row("Graph Nodes", "N/A (Legacy SQL)", str(val["surrealdb"]["graph_nodes"]))
    table.add_row("Graph Edges", "N/A (Legacy SQL)", str(val["surrealdb"]["graph_edges"]))

    console.print(table)

    total_docs = len(qdrant_manager._memory_points.get("workline_documents", {}))
    console.print(f"\n[bold white]Qdrant Documents Indexed:[/bold white] [bold cyan]{total_docs}[/bold cyan]\n")
