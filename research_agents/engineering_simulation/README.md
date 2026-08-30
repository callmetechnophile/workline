# EngineeringSimulationAgent (Agent #19)

**EngineeringSimulationAgent** is Agent #19 of the WorkflowGuide AI multi-agent platform. It operates as the **engineering simulation, computational modeling, digital-twin representation, what-if analysis, parameter sweep, and simulation evidence engine** across the platform.

---

## 1. Multi-Agent Pipeline Position

```
User
  ↓
Research Orchestrator
  ↓
Agent #1 — ResearchPaperAgent (Academic Research via Freephdlabor)
  ↓
Agent #2 — WebResearchAgent (Engineering Web Evidence via Tavily + Anakin)
  ↓
Agent #3 — DocumentProcessingAgent (PDF/HTML Normalization, Chunks, Facts, Entities)
  ↓
Agent #4 — DeepResearchAgent (Amazon Bedrock Cross-Source Reasoning & Evidence Synthesis)
  ↓
Agent #5 — EngineeringSynthesisAgent (Requirements, Findings, Decisions, Risks)
  ↓
Agent #6 — EngineeringArchitectureAgent (Subsystems, Interfaces, Power, Flows, Graphs)
  ↓
Agent #7 — ComponentPlanningAgent (Engineering BOM, Exact Components, Validation)
  ↓
Agent #8 — BOMOptimizationAgent (BOM Optimization, Suppliers, Landed Cost, Logistics)
  ↓
Agent #9 — EngineeringValidationAgent (Engineering Quality Gate, Design Rules, Verdict)
  ↓
Agent #10 — ProjectExecutionAgent (Work Packages, Task Breakdown, Scheduling)
  ↓
Agent #11 — EngineeringExecutionAgent (Cryptographic ArmorIQ Scoped Implementation)
  ↓
Agent #12 — VerificationQAAgent (Independent Verification & Autonomous QA Quality Gate)
  ↓
Agent #13 — EngineeringKnowledgeGraphAgent (SurrealDB Graph & Project State Machine)
  ↓
Agent #14 — ProjectLifecycleOrchestrator (Autonomous Project Orchestrator & Lifecycle Manager)
  ↓
Agent #15 — EngineeringCopilotAgent (Natural-Language Engineering Copilot & Interface)
  ↓
Agent #16 — EngineeringChangeControlAgent (Change Control & Version Management Authority)
  ↓
Agent #17 — EngineeringComplianceAgent (Deterministic Engineering Compliance & Safety Gatekeeper)
  ↓
Agent #18 — EngineeringVerificationAgent (Engineering Verification, Test & Evidence Engine)
  ↓
Agent #19 — EngineeringSimulationAgent (Engineering Simulation & Digital Twin Engine)
  ↓
USER
```

---

## 2. Core Principles & Simulation Integrity

> [!IMPORTANT]
> **THE SIMULATION ENGINE (ZERO FABRICATION & WHAT-IF ISOLATION).**  
> - Answers: **"WHAT HAPPENS IF WE MODEL THIS?"**  
> - Strictly distinguishes: `THEORETICAL`, `MODELED`, `SIMULATED`, `MEASURED`, `VERIFIED`, `VALIDATED`.  
> - A simulation result does NOT automatically equal physical verification (Agent #18) or compliance (Agent #17).  
> - Never invents results, measurements, or model parameters.  
> - **What-If Isolation**: Exploratory what-if scenario branches **never modify** the production project BOM, architecture, or state.  
> - **Deterministic Unit System**: Physical units are checked deterministically ($P = V \times I$). Mismatched dimensions produce `MODEL_ERROR` and halt execution.  
> - **Change Invalidation**: When an upstream BOM/architecture changes in Agent #16, dependent models are marked `STALE`, existing simulation results are marked `INVALIDATED` (never deleted), and re-simulation is scheduled.

$$\text{MODEL} \longrightarrow \text{UNIT VALIDATION} \longrightarrow \text{SIMULATION} \longrightarrow \text{HASHED RESULT} \longrightarrow \text{AGENT \#18} \longrightarrow \text{AGENT \#17} \longrightarrow \text{SURREALDB}$$

---

## 3. Simulation Domains (15 Domains)

1. `ELECTRICAL`
2. `ELECTRONICS`
3. `POWER`
4. `THERMAL`
5. `SIGNAL`
6. `COMMUNICATION`
7. `CONTROL`
8. `MECHANICAL`
9. `FLUID`
10. `STRUCTURAL`
11. `SOFTWARE`
12. `PERFORMANCE`
13. `SYSTEM`
14. `NETWORK`
15. `AI_ML`

---

## 4. CLI Usage & Commands

```bash
# Full simulation demo run
python -m engineering_simulation --demo

# Run electro-thermal simulation
python -m engineering_simulation simulate \
    --project proj_sar_drone_001 \
    --voltage 3.3 \
    --current 150.0

# Run isolated what-if scenario branch
python -m engineering_simulation scenario \
    --project proj_sar_drone_001 \
    --description "What if sensor load doubles to 300mA?"

# Run parameter sweep
python -m engineering_simulation sweep \
    --project proj_sar_drone_001 \
    --param current_ma \
    --min 100.0 \
    --max 200.0 \
    --step 25.0

# Run Monte Carlo uncertainty analysis
python -m engineering_simulation monte-carlo \
    --samples 100 \
    --seed 42
```

---

## 5. Artifact File Exports (8 Files)

1. `digital_twin.json`
2. `model.json`
3. `simulation.json`
4. `simulation_result.json`
5. `scenario.json`
6. `sweep.json`
7. `simulation_evidence.json`
8. `simulation_report.md` (23-section Markdown report)

---

## 6. Automated Testing

```bash
pytest research_agents/engineering_simulation/tests/ -v
```
