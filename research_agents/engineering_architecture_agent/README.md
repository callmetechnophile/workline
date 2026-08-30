# EngineeringArchitectureAgent (Agent #6)

**EngineeringArchitectureAgent** is Agent #6 of the WorkflowGuide AI multi-agent engineering platform. It transforms the engineering decisions, requirements, constraints, findings, risks, and recommendations produced by **EngineeringSynthesisAgent** (Agent #5) into a concrete, multi-domain system architecture ready to feed **Agent #7 (BOM / Component Planning Agent)**.

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
Future Agent #7 — BOM / Component Planning Agent
```

---

## 2. Core Staged Pipeline

```
Project Requirements & Engineering Decisions
        ↓
Subsystem Decomposition & Functional Boundaries
        ↓
Component Role Mapping (Mandatory / Optional / Pending)
        ↓
Interface Design (Electrical, Protocol & Logic Voltages)
        ↓
Power Domain & Voltage Rail Architecture
        ↓
Data Flow, Control Flow & Closed-Loop Feedback Loops
        ↓
Software Architecture & HW/SW Responsibility Partitioning
        ↓
Architectural Dependency Graph
        ↓
Architecture Alternatives & Risk Analysis
        ↓
Block Diagram & Typed Architecture Graph Generation
        ↓
20-Section Markdown Architecture Report & 8-File Artifact Bundle
```

---

## 3. Mandatory Architecture Traceability

Every major architectural decision maintains an unbroken lineage:

$$\text{Project Requirement} \longrightarrow \text{Engineering Decision} \longrightarrow \text{Architecture Decision} \longrightarrow \text{Subsystem} \longrightarrow \text{Component / Interface} \longrightarrow \text{Validation}$$

```json
{
  "traceability_id": "TRACE-ARCH-001",
  "requirement_ids": ["REQ-001", "REQ-002"],
  "engineering_decision_ids": ["DEC-001"],
  "architecture_decision_ids": ["ARCH-DEC-001"],
  "subsystem_ids": ["SUB-001", "SUB-002"],
  "component_ids": ["NVIDIA Jetson Orin Nano 8GB", "FLIR Lepton 3.5"],
  "interface_ids": ["IF-001", "IF-002"],
  "validation_ids": ["VAL-ARCH-001", "VAL-ARCH-002"]
}
```

---

## 4. 8-File Artifact Export Engine (Section 45)

When invoked with `--output <directory>`, the agent generates 8 distinct artifacts:

1. `architecture.json`: Complete machine-readable system architecture object.
2. `architecture.md`: Comprehensive 20-section publication-ready Markdown report.
3. `architecture_graph.json`: Graph-ready node and edge relationships (typed).
4. `block_diagram.json`: Block diagram structure for UI rendering.
5. `subsystems.json`: Subsystem boundary and responsibility specifications.
6. `interfaces.json`: Inter-subsystem electrical, protocol, and bus interfaces.
7. `power_architecture.json`: Multi-rail power domains, regulators, and protection circuits.
8. `validation_requirements.json`: Architecture verification procedures and acceptance criteria.

---

## 5. CLI Usage & Development Mode

```bash
# Run offline demo mode
python -m engineering_architecture_agent --demo --project "Autonomous Search and Rescue Drone"

# Run with custom input bundle and export directory
python -m engineering_architecture_agent \
    --input ./engineering_synthesis.json \
    --output ./architecture
```

---

## 6. Testing

Run all unit and integration tests across the platform:

```bash
pytest research_agents/engineering_architecture_agent/tests/ -v
```

---

## 7. Downstream Hand-off to Agent #7

The agent outputs `component_requirements` containing categories, quantities, and required technical specs (e.g. `40 TOPS`, `8GB RAM`, `160x120 LWIR`, `3.3V logic`) without performing procurement, pricing, or vendor selection, providing a clean boundary for **Agent #7 (BOM / Component Planning Agent)**.
