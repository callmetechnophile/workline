# EngineeringValidationAgent (Agent #9)

**EngineeringValidationAgent** is Agent #9 of the WorkflowGuide AI multi-agent engineering platform. It acts as the definitive **engineering quality gate** between design and physical implementation, verifying consistency across **Project Requirements (Agent #5)**, **System Architecture (Agent #6)**, **Engineering BOM (Agent #7)**, and the **Optimized Procurement Plan (Agent #8)**.

---

## 1. Architecture & Pipeline

```
User
  ↓
Research Orchestrator
  ↓
Agent #1 — ResearchPaperAgent (Academic Research via Freephdlabor)
  ↓
Agent #2 — WebResearchAgent (Engineering Web Evidence via Tavily + Anakin)
  ↓
Agent #3 — DocumentProcessingAgent (PDF/HTML Normalization, Markdown, Chunks, Facts, Entities)
  ↓
Agent #4 — DeepResearchAgent (Amazon Bedrock Cross-Source Reasoning & Evidence Synthesis)
  ↓
Agent #5 — EngineeringSynthesisAgent (Requirements, Findings, Trade-offs, Decisions, Risks, Validation)
  ↓
Agent #6 — EngineeringArchitectureAgent (Subsystems, Interfaces, Power, Data/Control Flows, Software, Graphs)
  ↓
Agent #7 — ComponentPlanningAgent (Engineering BOM, Exact/Candidate Components, Alternatives, Validation)
  ↓
Agent #8 — BOMOptimizationAgent (BOM Optimization, Supplier Consolidation, Landed Cost, Logistics)
  ↓
Agent #9 — EngineeringValidationAgent (Engineering Quality Gate, Design Rules, Verdict)
  ↓
Future Subsystems — Project Scheduling, Hardware Build & Firmware Execution
```

---

## 2. Core Principles & Priority

> [!IMPORTANT]
> **TECHNICAL VALIDITY ALWAYS OVERRIDES COST.**  
> Procurement optimization and supplier substitutions must never violate engineering requirements. Deterministic validation rules execute with absolute priority and cannot be overridden by LLMs. Any missing specifications are explicitly returned as `UNKNOWN` rather than assumed valid.

---

## 3. Modular Deterministic Design Rule Engine (`rules/`)

| Rule ID | Domain | Severity | Description |
|---|---|---|---|
| `RULE-ELEC-001` | Electrical | `CRITICAL` | Logic voltage mismatch (e.g. 5V output into 3.3V input without level shifting) |
| `RULE-POWER-001` | Power | `CRITICAL` | Total load current exceeding regulator / power rail capacity |
| `RULE-POWER-002` | Power | `HIGH` | Battery pack voltage, capacity, and flight runtime verification |
| `RULE-INT-001` | Interface | `CRITICAL` | Communication protocol and pinout direction mismatch |
| `RULE-INT-002` | Interface | `HIGH` | I2C slave address collision across shared buses |
| `RULE-RES-001` | Resource | `HIGH` | Microcontroller / SBC peripheral pin and channel capacity limits |
| `RULE-BOM-001` | BOM | `CRITICAL` | Required architectural subsystem component missing from BOM |
| `RULE-BOM-002` | BOM | `HIGH` | Component quantity mismatch across Architecture, BOM, and Procurement |
| `RULE-BOM-003` | BOM | `MEDIUM` | Missing supporting decoupling capacitors or circuit protection passives |
| `RULE-PROC-001` | Procurement | `CRITICAL` | Procurement substitution violates architecture interface requirements |
| `RULE-SW-001` | Software | `HIGH` | Toolchain, OS (ROS 2 / micro-ROS), and runtime architecture compatibility |
| `RULE-THERM-001` | Thermal | `MEDIUM` | Thermal dissipation and heatsink check for high-power compute |
| `RULE-MECH-001` | Mechanical | `LOW` | Mechanical mounting envelope and avionics weight limits |

---

## 4. Formal Verdicts & Blocking Gate

- `READY`: All rules pass; 0 critical or high blocking failures; 100% requirement coverage.
- `READY_WITH_WARNINGS`: Non-blocking design warnings; execution permitted with monitoring.
- `BLOCKED`: At least 1 CRITICAL or HIGH blocking failure.
- `INCOMPLETE`: Critical specifications missing (`UNKNOWN`).

---

## 5. 10-File Artifact Export Engine (Section 51)

When invoked with `--output <directory>`, the agent generates 10 distinct artifacts:

1. `validation.json`: Complete machine-readable validation dataset.
2. `validation_report.md`: Publication-ready 21-section Markdown report.
3. `validation_rules.json`: Individual design rule execution results.
4. `requirement_validation.json`: End-to-end requirement traceability evaluations.
5. `electrical_validation.json`: Electrical logic voltage checks.
6. `power_validation.json`: Power load and regulator headroom calculations.
7. `interface_validation.json`: Protocol and I2C address collision checks.
8. `bom_validation.json`: Architecture-to-BOM completeness and quantity checks.
9. `procurement_validation.json`: Procurement substitution compliance evaluations.
10. `validation_traceability.json`: Requirement-to-rule-to-verdict lineage records.

---

## 6. CLI Usage & Development Mode

```bash
# Run offline demo mode
python -m engineering_validation_agent --demo

# Run with custom architecture, BOM, and procurement files
python -m engineering_validation_agent \
    --architecture ./architecture.json \
    --bom ./bom.json \
    --procurement ./procurement_optimization.json \
    --output ./validation
```

---

## 7. Testing

Run all unit and integration tests across the platform:

```bash
pytest research_agents/engineering_validation_agent/tests/ -v
```
