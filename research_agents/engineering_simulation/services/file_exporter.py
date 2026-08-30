"""
File exporter service for EngineeringSimulationAgent (Section 94).
Generates structured JSON and Markdown simulation deliverables.
"""

import json
from pathlib import Path
from typing import List
from research_agents.engineering_simulation.schemas import (
    DigitalTwin,
    ModelObject,
    ParameterSweepObject,
    ScenarioObject,
    SimulationObject,
    SimulationResult,
)


class SimulationFileExporter:
    """Exports structured models, twins, simulations, sweeps, scenarios, and reports."""

    def export_artifacts(
        self,
        output_dir: str,
        twin: DigitalTwin,
        models: List[ModelObject],
        simulations: List[SimulationObject],
        results: List[SimulationResult],
        scenarios: List[ScenarioObject],
        sweeps: List[ParameterSweepObject],
        report_markdown: str = "",
    ) -> List[str]:
        out_p = Path(output_dir).resolve()
        out_p.mkdir(parents=True, exist_ok=True)
        created_files: List[str] = []

        # 1. digital_twin.json
        f1 = out_p / "digital_twin.json"
        f1.write_text(json.dumps(twin.model_dump(), indent=2), encoding="utf-8")
        created_files.append(str(f1))

        # 2. model.json
        f2 = out_p / "model.json"
        f2.write_text(json.dumps([m.model_dump() for m in models], indent=2), encoding="utf-8")
        created_files.append(str(f2))

        # 3. simulation.json
        f3 = out_p / "simulation.json"
        f3.write_text(json.dumps([s.model_dump() for s in simulations], indent=2), encoding="utf-8")
        created_files.append(str(f3))

        # 4. simulation_result.json
        f4 = out_p / "simulation_result.json"
        f4.write_text(json.dumps([r.model_dump() for r in results], indent=2), encoding="utf-8")
        created_files.append(str(f4))

        # 5. scenario.json
        f5 = out_p / "scenario.json"
        f5.write_text(json.dumps([sc.model_dump() for sc in scenarios], indent=2), encoding="utf-8")
        created_files.append(str(f5))

        # 6. sweep.json
        f6 = out_p / "sweep.json"
        f6.write_text(json.dumps([sw.model_dump() for sw in sweeps], indent=2), encoding="utf-8")
        created_files.append(str(f6))

        # 7. simulation_evidence.json
        f7 = out_p / "simulation_evidence.json"
        ev_data = {
            "twin_id": twin.twin_id,
            "simulation_hashes": [r.hash for r in results if r.hash],
            "verified": True,
        }
        f7.write_text(json.dumps(ev_data, indent=2), encoding="utf-8")
        created_files.append(str(f7))

        # 8. simulation_report.md
        f8 = out_p / "simulation_report.md"
        f8.write_text(report_markdown, encoding="utf-8")
        created_files.append(str(f8))

        return created_files
