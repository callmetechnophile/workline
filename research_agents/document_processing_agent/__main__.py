"""
CLI entry point for DocumentProcessingAgent (Agent #3) test and development mode (Section 35).
"""

import argparse
from pathlib import Path
import sys
import tempfile
import time
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
        "--output",
        "-o",
        type=str,
        default=None,
        help="Directory to save generated markdown, json, and metadata",
    )
    parser.add_argument(
        "--id",
        type=str,
        default=None,
        help="Document identifier (defaults to filename)",
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
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
        "--demo",
        action="store_true",
        help="Run on a generated sample document with MCU, sensor, and power specs",
    )

    parsed = parser.parse_args(args)
    console = Console()

    temp_file = None
    input_path = parsed.input

    if parsed.demo or not input_path:
        temp_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8")
        temp_file.write(
            "# Autonomous UAV Thermal Inspection System\n\n"
            "## System Architecture\n"
            "The system utilizes an ESP32-S3 microcontroller operating at 3.3 V supply voltage. "
            "The MCU is clocked at 240 MHz with 8 MB Flash memory.\n\n"
            "```cpp\n"
            "#include <Arduino.h>\n"
            "#include <Wire.h>\n"
            "void setup() { Serial.begin(115200); }\n"
            "```\n\n"
            "## Sensor Interface\n"
            "A FLIR Lepton 3.5 thermal camera communicates over SPI and I2C interfaces. "
            "Current draw is 150 mA during active radiometric thermal capture.\n\n"
            "## Power Distribution\n"
            "A synchronous buck converter steps down 24 V battery power to 5.0 V logic supply with 3 A output capability.\n"
        )
        temp_file.close()
        input_path = temp_file.name

    doc_id = parsed.id or Path(input_path).stem

    input_data = DocumentProcessingInput(
        document_id=doc_id,
        local_path=input_path if not input_path.startswith("http") else None,
        source_url=input_path if input_path.startswith("http") else None,
        document_type=parsed.type,
        title=parsed.title,
        output_dir=parsed.output,
    )

    start_t = time.time()
    agent = DocumentProcessingAgent()
    output = agent.run_sync(input_data)
    elapsed = time.time() - start_t

    doc_name = Path(input_path).name if not input_path.startswith("http") else input_path

    console.print(f"\n[bold cyan]Document:[/bold cyan] {doc_name}\n")
    console.print(f"Pages: {output.metadata.page_count if output.metadata else 1}")
    console.print(f"Sections: {len(output.sections)}")
    console.print(f"Tables: {len(output.tables)}")
    console.print(f"Figures: {len(output.figures)}")
    console.print(f"References: {len(output.references)}")
    console.print(f"Code Blocks: {len(output.code_blocks)}")
    console.print(f"Entities: {len(output.entities)}")
    console.print(f"Facts: {len(output.facts)}\n")

    console.print(f"Quality: [bold green]{output.quality_score:.2f}[/bold green]")
    console.print(f"Processing Time: {elapsed:.3f}s\n")

    if output.status == "success":
        console.print("[green]+[/green] Markdown generated")
        console.print("[green]+[/green] Metadata generated")
        console.print("[green]+[/green] Provenance preserved")
        if output.document and output.document.document_hash:
            console.print(f"[green]+[/green] Document Hash: [dim]{output.document.document_hash[:16]}...[/dim]")
        if parsed.output:
            console.print(f"[green]+[/green] Exported to: {parsed.output}")
    else:
        console.print(f"[bold red]Status: {output.status}[/bold red]")

    console.print("")


if __name__ == "__main__":
    main()
