"""Implementation of `wg inspect` — show project bootstrap info or inspect a .wlipjt package."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def inspect_command(
    target: Optional[str] = typer.Argument(
        None,
        help="Project directory or .wlipjt package file (defaults to current directory)",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full file listing"),
) -> None:
    """Inspect a WORKLINE project directory or .wlipjt package file."""
    raw_target = Path(target).resolve() if target else Path.cwd()

    # Dispatch based on target type
    if raw_target.is_file() and raw_target.suffix == ".wlipjt":
        _inspect_package(raw_target, verbose)
    else:
        _inspect_project(raw_target, verbose)


def _inspect_package(path: Path, verbose: bool) -> None:
    """Inspect a .wlipjt package using the backend PackageInspector."""
    console.print(f"\n[bold white]WORKLINE Package Inspection[/bold white]")
    console.print(f"[dim]{path}[/dim]\n")

    try:
        from backend.workline.project.inspector import PackageInspector
        inspection = PackageInspector.inspect(path)
    except ImportError:
        console.print("[yellow]⚠[/yellow] Backend not available — showing basic package info")
        _basic_package_info(path)
        return
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)

    m = inspection.manifest

    status_color = "green" if inspection.valid else "red"
    console.print(f"[bold]Package:[/bold]    {m.project_name} ({m.project_id})")
    console.print(f"[bold]Format:[/bold]     {m.format} v{m.format_version}")
    console.print(f"[bold]Version:[/bold]    {m.project_version}")
    console.print(f"[bold]Exported:[/bold]   {m.exported_at}")
    console.print(
        f"[bold]Integrity:[/bold]  [{status_color}]{inspection.integrity_status}[/{status_color}]"
    )

    sb = inspection.size_breakdown
    size_mb = sb.total_package_size_bytes / (1024 * 1024)
    console.print(f"[bold]Size:[/bold]       {size_mb:.2f} MB")
    console.print(f"  Project state:  {sb.project_state_size_bytes:,} bytes")
    console.print(f"  Documentation:  {sb.documentation_size_bytes:,} bytes")
    console.print(f"  Artifacts:      {sb.artifacts_size_bytes:,} bytes")
    console.print(f"  Git:            {sb.git_size_bytes:,} bytes")

    console.print(f"\n[bold]Contents:[/bold]")
    console.print(f"  Components: {m.components_count}")
    console.print(f"  Nets:       {m.nets_count}")
    console.print(f"  BOM items:  {m.bom_count}")
    console.print(f"  Artifacts:  {m.artifacts_count}")

    if inspection.warnings:
        console.print("\n[bold yellow]Warnings:[/bold yellow]")
        for w in inspection.warnings:
            console.print(f"  [yellow]⚠[/yellow] {w}")

    if inspection.errors:
        console.print("\n[bold red]Errors:[/bold red]")
        for e in inspection.errors:
            console.print(f"  [red]✗[/red] {e}")

    console.print()


def _basic_package_info(path: Path) -> None:
    """Show minimal info about a .wlipjt package without backend."""
    import zipfile
    try:
        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()
        size_mb = path.stat().st_size / (1024 * 1024)
        console.print(f"[bold]File:[/bold]    {path.name}")
        console.print(f"[bold]Size:[/bold]    {size_mb:.2f} MB")
        console.print(f"[bold]Entries:[/bold] {len(names)}")
        if "manifest.toon" in names:
            console.print("[bold green]✓[/bold green] manifest.toon present")
        if "checksums.toon" in names:
            console.print("[bold green]✓[/bold green] checksums.toon present")
    except Exception as e:
        console.print(f"[red]Cannot read package: {e}[/red]")


def _inspect_project(path: Path, verbose: bool) -> None:
    """Inspect a .wl project directory."""
    console.print(f"\n[bold white]WORKLINE Project[/bold white]\n")

    from cli.workline.project.filesystem import find_project_root, STANDARD_MODULES, WL_METADATA_DIR

    root = find_project_root(path)
    if not root:
        console.print(f"[red]Error:[/red] No WORKLINE project found at '{path}'")
        console.print("[dim]A WORKLINE project must contain README.wl or .wl/manifest.wl[/dim]")
        raise typer.Exit(code=1)

    console.print(f"[bold]Location:[/bold]  {root}")

    # README.wl
    readme_file = root / "README.wl"
    if readme_file.exists():
        try:
            from cli.workline.project.readme import parse_readme_wl
            identity = parse_readme_wl(readme_file)
            console.print(f"[bold]Project:[/bold]   {identity.name}")
            console.print(f"[bold]ID:[/bold]        {identity.project_id}")
            console.print(f"[bold]Version:[/bold]   {identity.version}")
            console.print(f"[bold]Domain:[/bold]    {identity.domain}")
            console.print(f"[bold]Status:[/bold]    {identity.status}")
            if identity.description:
                console.print(f"[bold]Description:[/bold] {identity.description}")
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Could not parse README.wl: {e}")
    else:
        console.print("[yellow]⚠[/yellow] README.wl not found")

    # .wl/ metadata
    wl_dir = root / WL_METADATA_DIR
    console.print(f"\n[bold].wl Metadata[/bold]")
    wl_files = list(wl_dir.glob("*.wl")) if wl_dir.exists() else []
    if wl_files:
        for f in sorted(wl_files):
            console.print(f"  [green]✓[/green] {f.name}")
    else:
        console.print("  [yellow]⚠[/yellow] .wl/ directory empty or missing")

    # Moss index status
    moss_file = wl_dir / "moss.wl"
    console.print(f"\n[bold]Index (Moss)[/bold]")
    if moss_file.exists():
        try:
            import yaml
            m = yaml.safe_load(moss_file.read_text(encoding="utf-8")) or {}
            mc = m.get("moss", {})
            status = mc.get("status", "UNKNOWN")
            count = mc.get("document_count", 0)
            indexed_at = mc.get("indexed_at", "never")
            s_color = "green" if status == "READY" else "yellow"
            console.print(f"  Status:   [{s_color}]{status}[/{s_color}]")
            console.print(f"  Records:  {count:,}")
            console.print(f"  Last indexed: {indexed_at}")
        except Exception:
            console.print("  [yellow]⚠[/yellow] Could not read moss.wl")
    else:
        console.print("  [yellow]⚠[/yellow] Not indexed — run [bold]wg backup[/bold] then [bold]wg restore[/bold] to rebuild, or open WORKLINE to auto-index")

    # Resource counts
    console.print(f"\n[bold]Resources[/bold]")
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    table.add_column("Module")
    table.add_column("Files", justify="right")
    for mod in STANDARD_MODULES:
        mod_dir = root / mod
        if mod_dir.exists():
            count = sum(1 for f in mod_dir.rglob("*") if f.is_file())
            table.add_row(mod, str(count))
        elif verbose:
            table.add_row(f"[dim]{mod}[/dim]", "[dim]—[/dim]")
    console.print(table)

    console.print("[dim]Run [bold]wg open[/bold] to work with this project in WORKLINE.[/dim]\n")
