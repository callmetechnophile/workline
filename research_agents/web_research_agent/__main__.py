"""
CLI entry point for WebResearchAgent (Agent #2) development mode.
Allows local testing and formatted terminal table output with source URLs and facts.
"""

import argparse
from typing import List

from rich.console import Console
from rich.table import Table

from research_agents.web_research_agent.agent import WebResearchAgent
from research_agents.web_research_agent.schemas import WebResearchAgentInput


def main(args: List[str] = None):
    parser = argparse.ArgumentParser(
        description="WorkflowGuide AI — WebResearchAgent (Agent #2) CLI Development Mode"
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
        default="A drone using computer vision and thermal sensing to locate humans during disaster response.",
        help="Project detailed description",
    )
    parser.add_argument(
        "--domain",
        type=str,
        default="Robotics / UAV / Computer Vision",
        help="Engineering domain",
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
        "--max-sources",
        "-m",
        type=int,
        default=10,
        help="Maximum web sources to return",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use realistic offline mock records without external network",
    )

    parsed = parser.parse_args(args)

    objectives = parsed.objective or ["thermal human detection", "edge inference", "autonomous navigation"]
    components = parsed.component or ["Jetson Orin Nano", "thermal camera"]
    technologies = parsed.technology or ["YOLO", "ROS 2"]
    constraints = parsed.constraint or ["real-time inference", "edge deployment"]
    keywords = parsed.keyword or ["UAV search and rescue", "thermal human detection"]

    input_data = WebResearchAgentInput(
        project_title=parsed.project,
        project_description=parsed.description,
        engineering_domain=parsed.domain,
        research_objectives=objectives,
        components=components,
        technologies=technologies,
        constraints=constraints,
        keywords=keywords,
        max_sources=parsed.max_sources,
    )

    console = Console()
    console.print(
        f"\n[bold cyan]WorkflowGuide AI[/bold cyan] — [bold green]WebResearchAgent (Agent #2)[/bold green]"
    )
    console.print(f"[dim]Project:[/dim] {input_data.project_title}")
    console.print(f"[dim]Domain:[/dim] {input_data.engineering_domain}")
    console.print(f"[dim]Objectives:[/dim] {', '.join(input_data.research_objectives)}")
    console.print(f"[dim]Max Sources:[/dim] {input_data.max_sources}\n")

    if parsed.mock:
        from research_agents.web_research_agent.tests.test_agent import MockTavilyProvider, MockAnakinProvider
        agent = WebResearchAgent(
            tavily_provider=MockTavilyProvider(),
            anakin_provider=MockAnakinProvider(),
        )
    else:
        agent = WebResearchAgent()

    output = agent.run_sync(input_data)

    if output.errors:
        console.print("[bold yellow]Notices / Warnings:[/bold yellow]")
        for err in output.errors:
            console.print(f"  • [{err.code}] {err.message}")
        console.print("")

    table = Table(title=f"Discovered Web Evidence ({output.sources_selected} selected)")
    table.add_column("Rank", justify="right", style="cyan", no_wrap=True)
    table.add_column("Source Title", style="white", max_width=40)
    table.add_column("Type", style="yellow")
    table.add_column("Authority", justify="center", style="magenta")
    table.add_column("Relevance", justify="right", style="green")
    table.add_column("Tool", style="dim")
    table.add_column("URL", style="blue", max_width=35)

    for idx, src in enumerate(output.sources, 1):
        table.add_row(
            str(idx),
            src.title,
            src.source_type,
            f"{src.authority_score:.2f}",
            f"{src.relevance_score:.2f}",
            src.source_tool,
            src.url,
        )

    console.print(table)

    if output.facts:
        console.print(f"\n[bold cyan]Extracted Engineering Facts ({len(output.facts)} found):[/bold cyan]")
        for fact in output.facts[:5]:
            cat = f"[{fact.category}] " if fact.category else ""
            console.print(f"  • {cat}{fact.fact} [dim]({fact.source_url})[/dim]")

    console.print(
        f"\n[dim]Total Candidates Found: {output.sources_found} | Queries Used: {len(output.queries_used)}[/dim]\n"
    )


if __name__ == "__main__":
    main()
