"""
CLI entry point for DocumentProcessingAgent (Agent #3) test and development mode.
"""

import argparse
import sys
import tempfile
from typing import List

from rich.console import Console
from rich.table import Table

from research_agents.document_processing_agent.agent import DocumentProcessingAgent
from research_agents.document_processing_agent.schemas import DocumentProcessingInput


def main(args: List[str] = None):
    parser = argparse.ArgumentParser(
        description="WorkflowGuide AI — DocumentProcessingAgent (Agent #3) CLI Mode"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default=None,
        help="Local file path or remote document URL",
    )
    parser.add_argument(
        "--id",
        type=str,
        default="doc_sample_001",
        help="Document identifier",
    )
    parser.add_argument(
        "--title",
        type=str,
        default="Technical Specification Document",
        help="Document title hint",
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=["pdf", "html", "text", "auto"],
        default="auto",
        help="Document format type",
    )
    parser.add_argument(
        "--max-chunks",
        type=int,
        default=10,
        help="Maximum chunks to display",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run on a generated sample PDF document containing MCU and sensor specifications",
    )

    parsed = parser.parse_args(args)
    console = Console()

    temp_file = None
    input_path = parsed.input

    if parsed.demo or not input_path:
        # Synthesize demo text file
        temp_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8")
        temp_file.write(
            "# Autonomous UAV Thermal Inspection System\n\n"
            "## System Architecture\n"
            "The system utilizes an ESP32-S3 microcontroller operating at 3.3 V supply voltage. "
            "The MCU is clocked at 240 MHz with 8 MB Flash memory.\n\n"
            "## Sensor Interface\n"
            "A FLIR Lepton 3.5 thermal camera communicates over SPI and I2C interfaces. "
            "Current draw is 150 mA during active radiometric thermal capture.\n\n"
            "## Power Distribution\n"
            "A synchronous buck converter steps down 24 V battery power to 5.0 V logic supply with 3 A output capability.\n"
        )
        temp_file.close()
        input_path = temp_file.name

    input_data = DocumentProcessingInput(
        document_id=parsed.id,
        local_path=input_path if not input_path.startswith("http") else None,
        source_url=input_path if input_path.startswith("http") else None,
        document_type=parsed.type,
        title=parsed.title,
    )

    console.print(f"\n[bold cyan]WorkflowGuide AI[/bold cyan] — [bold green]DocumentProcessingAgent (Agent #3)[/bold green]")
    console.print(f"[dim]Document ID:[/dim] {input_data.document_id}")
    console.print(f"[dim]Source:[/dim] {input_path}")
    console.print(f"[dim]Type:[/dim] {input_data.document_type}\n")

    agent = DocumentProcessingAgent()
    output = agent.run_sync(input_data)

    if output.errors:
        console.print("[bold red]Processing Errors:[/bold red]")
        for err in output.errors:
            console.print(f"  • [{err.code}] {err.message}")

    if output.quality_warnings:
        console.print("[bold yellow]Quality Notices / Warnings:[/bold yellow]")
        for w in output.quality_warnings:
            console.print(f"  • {w}")
        console.print("")

    # Summary Table
    summary_tab = Table(title="Document Processing Summary")
    summary_tab.add_column("Metric", style="cyan")
    summary_tab.add_column("Value", style="white")

    summary_tab.add_row("Status", f"[bold green]{output.status.upper()}[/bold green]" if output.status == "success" else f"[bold red]{output.status.upper()}[/bold red]")
    summary_tab.add_row("Quality Score", f"{output.quality_score:.2f} / 1.00")
    summary_tab.add_row("Page Count", str(output.metadata.page_count))
    summary_tab.add_row("Sections Detected", str(len(output.sections)))
    summary_tab.add_row("Tables Extracted", str(len(output.tables)))
    summary_tab.add_row("Chunks Created", str(len(output.chunks)))
    summary_tab.add_row("Entities Found", str(len(output.entities)))
    summary_tab.add_row("Engineering Facts", str(len(output.facts)))

    console.print(summary_tab)

    # Chunks Table
    if output.chunks:
        chunk_tab = Table(title=f"Extracted Semantic Chunks (Showing top {min(len(output.chunks), parsed.max_chunks)})")
        chunk_tab.add_column("Chunk ID", style="cyan", no_wrap=True)
        chunk_tab.add_column("Section", style="yellow")
        chunk_tab.add_column("Pages", justify="center", style="magenta")
        chunk_tab.add_column("Est. Tokens", justify="right", style="green")
        chunk_tab.add_column("Text Preview", style="white", max_width=45)

        for c in output.chunks[:parsed.max_chunks]:
            page_str = f"p.{c.page_start}" if c.page_start == c.page_end else f"p.{c.page_start}-{c.page_end}"
            preview = c.text.replace("\n", " ")[:60] + "..." if len(c.text) > 60 else c.text
            chunk_tab.add_row(c.chunk_id, c.section, page_str, str(c.token_estimate), preview)

        console.print(chunk_tab)

    # Facts
    if output.facts:
        console.print("\n[bold cyan]Extracted Engineering Facts with Provenance:[/bold cyan]")
        for f in output.facts[:6]:
            norm_info = f" [green]-> ({f.normalized_value} {f.normalized_unit})[/green]" if f.normalized_value else ""
            console.print(f"  * [bold]{f.attribute or 'fact'}[/bold]: \"{f.fact}\"{norm_info} [dim](page {f.page})[/dim]")
        console.print("")


if __name__ == "__main__":
    main()
