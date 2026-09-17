"""
wline eval - Evaluation harness commands for agent benchmark execution.

Uses the UniversalEvaluationHarness (armourflow.evals) which executes
structured benchmark suites against registered domain agents.
"""

import asyncio
import json
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cli.wline.ui.output import print_error, print_info

eval_app = typer.Typer(
    name="eval",
    help="Run benchmark suites and view evaluation reports.",
)
console = Console()


def _harness():
    from armourflow.evals import get_evaluation_harness
    return get_evaluation_harness()


@eval_app.command("run")
def eval_run(
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Run benchmarks for a specific agent ID; omit for all"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show individual benchmark case results"),
):
    """Execute evaluation benchmarks against registered agents."""
    harness = _harness()

    if agent:
        console.print(f"[bold cyan]Eval:[/] Benchmarking agent [bold white]{agent}[/]...")
        summary = asyncio.run(harness.evaluate_agent(agent))
        if not summary:
            print_error(f"No benchmark suite found for agent '{agent}'.")
            raise typer.Exit(1)

        table = Table(title=f"Benchmark Results: {agent}", border_style="cyan")
        table.add_column("Benchmark Name", style="bold white")
        table.add_column("Category", style="cyan")
        table.add_column("Status", justify="center")

        for b in summary.benchmarks:
            table.add_row(
                b.name,
                b.category,
                "[bold green]PASS[/]" if b.passed else "[bold red]FAIL[/]",
            )

        console.print(table)
        color = "green" if summary.score_percentage == 100.0 else "yellow"
        console.print(
            f"Pass Rate: [{color}]{summary.score_percentage}%[/] "
            f"({summary.passed_benchmarks}/{summary.total_benchmarks})"
        )

    else:
        console.print("[bold cyan]Eval:[/] Running platform-wide benchmarks...")
        report = asyncio.run(harness.run_platform_benchmarks())

        table = Table(title="Platform Benchmark Summary", border_style="cyan")
        table.add_column("Agent ID", style="bold cyan")
        table.add_column("Benchmarks", justify="right")
        table.add_column("Passed", justify="right")
        table.add_column("Score %", justify="right")

        for aid, s in report.agent_summaries.items():
            color = "green" if s.score_percentage == 100.0 else "yellow"
            table.add_row(
                aid,
                str(s.total_benchmarks),
                str(s.passed_benchmarks),
                f"[{color}]{s.score_percentage}%[/]",
            )

        console.print(table)
        console.print(
            f"\nOverall: [bold green]{report.overall_pass_rate}%[/] "
            f"({report.total_passed}/{report.total_benchmarks} across {report.total_agents_evaluated} agents)"
        )


@eval_app.command("report")
def eval_report(
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Filter report to a specific agent ID"),
    output_json: bool = typer.Option(False, "--json", help="Output raw JSON report"),
):
    """Print a summary evaluation report across all evaluated agents."""
    harness = _harness()

    if agent:
        summary = asyncio.run(harness.evaluate_agent(agent))
        if not summary:
            print_error(f"No evaluation data for agent '{agent}'.")
            raise typer.Exit(1)
        report_data = {
            "agent_id": agent,
            "score_percentage": summary.score_percentage,
            "total_benchmarks": summary.total_benchmarks,
            "passed_benchmarks": summary.passed_benchmarks,
            "benchmarks": [{"name": b.name, "category": b.category, "passed": b.passed} for b in summary.benchmarks],
        }
    else:
        report = asyncio.run(harness.run_platform_benchmarks())
        report_data = {
            "overall_pass_rate": report.overall_pass_rate,
            "total_benchmarks": report.total_benchmarks,
            "total_passed": report.total_passed,
            "total_agents_evaluated": report.total_agents_evaluated,
            "agents": {
                aid: {
                    "score": s.score_percentage,
                    "passed": s.passed_benchmarks,
                    "total": s.total_benchmarks,
                }
                for aid, s in report.agent_summaries.items()
            },
        }

    if output_json:
        console.print(Panel(json.dumps(report_data, indent=2), title="Eval Report (JSON)", border_style="cyan"))
    else:
        console.print(Panel(json.dumps(report_data, indent=2), title="Evaluation Report", border_style="cyan"))
