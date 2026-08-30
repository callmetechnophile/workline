"""
CLI entry point for EngineeringSimulationAgent (Agent #19) (Sections 85–93).
Supports model, twin, simulate, scenario, sweep, monte-carlo, impact, resimulate, and --demo.
"""

import argparse
import json
from pathlib import Path
import sys
from typing import List, Optional

from research_agents.engineering_simulation.agent import EngineeringSimulationAgent
from research_agents.engineering_simulation.providers.mock_provider import MockSimulationProvider
from research_agents.engineering_simulation.schemas import SimulationInput


def main(args: List[str] = None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="WorkflowGuide AI — EngineeringSimulationAgent (Agent #19) CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Simulation commands")

    # simulate command
    p_sim = subparsers.add_parser("simulate", help="Execute computational simulation")
    p_sim.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")
    p_sim.add_argument("--voltage", type=float, default=3.3, help="Supply voltage (V)")
    p_sim.add_argument("--current", type=float, default=150.0, help="Operating current (mA)")
    p_sim.add_argument("--output", type=str, help="Output directory")

    # scenario command
    p_scen = subparsers.add_parser("scenario", help="Run isolated what-if scenario branch")
    p_scen.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")
    p_scen.add_argument("--description", type=str, default="Double sensor load scenario", help="Scenario description")

    # sweep command
    p_swp = subparsers.add_parser("sweep", help="Run parameter sweep")
    p_swp.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")
    p_swp.add_argument("--param", type=str, default="current_ma", help="Parameter name")
    p_swp.add_argument("--min", type=float, default=100.0, help="Min value")
    p_swp.add_argument("--max", type=float, default=200.0, help="Max value")
    p_swp.add_argument("--step", type=float, default=25.0, help="Step size")

    # monte carlo command
    p_mc = subparsers.add_parser("monte-carlo", help="Run Monte Carlo uncertainty analysis")
    p_mc.add_argument("--samples", type=int, default=100, help="Number of samples")
    p_mc.add_argument("--seed", type=int, default=42, help="Random seed")

    parser.add_argument("--demo", action="store_true", help="Run simulation demonstration")

    parsed = parser.parse_args(args)
    agent = EngineeringSimulationAgent(reasoning_provider=MockSimulationProvider())

    if parsed.demo or not parsed.command:
        inp = SimulationInput(project_id="proj_sar_drone_001")
        out = agent.execute_simulation_cycle_sync(inp)
        print(f"\nDigital Twin: {out.twin.twin_id} ({out.twin.name})")
        print(f"Model: {out.models[0].model_id} ({out.models[0].domain})")
        print(f"Simulation Status: {out.results[0].status} (Hash: {out.results[0].hash[:12]})")
        print("\nOutputs Computed:")
        for k, v in out.results[0].outputs.items():
            print(f"- {k}: {v}")
        print("\nParameter Sweep Summary:")
        print(f"- Parameter: {out.sweeps[0].parameter_name} ({out.sweeps[0].samples} sample points)")
        for pt in out.sweeps[0].results:
            print(f"  * {pt['current_ma']} mA -> {pt['power_watts']} W -> {pt['temp_c']} °C")

    elif parsed.command == "simulate":
        inp = SimulationInput(project_id=parsed.project, output_dir=parsed.output)
        out = agent.execute_simulation_cycle_sync(
            inp,
            custom_inputs={"voltage": parsed.voltage, "current_ma": parsed.current},
        )
        print(f"\nProject: {parsed.project}")
        print(f"Simulation: {out.simulations[0].simulation_id}")
        print(f"Status: {out.results[0].status}")
        print(f"Power Dissipation: {out.results[0].outputs.get('power_dissipation_watts')} W")
        print(f"Junction Temp: {out.results[0].outputs.get('junction_temp_c')} °C")

    elif parsed.command == "scenario":
        scen = agent.run_scenario(
            project_id=parsed.project,
            scenario_description=parsed.description,
            changes={"parameters": {"load": 2.0}},
        )
        print(f"\nScenario Created: {scen.scenario_id}")
        print(f"Name: {scen.name}")
        print(f"Description: {scen.description}")
        print(f"Status: {scen.status} (Base Project Unchanged)")

    elif parsed.command == "monte-carlo":
        mc_res = agent.runner.run_monte_carlo("SIM-001", samples=parsed.samples, random_seed=parsed.seed)
        print(f"\nMonte Carlo Analysis ({parsed.samples} samples, Seed: {parsed.seed}):")
        print(f"- Mean Power: {mc_res['mean_power_watts']} W")
        print(f"- Mean Junction Temp: {mc_res['mean_junction_temp_c']} °C")
        print(f"- 95% Confidence Interval: {mc_res['confidence_interval_95']} °C")


if __name__ == "__main__":
    main()
