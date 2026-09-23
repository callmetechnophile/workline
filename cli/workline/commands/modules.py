"""
Modular domain inspection commands for WORKLINE project resources.
Provides structured views into requirements, architecture, components, BOM,
research, documents, analysis, tasks, decisions, agents, and team.
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

from cli.workline.project.filesystem import find_project_root
from cli.workline.retrieval.retriever import ProjectRetriever

console = Console()


def _get_retriever(path: Optional[str]) -> ProjectRetriever:
    target_dir = Path(path).resolve() if path else Path.cwd()
    root = find_project_root(target_dir)
    if not root:
        console.print(f"[bold red]Error:[/bold red] '{target_dir}' is not a WORKLINE project.")
        raise typer.Exit(code=1)
    return ProjectRetriever(root)


def requirements_command(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category (functional, technical, constraint)"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """List and inspect project requirements."""
    retriever = _get_retriever(path)
    records = retriever.retrieve("requirement specification", top_k=30, resource_types=["requirement"])
    
    console.print("\n[bold white]PROJECT REQUIREMENTS[/bold white]\n")
    if not records:
        console.print("[dim]No requirements registered yet.[/dim]\n")
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID / Path", style="dim")
    table.add_column("Title")
    table.add_column("Category")
    table.add_column("Subsystem")

    for r in records:
        cat = str(r.metadata.get("category", "general"))
        if category and cat.lower() != category.lower():
            continue
        table.add_row(
            r.metadata.get("requirement_id") or r.path,
            r.title,
            cat,
            str(r.metadata.get("subsystem", "-")),
        )
    console.print(table)
    console.print()


def architecture_command(
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """Display project system architecture and subsystems."""
    retriever = _get_retriever(path)
    records = retriever.retrieve("architecture subsystem block system", top_k=20, resource_types=["architecture"])
    
    console.print("\n[bold white]SYSTEM ARCHITECTURE[/bold white]\n")
    if not records:
        console.print("[dim]No architecture documents registered.[/dim]\n")
        return

    for r in records:
        console.print(f"[bold cyan]• {r.title}[/bold cyan] ([dim]{r.path}[/dim])")
        for line in r.content.splitlines()[:6]:
            if line.strip() and not line.strip().startswith("="):
                console.print(f"    {line.strip()}")
        console.print()


def components_command(
    subsystem: Optional[str] = typer.Option(None, "--subsystem", "-s", help="Filter by subsystem"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """List hardware components and MPN dossiers."""
    retriever = _get_retriever(path)
    records = retriever.retrieve("component MPN manufacturer", top_k=40, resource_types=["component"])
    
    console.print("\n[bold white]PROJECT COMPONENTS[/bold white]\n")
    if not records:
        console.print("[dim]No components registered.[/dim]\n")
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("MPN", style="bold white")
    table.add_column("Category")
    table.add_column("Manufacturer")
    table.add_column("Subsystem")
    table.add_column("Path", style="dim")

    for r in records:
        sub = str(r.metadata.get("subsystem", "-"))
        if subsystem and sub.lower() != subsystem.lower():
            continue
        table.add_row(
            str(r.metadata.get("mpn") or r.title),
            str(r.metadata.get("category", "-")),
            str(r.metadata.get("manufacturer", "-")),
            sub,
            r.path,
        )
    console.print(table)
    console.print()


def bom_command(
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """Display Bill of Materials (BOM) items and cost estimates."""
    retriever = _get_retriever(path)
    records = retriever.retrieve("bill of materials BOM line item", top_k=40, resource_types=["bom"])
    
    console.print("\n[bold white]BILL OF MATERIALS (BOM)[/bold white]\n")
    if not records:
        console.print("[dim]No BOM records found.[/dim]\n")
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Item / MPN", style="bold white")
    table.add_column("Qty")
    table.add_column("Est. Cost")
    table.add_column("Supplier / Source")

    for r in records:
        table.add_row(
            str(r.metadata.get("mpn") or r.title),
            str(r.metadata.get("quantity") or r.metadata.get("qty") or "1"),
            str(r.metadata.get("cost") or r.metadata.get("unit_cost") or "-"),
            str(r.metadata.get("supplier") or r.path),
        )
    console.print(table)
    console.print()


def tasks_command(
    status: Optional[str] = typer.Option(None, "--status", help="Filter by status (open, in_progress, blocked, closed)"),
    assignee: Optional[str] = typer.Option(None, "--assignee", help="Filter by assignee"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """List project tasks with deterministic status and assignee filtering."""
    retriever = _get_retriever(path)
    records = retriever.lookup_tasks(status=status, assignee=assignee)
    
    console.print("\n[bold white]PROJECT TASKS[/bold white]\n")
    if not records:
        console.print("[dim]No matching tasks found.[/dim]\n")
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Task ID", style="dim")
    table.add_column("Title", style="bold white")
    table.add_column("Status")
    table.add_column("Assignee")

    for r in records:
        st = str(r.metadata.get("status", "open"))
        color = "green" if st == "closed" else ("yellow" if st == "in_progress" else "white")
        table.add_row(
            str(r.metadata.get("task_id") or r.path),
            r.title,
            f"[{color}]{st}[/{color}]",
            str(r.metadata.get("assignee", "unassigned")),
        )
    console.print(table)
    console.print()


def decisions_command(
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """List Architectural Decision Records (ADRs)."""
    retriever = _get_retriever(path)
    records = retriever.retrieve("architectural decision ADR", top_k=20, resource_types=["decision"])
    
    console.print("\n[bold white]ARCHITECTURAL DECISIONS (ADRs)[/bold white]\n")
    if not records:
        console.print("[dim]No decisions recorded.[/dim]\n")
        return

    for r in records:
        console.print(f"[bold cyan]• [{r.metadata.get('decision_id') or r.path}][/bold cyan] {r.title}")
        for l in r.content.splitlines()[:5]:
            if ":" in l and not l.strip().startswith("="):
                console.print(f"    {l.strip()}")
        console.print()


def research_command(
    query: Optional[str] = typer.Argument(None, help="Optional search query within research papers"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """Search and inspect literature dossiers and synthesized research findings."""
    retriever = _get_retriever(path)
    q = query or "literature research paper findings"
    records = retriever.retrieve(q, top_k=15, resource_types=["research"])
    
    console.print(f"\n[bold white]RESEARCH DOSSIERS & FINDINGS[/bold white]\n")
    if not records:
        console.print("[dim]No research entries found.[/dim]\n")
        return

    for r in records:
        console.print(f"[bold cyan]• {r.title}[/bold cyan] ([dim]{r.path}[/dim])")
        for l in r.content.splitlines()[:4]:
            if l.strip() and not l.strip().startswith("="):
                console.print(f"    {l.strip()}")
        console.print()


def documents_command(
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """List technical specifications and document dossiers."""
    retriever = _get_retriever(path)
    records = retriever.retrieve("technical specification document", top_k=20, resource_types=["document", "datasheet"])
    
    console.print("\n[bold white]TECHNICAL DOCUMENTS & DATASHEETS[/bold white]\n")
    for r in records:
        console.print(f"  • [bold white]{r.title}[/bold white] ([dim]{r.path}[/dim])")
    console.print()


def analysis_command(
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """Display power, thermal, and electrical simulation reports."""
    retriever = _get_retriever(path)
    records = retriever.retrieve("simulation analysis power thermal pcb", top_k=15, resource_types=["analysis"])
    
    console.print("\n[bold white]ENGINEERING SIMULATION & ANALYSIS[/bold white]\n")
    for r in records:
        console.print(f"[bold cyan]• {r.title}[/bold cyan] ([dim]{r.path}[/dim])")
        for l in r.content.splitlines()[:4]:
            if l.strip() and not l.strip().startswith("="):
                console.print(f"    {l.strip()}")
        console.print()


def agents_command(
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """Display configured autonomous engineering agents and cryptographic receipts."""
    retriever = _get_retriever(path)
    records = retriever.retrieve("agent delegation receipt governance", top_k=15, resource_types=["agent", "delegation", "receipt"])
    
    console.print("\n[bold white]AGENT GOVERNANCE & RECEIPTS[/bold white]\n")
    for r in records:
        console.print(f"  • [bold white]{r.title}[/bold white] ([dim]{r.path}[/dim])")
    console.print()


def team_command(
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """Display project team members, roles, and authorization policies."""
    retriever = _get_retriever(path)
    records = retriever.retrieve("team member role authorization", top_k=10, resource_types=["team"])
    
    console.print("\n[bold white]TEAM ROLES & GOVERNANCE[/bold white]\n")
    for r in records:
        console.print(f"  • [bold white]{r.title}[/bold white] ([dim]{r.path}[/dim])")
    console.print()
