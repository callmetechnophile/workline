"""
CLI entry point for ResearchPaperAgent test mode.
Allows local testing and formatted table output directly from terminal.
"""

import argparse
import sys
from typing import List

from rich.console import Console
from rich.table import Table

from research_agents.research_paper_agent.agent import ResearchPaperAgent
from research_agents.research_paper_agent.schemas import ResearchPaperAgentInput


def main(args: List[str] = None):
    parser = argparse.ArgumentParser(
        description="WorkflowGuide AI — ResearchPaperAgent (Agent #1) CLI Test Mode"
    )
    parser.add_argument(
        "--project",
        "-p",
        type=str,
        default="Autonomous Search and Rescue Drone",
        help="Project title / concept",
    )
    parser.add_argument(
        "--description",
        "-d",
        type=str,
        default="Autonomous UAV system employing thermal vision and edge neural networks for disaster human detection.",
        help="Project detailed description",
    )
    parser.add_argument(
        "--domain",
        type=str,
        default="Robotics / Computer Vision",
        help="Engineering discipline / domain",
    )
    parser.add_argument(
        "--objective",
        type=str,
        action="append",
        default=[],
        help="Target research objective (can be specified multiple times)",
    )
    parser.add_argument(
        "--component",
        "-c",
        type=str,
        action="append",
        default=[],
        help="Hardware/Software component",
    )
    parser.add_argument(
        "--technology",
        "-t",
        type=str,
        action="append",
        default=[],
        help="Algorithm / Technology",
    )
    parser.add_argument(
        "--constraint",
        type=str,
        action="append",
        default=[],
        help="Operational constraint",
    )
    parser.add_argument(
        "--keyword",
        "-k",
        type=str,
        action="append",
        default=[],
        help="Target keyword",
    )
    parser.add_argument(
        "--max-papers",
        "-m",
        type=int,
        default=10,
        help="Maximum papers to return",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use realistic offline mock records for provider testing without live network",
    )

    parsed = parser.parse_args(args)

    # Defaults for demo/test run if not provided
    objectives = parsed.objective or ["thermal human detection", "autonomous navigation"]
    components = parsed.component or ["thermal camera", "Jetson Orin"]
    technologies = parsed.technology or ["YOLO", "computer vision"]
    constraints = parsed.constraint or ["real-time inference"]
    keywords = parsed.keyword or ["thermal human detection", "UAV search and rescue"]

    input_data = ResearchPaperAgentInput(
        project_title=parsed.project,
        project_description=parsed.description,
        engineering_domain=parsed.domain,
        research_objectives=objectives,
        components=components,
        technologies=technologies,
        constraints=constraints,
        keywords=keywords,
        max_papers=parsed.max_papers,
    )

    console = Console()
    console.print(
        f"\n[bold cyan]WorkflowGuide AI[/bold cyan] — [bold green]ResearchPaperAgent (Agent #1)[/bold green]"
    )
    console.print(f"[dim]Project:[/dim] {input_data.project_title}")
    console.print(f"[dim]Domain:[/dim] {input_data.engineering_domain}")
    console.print(f"[dim]Objectives:[/dim] {', '.join(input_data.research_objectives)}")
    console.print(f"[dim]Max Papers:[/dim] {input_data.max_papers}\n")

    if parsed.mock:
        from research_agents.research_paper_agent.tests.test_agent import MockFreephdlaborProvider
        agent = ResearchPaperAgent(provider=MockFreephdlaborProvider())
    else:
        agent = ResearchPaperAgent()

    output = agent.run_sync(input_data)

    if output.errors:
        console.print("[bold yellow]Notices / Warnings:[/bold yellow]")
        for err in output.errors:
            console.print(f"  • [{err.code}] {err.message}")
        console.print("")

    table = Table(title=f"Discovered Academic Papers ({output.papers_selected} selected)")
    table.add_column("Rank", justify="right", style="cyan", no_wrap=True)
    table.add_column("Title", style="white", max_width=45)
    table.add_column("Authors", style="dim", max_width=25)
    table.add_column("Year", justify="center", style="yellow")
    table.add_column("Relevance", justify="right", style="green")
    table.add_column("PDF", justify="center", style="magenta")
    table.add_column("Source", style="dim")

    for idx, paper in enumerate(output.papers, 1):
        authors_str = ", ".join(paper.authors[:2]) if paper.authors else "Unknown"
        if len(paper.authors) > 2:
            authors_str += " et al."
        year_str = str(paper.publication_date)[:4] if paper.publication_date else "N/A"
        pdf_str = "[bold green]YES[/bold green]" if paper.pdf_available else "[dim]NO[/dim]"
        rel_str = f"{paper.relevance_score:.2f}"

        table.add_row(
            str(idx),
            paper.title,
            authors_str,
            year_str,
            rel_str,
            pdf_str,
            paper.source,
        )

    console.print(table)
    console.print(
        f"\n[dim]Total Candidates Found: {output.papers_found} | Queries Used: {len(output.queries_used)}[/dim]\n"
    )


if __name__ == "__main__":
    main()
