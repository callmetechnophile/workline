# Agent #25: Cost & Supply Chain Agent (`CostSupplyChainAgent`)

Part of the **WorkflowGuide AI / ArmourFlow AI** engineering platform.

## Overview
Agent #25 provides authoritative engineering cost estimation, hierarchical BOM cost rollups, cost driver identification (including DFM/DFA manufacturing penalties), supplier capability scoring, sourcing and lead-time analysis, MOQ feasibility, supply chain risk detection (single-source, obsolescence, geopolitical concentration), make-vs-buy breakeven crossover modeling, and engineering change cost impact assessment.

## Key Architectural Principles
- **Zero Fabrication Rule**: Missing prices, lead times, or MOQs are strictly reported as `PRICE_UNKNOWN` or `DATA_REQUIRED`. The agent never hallucinates or guesses costs.
- **Authority Boundaries**:
  - Does NOT execute purchasing or contracts (Engineering cost estimation only).
  - Proposes changes to Agent #16 (`EngineeringChangeControlAgent`); cannot directly overwrite production BOMs.
  - Ingests physical manufacturing and tooling insights from Agent #24 (`ManufacturingDFMAgent`).
- **SurrealDB & Bedrock Integration**: Graph persistence with multi-tenant isolation on `project_id`, `team_id`, and `user_id`.

## CLI Usage
```bash
# Run standalone BOM analysis
python -m research_agents.cost_supply_chain --project-id PROJ-101 --volume 5000 --currency USD

# Run 5-point evaluation harness
python -m research_agents.cost_supply_chain --eval
```
