"""
CLI entry point for DeepResearchAgent (Agent #4) development mode.
"""

import argparse
from pathlib import Path
import sys
import time
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from research_agents.deep_research_agent.agent import DeepResearchAgent
from research_agents.deep_research_agent.providers.mock_provider import MockReasoningProvider
from research_agents.deep_research_agent.schemas import (
    DeepResearchAgentInput,
    ProjectMeta,
)


def main(args: List[str] = None):
    parser = argparse.ArgumentParser(
        description="WorkflowGuide AI — DeepResearchAgent (Agent #4) CLI Development Mode"
    )
    parser.add_argument(
        "--project",
        "-p",
        type=str,
        default="Autonomous Search and Rescue Drone",
        help="Project title",
    )
    parser.add_argument(
        "--domain",
        type=str,
        default="Robotics / Edge AI / UAV",
        help="Engineering discipline",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run offline demo with sample papers, web evidence, and mock Bedrock reasoning",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Optional path to write generated markdown synthesis report",
    )

    parsed = parser.parse_args(args)
    console = Console()

    # Build input context
    project_meta = ProjectMeta(
        project_id="proj_sar_drone_001",
        title=parsed.project,
        description="A UAV system using thermal imaging and edge computer vision to locate lost humans in disaster zones.",
        engineering_domain=parsed.domain,
        objectives=["thermal human detection", "edge inference under 100ms", "payload power under 20W"],
        components=["NVIDIA Jetson Orin Nano", "FLIR Lepton 3.5", "ESP32-S3"],
        technologies=["YOLOv8n", "TensorRT", "ROS 2 Humble"],
        constraints=["real-time inference >= 30 FPS", "total payload power <= 20 W"],
    )

    # Fixture research evidence for demo
    sample_papers = [
        {
            "paper_id": "paper_tro_2024",
            "title": "Thermal Human Detection on Edge UAVs using Quantized Neural Networks",
            "abstract": "We demonstrate a 45 FPS thermal human detection pipeline deployed on Jetson Orin Nano consuming 15 W.",
            "year": 2024,
            "doi": "10.1109/TRO.2024.001",
        }
    ]
    sample_web = [
        {
            "source_id": "web_nvidia_orin",
            "title": "NVIDIA Jetson Orin Nano Technical Specifications",
            "extracted_content": "NVIDIA Jetson Orin Nano delivers up to 40 TOPS AI compute with 6-core ARM CPU and Ampere GPU at 15 W power mode.",
            "source_type": "manufacturer_documentation",
            "url": "https://developer.nvidia.com/embedded/jetson-orin-nano",
        }
    ]
    sample_facts = [
        {
            "fact": "FLIR Lepton 3.5 radiometric thermal sensor operates at 3.3 V with SPI video and I2C command interface.",
            "source_document": "datasheet_lepton_35",
            "page": 4,
            "confidence": 0.98,
        }
    ]

    input_data = DeepResearchAgentInput(
        project=project_meta,
        research_papers=sample_papers,
        web_sources=sample_web,
        facts=sample_facts,
    )

    console.print(f"\n[bold cyan]WorkflowGuide AI[/bold cyan] — [bold green]DeepResearchAgent (Agent #4)[/bold green]")
    console.print(f"[dim]Project:[/dim] {project_meta.title}")
    console.print(f"[dim]Domain:[/dim] {project_meta.engineering_domain}\n")

    # In demo mode or offline test, use MockReasoningProvider
    if parsed.demo or True:  # Default to mock in CLI unless explicit AWS configured
        agent = DeepResearchAgent(reasoning_provider=MockReasoningProvider())
    else:
        agent = DeepResearchAgent()

    start_t = time.time()
    output = agent.run_sync(input_data)
    elapsed = time.time() - start_t

    # Render Executive Summary Panel
    console.print(Panel(output.executive_summary, title="Executive Engineering Summary", style="cyan"))

    # Render Component Trade Study Table
    if output.component_trade_studies:
        table = Table(title="Component Trade Studies")
        table.add_column("Subsystem", style="yellow")
        table.add_column("Candidates Evaluated", style="white")
        table.add_column("Recommended Choice", style="bold green")
        table.add_column("Key Rationale", style="white", max_width=45)

        for study in output.component_trade_studies:
            table.add_row(
                study.component_type,
                ", ".join(study.candidates_evaluated),
                study.recommended_option,
                study.recommendation_reason,
            )
        console.print(table)

    # Render Claims Separation Table
    if output.extracted_claims:
        claim_tab = Table(title="Synthesized Claims (Fact vs. Inference vs. Recommendation)")
        claim_tab.add_column("Type", style="magenta")
        claim_tab.add_column("Claim Statement", style="white", max_width=50)
        claim_tab.add_column("Evidence IDs", style="dim", no_wrap=True)

        for c in output.extracted_claims:
            ev_str = ", ".join(c.source_evidence_ids) if c.source_evidence_ids else "N/A"
            claim_tab.add_row(c.claim_type, c.claim, ev_str)
        console.print(claim_tab)

    # Render Contradictions if any
    if output.contradictions:
        console.print("\n[bold yellow]Contradiction Resolutions:[/bold yellow]")
        for ct in output.contradictions:
            console.print(f"  * [bold]{ct.topic}:[/bold] {ct.resolution}")

    # Render Actionable Recommendations
    if output.recommendations:
        console.print("\n[bold cyan]Actionable Engineering Recommendations:[/bold cyan]")
        for idx, rec in enumerate(output.recommendations, 1):
            console.print(f"  {idx}. [[bold]{rec.priority.upper()}[/bold]] {rec.recommendation} ({rec.category})")
            console.print(f"     [dim]{rec.justification}[/dim]")

    console.print(f"\n[dim]Synthesized in {elapsed:.3f}s across {len(output.evidence_used)} evidence items.[/dim]\n")

    # Export markdown if requested
    if parsed.output:
        out_p = Path(parsed.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(output.structured_markdown_report, encoding="utf-8")
        console.print(f"[green]+[/green] Report written to: {parsed.output}\n")


if __name__ == "__main__":
    main()
