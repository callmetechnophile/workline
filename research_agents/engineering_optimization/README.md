# EngineeringOptimizationAgent (Agent #20)

**WorkflowGuide AI — Engineering Optimization & Trade-Space Agent**

## Core Purpose

> **"WHICH FEASIBLE DESIGN IS BEST FOR THE DEFINED OBJECTIVE?"**

Agent #20 explores feasible engineering design alternatives and identifies optimal or Pareto-efficient solutions against explicit objectives, constraints, requirements, simulation results, and verified evidence.

## Key Invariants

- **Rejects vague objectives** (e.g., "make it better", "make it powerful") unless converted into explicit measurable objectives (MINIMIZE/MAXIMIZE with unit).
- **Hard Constraint Enforcement**: Candidates violating hard constraints (e.g., Tj > 80°C, power > 0.5W) are marked `INFEASIBLE` and **never recommended**.
- **Candidate Isolation**: All candidates are evaluated in isolated design branches. **Production BOM and architecture are never modified**.
- **Candidate Selection → Change Request**: Selecting a candidate creates an `OptimizationDecision` and submits a `ChangeRequest` via **Agent #16 (EngineeringChangeControlAgent)**. Never directly mutates project state.
- **Simulation Integration**: Physical simulation delegated exclusively to **Agent #19 (EngineeringSimulationAgent)**. No duplicate simulation engines.
- **Change Invalidation**: Upstream BOM/architecture changes mark optimization results as `STALE` or `INVALIDATED`.

## Optimization Flow

```
OBJECTIVES → VARIABLES → CONSTRAINTS → DESIGN SPACE → CANDIDATES
→ AGENT #19 SIMULATION → FEASIBILITY → OBJECTIVE EVALUATION
→ PARETO FRONTIER → TRADE-OFF ANALYSIS → RECOMMENDATION
→ HUMAN SELECTION → AGENT #16 CHANGE REQUEST → AGENT #14 LIFECYCLE
```

## CLI Usage

```bash
# Full optimization demonstration
python -m research_agents.engineering_optimization --demo

# Run optimization for a project
python -m research_agents.engineering_optimization run --project proj_sar_drone_001 --candidates 20

# Compute Pareto frontier
python -m research_agents.engineering_optimization pareto --opt-id OPT-XXXXXXXX

# Get recommendation
python -m research_agents.engineering_optimization recommend --opt-id OPT-XXXXXXXX

# Select candidate (creates decision + change request)
python -m research_agents.engineering_optimization select \
  --opt-id OPT-XXXXXXXX --candidate CAND-YYYYYYYY \
  --user engineer_001 --rationale "Best Pareto candidate"

# Check if stale after upstream BOM change
python -m research_agents.engineering_optimization reoptimize \
  --opt-id OPT-XXXXXXXX --bom-version v2.0.0

# Generate report
python -m research_agents.engineering_optimization report --opt-id OPT-XXXXXXXX
```

## Running Tests

```bash
pytest research_agents/engineering_optimization/tests/ -v
```

## Architecture

| Component | Description |
|-----------|-------------|
| `agent.py` | Google ADK-compliant `EngineeringOptimizationAgent` (14 capability methods) |
| `schemas.py` | Pydantic data contracts (`OptimizationObject`, `DesignCandidate`, `ParetoFrontierObject`, `OptimizationDecision`, etc.) |
| `config.py` | Optimization configuration (Bedrock, constraint tolerance, max candidates) |
| `services/design_space_engine.py` | Candidate generator, feasibility checker, Pareto frontier, weighted ranking, robustness |
| `services/reoptimization_engine.py` | Staleness detection and invalidation engine |
| `services/report_generator.py` | 21-section Markdown Optimization Report |
| `services/file_exporter.py` | 7 JSON and Markdown deliverables exporter |
| `repository/optimization_repository.py` | SurrealDB + in-memory graph repository |
| `providers/` | Bedrock LLM and mock reasoning providers |
| `tests/` | 12 test modules covering all specification scenarios |

## Integration with Platform

- **Agent #14** (ProjectLifecycleOrchestrator): Lifecycle state management
- **Agent #16** (EngineeringChangeControlAgent): Change request for selected candidates
- **Agent #17** (EngineeringComplianceAgent): Compliance failure → `INFEASIBLE`
- **Agent #18** (EngineeringVerificationAgent): Verification authority for optimization evidence
- **Agent #19** (EngineeringSimulationAgent): Physical simulation authority
