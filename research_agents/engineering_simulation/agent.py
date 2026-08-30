"""
Agent #19: EngineeringSimulationAgent implementation using Google ADK conventions.
Generates computational models, executes simulations, runs what-if scenarios, and produces simulation evidence.
"""

import asyncio
from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid
from loguru import logger

from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.engineering_knowledge_graph_agent.services.graph_query import KnowledgeGraphService
from research_agents.engineering_simulation.config import simulation_config
from research_agents.engineering_simulation.providers.base import ReasoningProvider
from research_agents.engineering_simulation.providers.bedrock import BedrockSimulationProvider
from research_agents.engineering_simulation.repository.simulation_repository import SimulationRepository
from research_agents.engineering_simulation.schemas import (
    DigitalTwin,
    ModelAssumption,
    ModelObject,
    ParameterSweepObject,
    ScenarioObject,
    SimulationInput,
    SimulationObject,
    SimulationOutput,
    SimulationResult,
)
from research_agents.engineering_simulation.services.file_exporter import SimulationFileExporter
from research_agents.engineering_simulation.services.report_generator import SimulationReportGenerator
from research_agents.engineering_simulation.services.resimulation_engine import ReSimulationEngine
from research_agents.engineering_simulation.services.scenario_engine import ScenarioEngine
from research_agents.engineering_simulation.services.simulation_runner import SimulationRunner
from research_agents.engineering_simulation.services.unit_system import UnitEngine


