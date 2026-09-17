# Agent #24: Manufacturing / DFM-DFA Agent (`agent.24`)

**ManufacturingDFMAgent** bridges engineering design and manufacturing reality for **WorkflowGuide AI / ArmourFlow AI**. It evaluates whether designs can reliably, economically, and repeatably be manufactured and assembled.

---

## 1. Core Responsibilities & Authority Boundaries

- **Owns:**
  - Design-for-Manufacturing (DFM) Analysis
  - Design-for-Assembly (DFA) Analysis & Poka-Yoke Identification
  - Manufacturing Process Selection & Trade-Off Comparison
  - Tolerance & GD&T Manufacturability & 1D Stack-Up
  - Manufacturing Variation Analysis ($C_p, C_{pk}$) from Measured Data
  - Tooling & Fixture Complexity Evaluation
  - Process Sequencing & Inspection Gates
  - Manufacturing Readiness Gate Verdicts
  - Design Improvement Recommendations (Agent #16 Change Proposals)
  - Cost Driver Handoffs for Agent #25
- **Does NOT Own:**
  - General Risk & FMEA Authority (owned by Agent #21)
  - Reliability Analysis (owned by Agent #23)
  - Cybersecurity & File Integrity (owned by Agent #22)
  - Verification Authority (owned by Agent #18)
  - Simulation (owned by Agent #19)
  - Trade-Space Optimization (owned by Agent #20)
  - Change Approval (owned by Agent #16)
  - Release Orchestration (owned by Agent #14)

---

## 2. CLI Commands

```bash
# Complete DFM & DFA analysis
python -m research_agents.manufacturing_agent analyze --project PROJ-001

# Inspect readiness gates
python -m research_agents.manufacturing_agent readiness --project PROJ-001

# Generate 20-section report & JSON exports
python -m research_agents.manufacturing_agent report --project PROJ-001 --output output/manufacturing
```
