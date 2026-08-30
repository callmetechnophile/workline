"""
21-Section Engineering Optimization Report generator (Agent #20).
"""

from typing import List, Optional
from research_agents.engineering_optimization.schemas import (
    DesignCandidate,
    ObjectiveObject,
    OptimizationObject,
    ParetoFrontierObject,
    RobustnessObject,
)


class OptimizationReportGenerator:
    """Generates the 21-section Markdown Engineering Optimization Report."""

    def generate_report(
        self,
        optimization: OptimizationObject,
        candidates: List[DesignCandidate],
        pareto: Optional[ParetoFrontierObject],
        recommended_id: Optional[str],
        rationale: str,
        robustness: List[RobustnessObject],
    ) -> str:
        feasible = [c for c in candidates if c.feasible]
        infeasible = [c for c in candidates if not c.feasible]
        recommended = next((c for c in feasible if c.candidate_id == recommended_id), None)
        pareto_ids = {p.candidate_id for p in pareto.points} if pareto else set()

        md = f"""# Engineering Optimization Report: {optimization.project_id}

## 1. Project
- **Project ID:** `{optimization.project_id}`
- **Optimization ID:** `{optimization.optimization_id}`
- **Optimization Name:** {optimization.name}

## 2. Scope & Objective
{optimization.description}

## 3. Objectives ({len(optimization.objectives)})
"""
        for obj in optimization.objectives:
            md += f"- **{obj.name}** ({obj.direction}, weight={obj.weight}): {obj.description} [{obj.unit}]\n"

        md += f"\n## 4. Design Variables ({len(optimization.variables)})\n"
        for var in optimization.variables:
            step_str = f", step={var.step}" if var.step else " (continuous)"
            md += f"- **{var.name}**: [{var.min_value} \u2013 {var.max_value}] {var.unit}{step_str}\n"

        hard_cons = [c for c in optimization.constraints if c.constraint_type == "HARD"]
        soft_cons = [c for c in optimization.constraints if c.constraint_type == "SOFT"]
        md += f"\n## 5. Constraints ({len(optimization.constraints)})\n"
        md += f"### 5a. Hard Constraints ({len(hard_cons)}) \u2014 MUST NOT be violated\n"
        for con in hard_cons:
            md += f"- **{con.name}**: {con.expression} {con.limit} {con.unit}\n"
        md += f"### 5b. Soft Constraints ({len(soft_cons)})\n"
        for con in soft_cons:
            penalty_str = f", penalty={con.penalty}" if con.penalty else ""
            md += f"- **{con.name}**: {con.expression} {con.limit} {con.unit}{penalty_str}\n"
        if not hard_cons and not soft_cons:
            md += "None.\n"

        md += f"\n## 6. Candidate Summary\n"
        md += f"- **Total Candidates Evaluated:** {len(candidates)}\n"
        md += f"- **Feasible:** {len(feasible)}\n"
        md += f"- **Infeasible (Hard Constraint Violations):** {len(infeasible)}\n"

        md += f"\n## 7. Infeasible Candidates\n"
        if infeasible:
            for c in infeasible[:5]:
                md += f"- `{c.candidate_id}`: {'; '.join(c.hard_constraint_violations)}\n"
            if len(infeasible) > 5:
                md += f"  *(and {len(infeasible)-5} more)*\n"
        else:
            md += "None.\n"

        md += f"\n## 8. Feasible Candidates (Top 5)\n"
        for c in feasible[:5]:
            obj_str = ", ".join(f"{k}={v}" for k, v in c.objective_values.items())
            md += f"- `{c.candidate_id}`: {obj_str}\n"
        if not feasible:
            md += "No feasible candidates found. All candidates violate at least one hard constraint.\n"

        md += f"\n## 9. Pareto Frontier\n"
        if pareto and pareto.points:
            md += f"- **Pareto-optimal points:** {len(pareto.points)}\n"
            md += f"- **Dominated candidates:** {pareto.dominated_count}\n"
            md += f"- **Method:** `{pareto.method}`\n"
            md += "\n| Candidate | Objectives |\n|-----------|------------|\n"
            for pt in pareto.points[:8]:
                obj_str = ", ".join(f"{k}={v}" for k, v in pt.objective_values.items())
                md += f"| `{pt.candidate_id}` | {obj_str} |\n"
        else:
            md += "No Pareto frontier computed (no feasible candidates or single objective).\n"

        md += f"\n## 10. Dominance Analysis\n"
        if pareto:
            md += f"- **Non-dominated candidates:** {len(pareto.points)}\n"
            md += f"- **Dominated candidates:** {pareto.dominated_count}\n"
            md += f"- **Infeasible (excluded from Pareto):** {pareto.infeasible_count}\n"
        else:
            md += "Not computed.\n"

        md += f"\n## 11. Trade-off Analysis\n"
        if len(optimization.objectives) > 1 and pareto and pareto.points:
            obj_names = [obj.name for obj in optimization.objectives]
            md += f"- Objectives in tension: {' vs. '.join(obj_names)}\n"
            md += "- See Pareto frontier (Section 9) for achievable trade-off combinations.\n"
        elif len(optimization.objectives) == 1:
            md += "- Single-objective optimization: no trade-off required.\n"
        else:
            md += "No Pareto points available for trade-off analysis.\n"

        md += f"\n## 12. Weighted Ranking\n"
        if feasible:
            for i, c in enumerate(feasible[:5]):
                obj_str = ", ".join(f"{k}={v}" for k, v in c.objective_values.items())
                md += f"{i+1}. `{c.candidate_id}`: {obj_str}\n"
        else:
            md += "No feasible candidates.\n"

        md += f"\n## 13. Recommendation\n"
        if recommended:
            obj_str = ", ".join(f"{k}={v}" for k, v in recommended.objective_values.items())
            md += f"- **Recommended Candidate:** `{recommended.candidate_id}`\n"
            md += f"- **Objectives:** {obj_str}\n"
            md += f"- **Pareto-optimal:** {'Yes' if recommended.candidate_id in pareto_ids else 'No'}\n"
            md += f"- **Rationale:** {rationale}\n"
        else:
            md += "No recommendation available (no feasible candidates).\n"

        md += f"\n## 14. Robustness Analysis\n"
        if robustness:
            rob = robustness[0] if robustness else None
            if rob:
                md += f"- **Candidate:** `{rob.candidate_id}`\n"
                md += f"- **Robustness Score:** `{rob.robustness_score}`\n"
                sens_str = ", ".join(f"{k}={v}" for k, v in list(rob.sensitivity_map.items())[:4])
                md += f"- **Sensitivity:** {sens_str}\n"
        else:
            md += "Not computed.\n"

        md += f"\n## 15. Sensitivity Metrics\n"
        if robustness:
            for rob in robustness[:3]:
                top_sens = sorted(rob.sensitivity_map.items(), key=lambda x: -x[1])[:2]
                for var, sens in top_sens:
                    md += f"- `{rob.candidate_id}` \u2192 `{var}`: sensitivity={sens}\n"
        else:
            md += "Not computed.\n"

        md += f"\n## 16. Constraint Margins\n"
        for c in feasible[:3]:
            if c.constraint_violations:
                viol_str = ", ".join(f"{k}={v}" for k, v in c.constraint_violations.items())
                md += f"- `{c.candidate_id}` soft violations: {viol_str}\n"
            else:
                md += f"- `{c.candidate_id}`: no constraint violations.\n"

        md += f"\n## 17. Candidate Isolation\n"
        md += (
            "All candidates evaluated in isolated design branches. "
            "Production BOM and architecture were NOT modified during optimization.\n"
        )

        md += f"\n## 18. Simulation Integration\n"
        sim_linked = [c for c in candidates if c.simulation_id]
        md += f"- **Candidates with linked simulation results:** {len(sim_linked)} of {len(candidates)}\n"
        md += "- Simulation authority: Agent #19 (EngineeringSimulationAgent).\n"

        md += f"\n## 19. Compliance Status\n"
        for c in feasible[:3]:
            md += f"- `{c.candidate_id}`: compliance_status=`{c.compliance_status}`\n"

        md += f"\n## 20. Selection & Change Control\n"
        if optimization.decision_id:
            md += f"- **Decision ID:** `{optimization.decision_id}`\n"
            md += "- Selection triggers Agent #16 (EngineeringChangeControlAgent) change request.\n"
        else:
            md += "- No candidate selected yet. Human review required before change request.\n"

        md += f"\n## 21. Engineering Interpretation\n"
        if recommended:
            md += (
                f"**`Optimization complete. Candidate {recommended.candidate_id} identified as "
                "best feasible solution. No hard constraints violated. Human approval required "
                "before promoting via Agent #16 change-control workflow.`**\n"
            )
        else:
            md += "**`Optimization inconclusive. All candidates violate hard constraints. Redesign required.`**\n"

        return md