class EngineeringSimulationAgent:
    """
    Google ADK-compliant Engineering Simulation Agent (Agent #19).
    Computational modeling, digital twin representation, what-if branching, and simulation evidence engine.
    """

    NAME = "EngineeringSimulationAgent"
    DESCRIPTION = (
        "Create and execute controlled engineering simulations and digital-twin "
        "models using validated project data, then generate traceable simulation "
        "evidence for engineering verification and decision-making."
    )
    CAPABILITIES = [
        "simulation.model",
        "simulation.twin",
        "simulation.execute",
        "simulation.scenario",
        "simulation.sweep",
        "simulation.evidence",
        "graph.read",
        "graph.insert",
        "graph.update",
    ]

    def __init__(
        self,
        db_client: Optional[SurrealDBClient] = None,
        reasoning_provider: Optional[ReasoningProvider] = None,
    ):
        self.db = db_client or SurrealDBClient()
        self.provider = reasoning_provider or BedrockSimulationProvider()
        self.repo = SimulationRepository(self.db)
        self.graph_service = KnowledgeGraphService(self.db)
        self.unit_engine = UnitEngine()
        self.runner = SimulationRunner()
        self.scenario_engine = ScenarioEngine()
        self.resim_engine = ReSimulationEngine()
        self.report_gen = SimulationReportGenerator()
        self.exporter = SimulationFileExporter()

    async def execute_simulation_cycle(
        self,
        input_data: SimulationInput,
        custom_inputs: Optional[Dict[str, Any]] = None,
        simulate_timeout: bool = False,
    ) -> SimulationOutput:
        """
        Executes complete simulation lifecycle:
        DIGITAL TWIN -> MODEL -> SIMULATION RUN -> SWEEPS -> SCENARIOS -> REPORT -> EXPORT
        """
        start_time = time.time()
        proj_id = input_data.project_id
        user_id = input_data.user_id

        # 1. Multi-User Project Isolation (Section 109)
        if not await self.graph_service.verify_project_access(proj_id, user_id):
            raise PermissionError(f"ACCESS_DENIED: User '{user_id}' lacks permission for project '{proj_id}'.")

        logger.info(f"[{self.NAME}] Initiating simulation cycle for project '{proj_id}'")

        # 2. Establish Digital Twin & Thermal Model
        twin_id = f"TWIN-{proj_id}"
        twin = DigitalTwin(
            twin_id=twin_id,
            project_id=proj_id,
            name="SAR Thermal Imaging Drone Subsystem Twin",
            version="v1.0.0",
            status="VALIDATED",
        )
        await self.repo.create_twin(twin)

        model_id = f"MODEL-POWER-{proj_id}"
        model = ModelObject(
            model_id=model_id,
            twin_id=twin_id,
            domain="POWER",
            description="Lepton 3.5 Sensor Core Steady-State Electro-Thermal Model",
            inputs=["voltage", "current_ma", "ambient_temp_c"],
            outputs=["power_dissipation_watts", "junction_temp_c"],
            parameters={"thermal_resistance": 45.0, "nominal_voltage": 3.3},
            assumptions=[
                ModelAssumption(
                    assumption_id="ASSUMP-01",
                    model_id=model_id,
                    description="Linear convective thermal dissipation; radiation negligible at <85°C.",
                )
            ],
            constraints=["junction_temp_c <= 85.0"],
        )
        await self.repo.create_model(model)

        # 3. Create Simulation Object
        sim_id = f"SIM-{proj_id}"
        sim_inputs = custom_inputs if custom_inputs is not None else {"voltage": 3.3, "current_ma": 150.0}
        simulation = SimulationObject(
            simulation_id=sim_id,
            project_id=proj_id,
            model_id=model_id,
            inputs=sim_inputs,
            parameters=model.parameters,
            conditions={"ambient_temp_c": 25.0},
        )
        await self.repo.create_simulation(simulation)

        # 4. Run Simulation Deterministically
        result = self.runner.run_simulation(
            simulation=simulation,
            model=model,
            simulate_timeout=simulate_timeout,
        )
        await self.repo.create_result(result)

        # 5. Run Parameter Sweep
        sweep = self.runner.run_parameter_sweep(
            simulation_id=sim_id,
            param_name="current_ma",
            range_min=100.0,
            range_max=200.0,
            step=25.0,
        )
        await self.repo.create_sweep(sweep)

        # 6. What-If Scenario (if requested or baseline scenario)
        scenarios: List[ScenarioObject] = []
        if input_data.what_if_scenario:
            scen = self.scenario_engine.create_scenario(
                project_id=proj_id,
                name="High Load Operating Scenario",
                description=input_data.what_if_scenario,
                changes={"parameters": {"current_ma": 300.0}},
            )
            await self.repo.create_scenario(scen)
            scenarios.append(scen)

        # 7. Generate 23-Section Markdown Report
        report_md = self.report_gen.generate_report(
            twin=twin,
            models=[model],
            simulations=[simulation],
            results=[result],
            scenarios=scenarios,
            sweeps=[sweep],
        )

        # 8. Assemble Output & Export
        output = SimulationOutput(
            twin=twin,
            models=[model],
            simulations=[simulation],
            results=[result],
            scenarios=scenarios,
            sweeps=[sweep],
            report_markdown=report_md,
        )

        if input_data.output_dir:
            exported = self.exporter.export_artifacts(
                output_dir=input_data.output_dir,
                twin=twin,
                models=[model],
                simulations=[simulation],
                results=[result],
                scenarios=scenarios,
                sweeps=[sweep],
                report_markdown=report_md,
            )
            output.exported_files = exported

        elapsed = time.time() - start_time
        logger.info(f"[{self.NAME}] Simulation cycle completed in {elapsed:.3f}s (Result={result.status})")

        return output

    def execute_simulation_cycle_sync(
        self,
        input_data: SimulationInput,
        custom_inputs: Optional[Dict[str, Any]] = None,
        simulate_timeout: bool = False,
    ) -> SimulationOutput:
        """Synchronous wrapper for ADK and CLI."""
        return asyncio.run(self.execute_simulation_cycle(input_data, custom_inputs, simulate_timeout))

    # =========================================================================
    # Google ADK Capability Methods (Section 70)
    # =========================================================================

    def run_simulation(
        self,
        project_id: str,
        voltage: float = 3.3,
        current_ma: float = 150.0,
        user_id: str = "user_001",
    ) -> SimulationResult:
        """ADK Capability: Executes deterministic electro-thermal simulation."""
        out = self.execute_simulation_cycle_sync(
            SimulationInput(project_id=project_id, user_id=user_id),
            custom_inputs={"voltage": voltage, "current_ma": current_ma},
        )
        return out.results[0]

    def run_scenario(
        self,
        project_id: str,
        scenario_description: str,
        changes: Dict[str, Any],
        user_id: str = "user_001",
    ) -> ScenarioObject:
        """ADK Capability: Creates an isolated what-if exploratory branch."""
        scen = self.scenario_engine.create_scenario(
            project_id=project_id,
            name="What-If Scenario",
            description=scenario_description,
            changes=changes,
        )
        self.repo._memory_scenarios[scen.scenario_id] = scen
        return scen

    def run_parameter_sweep(
        self,
        simulation_id: str,
        param_name: str,
        range_min: float,
        range_max: float,
        step: float,
    ) -> ParameterSweepObject:
        """ADK Capability: Executes multi-point parameter sweep."""
        sweep = self.runner.run_parameter_sweep(simulation_id, param_name, range_min, range_max, step)
        self.repo._memory_sweeps[sweep.sweep_id] = sweep
        return sweep
