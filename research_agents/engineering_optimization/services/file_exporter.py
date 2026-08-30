"""
File exporter for EngineeringOptimizationAgent (Agent #20).
Generates structured JSON and Markdown optimization deliverables.
"""

import json
from pathlib import Path
from typing import List, Optional

from research_agents.engineering_optimization.schemas import (
    DesignCandidate,
    OptimizationDecision,
    OptimizationObject,
    ParetoFrontierObject,
    RobustnessObject,
)


class OptimizationFileExporter:
    """Exports optimization objects, candidates, Pareto frontiers, decisions, and reports."""

    def export_artifacts(
        self,
        output_dir: str,
        optimization: OptimizationObject,
        candidates: List[DesignCandidate],
        pareto: Optional[ParetoFrontierObject],
        decision: Optional[OptimizationDecision],
        robustness: List[RobustnessObject],
        report_markdown: str = "",
    ) -> List[str]:
        out_p = Path(output_dir).resolve()
        out_p.mkdir(parents=True, exist_ok=True)
        created_files: List[str] = []

        # 1. optimization.json
        f1 = out_p / "optimization.json"
        f1.write_text(json.dumps(optimization.model_dump(), indent=2), encoding="utf-8")
        created_files.append(str(f1))

        # 2. design_space.json
        f2 = out_p / "design_space.json"
        design_space = {
            "objectives": [o.model_dump() for o in optimization.objectives],
            "variables": [v.model_dump() for v in optimization.variables],
            "constraints": [c.model_dump() for c in optimization.constraints],
        }
        f2.write_text(json.dumps(design_space, indent=2), encoding="utf-8")
        created_files.append(str(f2))

        # 3. candidates.json
        f3 = out_p / "candidates.json"
        f3.write_text(json.dumps([c.model_dump() for c in candidates], indent=2), encoding="utf-8")
        created_files.append(str(f3))

        # 4. pareto_frontier.json
        f4 = out_p / "pareto_frontier.json"
        f4.write_text(
            json.dumps(pareto.model_dump() if pareto else {}, indent=2), encoding="utf-8"
        )
        created_files.append(str(f4))

        # 5. robustness.json
        f5 = out_p / "robustness.json"
        f5.write_text(json.dumps([r.model_dump() for r in robustness], indent=2), encoding="utf-8")
        created_files.append(str(f5))

        # 6. optimization_decision.json
        f6 = out_p / "optimization_decision.json"
        f6.write_text(
            json.dumps(decision.model_dump() if decision else {}, indent=2), encoding="utf-8"
        )
        created_files.append(str(f6))

        # 7. optimization_report.md
        f7 = out_p / "optimization_report.md"
        f7.write_text(report_markdown, encoding="utf-8")
        created_files.append(str(f7))

        return created_files
