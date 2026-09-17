"""
wline engineering - Engineering-domain commands (simulation, optimization, DFM).

Routes to specialist domain agents via the AgentControlFabric:
  - simulation  → agent.19  (EngineeringSimulationAgent)
  - optimize    → agent.20  (EngineeringOptimizationAgent / Pareto)
  - dfm         → agent.24  (ManufacturingDFMAgent)
"""

import asyncio
import json
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel

from cli.wline.ui.output import print_error, print_info

engineering_app = typer.Typer(
    name="engineering",
    help="Engineering analysis: simulation, optimization, and DFM.",
)
console = Console()


def _fabric():
    from armourflow.fabric.fabric import get_control_fabric
    return get_control_fabric()


def _run_task(agent_id: str, capability: str, payload: dict, project: str):
    fabric = _fabric()
    return asyncio.run(
        fabric.submit_task(
            payload=payload,
            target_agent_id=agent_id,
            target_capability=capability,
            project_id=project,
        )
    )


@engineering_app.command("simulation")
def engineering_simulation(
    component: str = typer.Option("generic", "--component", "-c", help="Component name or ID to simulate"),
    scenario: str = typer.Option("static_load", "--scenario", "-s", help="Simulation scenario (e.g. static_load, thermal, fatigue)"),
    project: str = typer.Option("default", "--project", "-p", help="Project identifier"),
    payload: str = typer.Option("{}", "--payload", help="Additional simulation parameters as JSON"),
):
    """Run an engineering simulation study via agent.19 (EngineeringSimulationAgent)."""
    try:
        extra = json.loads(payload)
    except json.JSONDecodeError:
        print_error("--payload must be valid JSON.")
        raise typer.Exit(1)

    data = {"component": component, "scenario": scenario, **extra}
    console.print(f"[bold cyan]Engineering Simulation[/] → agent.19")
    console.print(f"  Component: [bold white]{component}[/]  Scenario: [dim]{scenario}[/]")

    task = _run_task("agent.19", "run_simulation", data, project)
    color = "green" if task.state.value == "COMPLETED" else "yellow"
    console.print(f"Task: [bold cyan]{task.task_id}[/]  State: [{color}]{task.state.value}[/]")
    if task.error:
        console.print(f"[bold red]Error:[/] {task.error}")
    elif task.result:
        console.print(Panel(json.dumps(task.result, indent=2, default=str), title="Simulation Results", border_style="green"))


@engineering_app.command("optimize")
def engineering_optimize(
    design: str = typer.Option("current", "--design", "-d", help="Design ID or descriptor to optimize"),
    objectives: str = typer.Option("weight,cost,performance", "--objectives", "-o", help="Comma-separated Pareto objectives"),
    project: str = typer.Option("default", "--project", "-p", help="Project identifier"),
    payload: str = typer.Option("{}", "--payload", help="Additional optimization parameters as JSON"),
):
    """Run multi-objective Pareto optimization via agent.20 (EngineeringOptimizationAgent)."""
    try:
        extra = json.loads(payload)
    except json.JSONDecodeError:
        print_error("--payload must be valid JSON.")
        raise typer.Exit(1)

    obj_list = [o.strip() for o in objectives.split(",")]
    data = {"design_id": design, "objectives": obj_list, **extra}
    console.print(f"[bold cyan]Pareto Optimization[/] → agent.20")
    console.print(f"  Design: [bold white]{design}[/]  Objectives: [dim]{objectives}[/]")

    task = _run_task("agent.20", "optimize_design", data, project)
    color = "green" if task.state.value == "COMPLETED" else "yellow"
    console.print(f"Task: [bold cyan]{task.task_id}[/]  State: [{color}]{task.state.value}[/]")
    if task.error:
        console.print(f"[bold red]Error:[/] {task.error}")
    elif task.result:
        console.print(Panel(json.dumps(task.result, indent=2, default=str), title="Optimization Results", border_style="green"))


@engineering_app.command("dfm")
def engineering_dfm(
    component: str = typer.Option("current", "--component", "-c", help="Component name or CAD reference"),
    process: str = typer.Option("injection_molding", "--process", help="Manufacturing process (e.g. cnc, injection_molding, casting)"),
    material: str = typer.Option("aluminum_6061", "--material", "-m", help="Material grade or class"),
    project: str = typer.Option("default", "--project", "-p", help="Project identifier"),
    payload: str = typer.Option("{}", "--payload", help="Additional DFM parameters as JSON"),
):
    """Run a Design-for-Manufacturability (DFM) check via agent.24 (ManufacturingDFMAgent)."""
    try:
        extra = json.loads(payload)
    except json.JSONDecodeError:
        print_error("--payload must be valid JSON.")
        raise typer.Exit(1)

    data = {"component": component, "manufacturing_process": process, "material": material, **extra}
    console.print(f"[bold cyan]Design For Manufacturability[/] → agent.24")
    console.print(f"  Component: [bold white]{component}[/]  Process: [dim]{process}[/]  Material: [dim]{material}[/]")

    task = _run_task("agent.24", "dfm_analysis", data, project)
    color = "green" if task.state.value == "COMPLETED" else "yellow"
    console.print(f"Task: [bold cyan]{task.task_id}[/]  State: [{color}]{task.state.value}[/]")
    if task.error:
        console.print(f"[bold red]Error:[/] {task.error}")
    elif task.result:
        console.print(Panel(json.dumps(task.result, indent=2, default=str), title="DFM Analysis", border_style="green"))
