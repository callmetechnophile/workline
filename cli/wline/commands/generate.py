"""CLI command group for Visual (Paper Banana) and Presentation (Gamma) generation."""

import asyncio
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import typer
from backend.workline.generation.models import ImagePurpose, PresentationPurpose
from backend.workline.generation.service import generation_service

app = typer.Typer(name="generate", help="Generate technical architecture visuals and presentation decks.")
console = Console()


@app.command("image")
def generate_image_cmd(
    project_id: str = typer.Option("default_project", "--project", "-p", help="Target project ID"),
    purpose: str = typer.Option("ARCHITECTURE", "--purpose", help="Visual purpose (ARCHITECTURE, PCB, WORKFLOW, etc.)"),
    prompt: Optional[str] = typer.Option(None, "--prompt", help="Custom visual focus prompt"),
    provider: Optional[str] = typer.Option("PaperBanana", "--provider", help="Image generation provider"),
    ratio: str = typer.Option("16:9", "--ratio", help="Aspect ratio (16:9, 4:3, 1:1)"),
):
    """Generate a technical visual diagram via Paper Banana."""
    try:
        purpose_enum = ImagePurpose(purpose.upper())
    except ValueError:
        purpose_enum = ImagePurpose.ARCHITECTURE

    console.print(
        Panel.fit(
            f"[bold cyan]WORKLINE TECHNICAL VISUAL GENERATION[/bold cyan]\n"
            f"[dim]Project:[/dim] {project_id}\n"
            f"[dim]Provider:[/dim] {provider or 'Paper Banana'}\n"
            f"[dim]Purpose:[/dim] {purpose_enum.value}\n"
            f"[dim]Aspect Ratio:[/dim] {ratio}",
            title="Image Generation Request",
            border_style="cyan",
        )
    )

    with console.status("[bold green]Synthesizing architecture and rendering SVG visual...[/bold green]"):
        artifact = asyncio.run(
            generation_service.generate_image(
                project_id=project_id,
                purpose=purpose_enum,
                user_prompt=prompt,
                provider_name=provider,
                aspect_ratio=ratio,
            )
        )

    console.print(f"[bold green]✓[/bold green] Technical visual generated successfully!")
    console.print(f"  [bold]Artifact ID:[/bold] {artifact.artifact_id}")
    console.print(f"  [bold]Filename:[/bold] {artifact.filename}")
    console.print(f"  [bold]SHA-256:[/bold] {artifact.sha256}")
    console.print(f"  [bold]Format:[/bold] {artifact.format.upper()} ({artifact.width}x{artifact.height})")


@app.command("architecture")
def generate_architecture_cmd(
    project_id: str = typer.Option("default_project", "--project", "-p", help="Target project ID"),
):
    """Generate a complete system architecture visual for the project."""
    generate_image_cmd(
        project_id=project_id,
        purpose="ARCHITECTURE",
        prompt=None,
        provider="PaperBanana",
        ratio="16:9",
    )


@app.command("pcb-visual")
def generate_pcb_visual_cmd(
    project_id: str = typer.Option("default_project", "--project", "-p", help="Target project ID"),
):
    """Generate a precision PCB layout and thermal distribution visual."""
    generate_image_cmd(
        project_id=project_id,
        purpose="PCB",
        prompt=None,
        provider="PaperBanana",
        ratio="16:9",
    )


@app.command("presentation")
def generate_presentation_cmd(
    project_id: str = typer.Option("default_project", "--project", "-p", help="Target project ID"),
    title: str = typer.Option("Project Architecture & Engineering Review", "--title", "-t", help="Presentation title"),
    audience: str = typer.Option("Technical Audience", "--audience", help="Target audience"),
    purpose: str = typer.Option("PROJECT_OVERVIEW", "--purpose", help="Presentation purpose"),
    slides: int = typer.Option(8, "--slides", "-s", help="Total slide count"),
    provider: Optional[str] = typer.Option("Gamma", "--provider", help="Presentation provider"),
):
    """Generate a structured technical presentation deck via Gamma."""
    try:
        purpose_enum = PresentationPurpose(purpose.upper())
    except ValueError:
        purpose_enum = PresentationPurpose.PROJECT_OVERVIEW

    console.print(
        Panel.fit(
            f"[bold magenta]WORKLINE TECHNICAL PRESENTATION GENERATION[/bold magenta]\n"
            f"[dim]Project:[/dim] {project_id}\n"
            f"[dim]Title:[/dim] {title}\n"
            f"[dim]Audience:[/dim] {audience}\n"
            f"[dim]Purpose:[/dim] {purpose_enum.value}\n"
            f"[dim]Slide Count:[/dim] {slides}\n"
            f"[dim]Provider:[/dim] {provider or 'Gamma'}",
            title="Presentation Request",
            border_style="magenta",
        )
    )

    with console.status("[bold green]Extracting project state and generating slide outline...[/bold green]"):
        artifact = asyncio.run(
            generation_service.generate_presentation(
                project_id=project_id,
                title=title,
                audience=audience,
                purpose=purpose_enum,
                slide_count=slides,
                provider_name=provider,
            )
        )

    console.print(f"[bold green]✓[/bold green] Presentation deck generated successfully!")
    console.print(f"  [bold]Artifact ID:[/bold] {artifact.artifact_id}")
    console.print(f"  [bold]Title:[/bold] {artifact.title}")
    console.print(f"  [bold]Slides:[/bold] {artifact.slide_count}")
    console.print(f"  [bold]SHA-256:[/bold] {artifact.sha256}")
    console.print(f"  [bold]Filename:[/bold] {artifact.filename}")


@app.command("deck")
def generate_deck_interactive_cmd(
    project_id: str = typer.Option("default_project", "--project", "-p", help="Target project ID"),
):
    """Generate an engineering presentation deck with guided defaults."""
    generate_presentation_cmd(
        project_id=project_id,
        title=f"Workline Engineering Review: {project_id}",
        audience="Engineering Leads & Architects",
        purpose="TECHNICAL_DEEP_DIVE",
        slides=8,
        provider="Gamma",
    )
