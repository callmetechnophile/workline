# ComponentPlanningAgent (Agent #7)

**ComponentPlanningAgent** is Agent #7 of the WorkflowGuide AI multi-agent engineering platform. It transforms the multi-domain system architecture produced by **EngineeringArchitectureAgent** (Agent #6) into a technically valid, structured engineering Bill of Materials (BOM) ready to feed future procurement and cost optimization subsystems.

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
Future Subsystems — Procurement / Cost Optimization / Vendor Selection
```

---

## 2. Core Staged Pipeline

```
System Architecture
        ↓
Subsystem Requirements
        ↓
Component Requirements
        ↓
Component Category Identification
        ↓
Specification Extraction (Required vs Known)
        ↓
Candidate Component Selection
        ↓
Compatibility Validation (Electrical, Power, Interface, Mechanical, Software)
        ↓
Quantity Determination
        ↓
Supporting Component & Passive Identification
        ↓
Alternative Component Identification & Classification
        ↓
BOM Construction & Grouping
        ↓
BOM Validation & Resource Conflict Detection
        ↓
Procurement-Ready Component Dataset
```

---

## 3. Mandatory BOM Traceability

Every BOM line item maintains an unbroken lineage:

$$\text{Project Requirement} \longrightarrow \text{Architecture Subsystem} \longrightarrow \text{Component Requirement} \longrightarrow \text{Selected Component} \longrightarrow \text{Specification} \longrightarrow \text{Validation}$$

```json
{
  "traceability_id": "TRACE-BOM-001",
  "requirement_ids": ["REQ-001"],
  "subsystem_ids": ["SUB-001"],
  "component_requirement_ids": ["COMP-REQ-001"],
  "bom_item_ids": ["BOM-001"],
  "validation_ids": ["VAL-BOM-001"]
}
```

---

## 4. 7-File Artifact Export Engine (Section 46)

When invoked with `--output <directory>`, the agent generates 7 distinct artifacts:

1. `bom.json`: Complete machine-readable engineering Bill of Materials.
2. `bom.md`: Comprehensive publication-ready Markdown BOM report grouped by subsystem.
3. `bom_items.json`: Detailed specifications, interfaces, and power limits per BOM item.
4. `component_requirements.json`: Derived technical requirements from architecture.
5. `component_alternatives.json`: Evaluated alternative components with compatibility classifications.
6. `bom_validation.json`: Pre-procurement electrical, power, and interface verification procedures.
7. `bom_traceability.json`: Requirement-to-component-to-validation traceability lineage.

---

## 5. CLI Usage & Development Mode

```bash
# Run offline demo mode
python -m component_planning_agent --demo --project "Autonomous Search and Rescue Drone"

# Run with custom architecture input and export directory
python -m component_planning_agent \
    --input ./architecture.json \
    --output ./bom
```

---

## 6. Testing

Run all unit and integration tests across the platform:

```bash
pytest research_agents/component_planning_agent/tests/ -v
```

---

## 7. Strict Separation from Procurement

The agent identifies manufacturer part numbers, technical specifications, datasheets, supporting passives, and alternatives, but **does not** perform:
- Live price scraping
- Shipping or tax calculations
- Vendor price optimization
- Order placement or checkout
- Payment processing

This provides a clean, modular boundary for future procurement and supply chain agents.
