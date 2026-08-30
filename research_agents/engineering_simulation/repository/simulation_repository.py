"""
SurrealDB repository for digital twins, computational models, simulations, and scenarios (Sections 57 & 58).
"""

from typing import Any, Dict, List, Optional
from loguru import logger
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.engineering_simulation.schemas import (
    CalibrationObject,
    DigitalTwin,
    ModelObject,
    ParameterSweepObject,
    ScenarioObject,
    SimulationObject,
    SimulationResult,
)


class SimulationRepository:
    """SurrealDB graph access repository for digital twin models and simulations."""

    def __init__(self, db_client: Optional[SurrealDBClient] = None):
        self.db = db_client or SurrealDBClient()
        self._memory_twins: Dict[str, DigitalTwin] = {}
        self._memory_models: Dict[str, ModelObject] = {}
        self._memory_sims: Dict[str, SimulationObject] = {}
        self._memory_results: Dict[str, SimulationResult] = {}
        self._memory_scenarios: Dict[str, ScenarioObject] = {}
        self._memory_sweeps: Dict[str, ParameterSweepObject] = {}

    async def create_twin(self, twin: DigitalTwin) -> DigitalTwin:
        try:
            await self.db.create_node("digital_twin", twin.twin_id, twin.model_dump())
            await self.db.relate_nodes(f"project:{twin.project_id}", "has_digital_twin", f"digital_twin:{twin.twin_id}")
        except Exception as e:
            logger.warning(f"SurrealDB create_twin fallback to memory: {e}")

        self._memory_twins[twin.twin_id] = twin
        return twin

    async def create_model(self, model: ModelObject) -> ModelObject:
        try:
            await self.db.create_node("model", model.model_id, model.model_dump())
            await self.db.relate_nodes(f"digital_twin:{model.twin_id}", "has_model", f"model:{model.model_id}")
        except Exception as e:
            logger.warning(f"SurrealDB create_model fallback: {e}")

        self._memory_models[model.model_id] = model
        return model

    async def create_simulation(self, sim: SimulationObject) -> SimulationObject:
        try:
            await self.db.create_node("simulation", sim.simulation_id, sim.model_dump())
            await self.db.relate_nodes(f"model:{sim.model_id}", "generates", f"simulation:{sim.simulation_id}")
        except Exception as e:
            logger.warning(f"SurrealDB create_simulation fallback: {e}")

        self._memory_sims[sim.simulation_id] = sim
        return sim

    async def create_result(self, result: SimulationResult) -> SimulationResult:
        try:
            await self.db.create_node("simulation_result", result.simulation_result_id, result.model_dump())
            await self.db.relate_nodes(f"simulation:{result.simulation_id}", "produces", f"simulation_result:{result.simulation_result_id}")
        except Exception as e:
            logger.warning(f"SurrealDB create_result fallback: {e}")

        self._memory_results[result.simulation_result_id] = result
        return result

    async def create_scenario(self, scenario: ScenarioObject) -> ScenarioObject:
        try:
            await self.db.create_node("scenario", scenario.scenario_id, scenario.model_dump())
        except Exception as e:
            logger.warning(f"SurrealDB create_scenario fallback: {e}")

        self._memory_scenarios[scenario.scenario_id] = scenario
        return scenario

    async def create_sweep(self, sweep: ParameterSweepObject) -> ParameterSweepObject:
        try:
            await self.db.create_node("parameter_sweep", sweep.sweep_id, sweep.model_dump())
        except Exception as e:
            logger.warning(f"SurrealDB create_sweep fallback: {e}")

        self._memory_sweeps[sweep.sweep_id] = sweep
        return sweep

    async def invalidate_simulation(self, sim_id: str) -> Optional[SimulationObject]:
        if sim_id in self._memory_sims:
            self._memory_sims[sim_id].status = "INVALIDATED"
            try:
                await self.db.upsert_node("simulation", sim_id, {"status": "INVALIDATED"})
            except Exception as e:
                logger.warning(f"SurrealDB invalidate simulation fallback: {e}")
            return self._memory_sims[sim_id]
        return None

    async def get_models(self) -> List[ModelObject]:
        return list(self._memory_models.values())

    async def get_simulations(self, project_id: str) -> List[SimulationObject]:
        return [s for s in self._memory_sims.values() if s.project_id == project_id]

    async def get_results(self) -> List[SimulationResult]:
        return list(self._memory_results.values())
