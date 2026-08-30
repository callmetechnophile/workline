# BOMOptimizationAgent (Agent #8)

**BOMOptimizationAgent** is Agent #8 of the WorkflowGuide AI multi-agent engineering platform. It transforms the engineering Bill of Materials (BOM) produced by **ComponentPlanningAgent** (Agent #7) into an optimal, cost-effective, and logistically sound procurement plan across component pricing, availability, MOQ, bulk breaks, supplier consolidation, and Blue Dart shipping modes.

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
Future Subsystems — Project Scheduling, Team Collaboration & Purchasing Execution
```

---

## 2. Core Staged Pipeline

```
Agent #7 Engineering BOM
        ↓
Supplier Adapter Candidate Queries (Robu, Mouser, DigiKey, Probots, etc.)
        ↓
Technical Compatibility Gate (Filters incompatible parts & flags unapproved alternatives)
        ↓
Price Calculation (Unit Prices, MOQs, Price Breaks & Bulk Tiers)
        ↓
Blue Dart Logistics Engine (Surface vs Express Air quotes & distance matrix)
        ↓
Order Consolidation (Groups items by supplier to minimize freight charges)
        ↓
4 Deterministic Procurement Strategies (Cheapest, Fastest, Balanced, Min Suppliers)
        ↓
Alternative Component Economic Evaluation
        ↓
Cost Summary & Traceability Generation
        ↓
17-Section Markdown Procurement Report & 7-File Artifact Bundle
```

---

## 3. Mandatory Compatibility Gate

> [!IMPORTANT]
> **TECHNICAL CORRECTNESS ALWAYS PRECEDES COST OPTIMIZATION.**  
> Cost optimization never selects a cheaper component if it violates the engineering requirements established by Agent #7. Candidate components and alternatives must satisfy electrical logic levels, power ratings, package formats, and interface speeds before entering the optimization pool.

---

## 4. 4 Deterministic Procurement Strategies

1. **Lowest Landed Cost (`STRAT-001`)**: Minimizes total product cost + surface shipping.
2. **Fastest Delivery (`STRAT-002`)**: Prioritizes suppliers with shortest lead times and Blue Dart Air Express shipping.
3. **Minimum Number of Suppliers (`STRAT-003`)**: Consolidates orders to primary distributors to reduce administrative overhead.
4. **Balanced Cost + Delivery (`STRAT-004`)**: Balances product cost optimization with expedited express freight.

---

## 5. 7-File Artifact Export Engine (Section 47)

When invoked with `--output <directory>`, the agent generates 7 distinct artifacts:

1. `procurement_optimization.json`: Complete machine-readable optimization dataset.
2. `procurement_report.md`: Publication-ready 17-section Markdown report.
3. `optimized_bom.json`: Line-by-line procurement-assigned BOM items.
4. `supplier_comparison.json`: Comparative distributor pricing and lead-time summaries.
5. `shipping_analysis.json`: Order-level freight calculations and carrier allocations.
6. `procurement_strategies.json`: All 4 evaluated procurement strategies with financial metrics.
7. `procurement_traceability.json`: Requirement-to-supplier-to-landed-cost lineage records.

---

## 6. CLI Usage & Development Mode

```bash
# Run offline demo mode
python -m bom_optimization_agent --demo --destination "Bengaluru, Karnataka, India"

# Run with custom BOM input, budget, and export directory
python -m bom_optimization_agent \
    --input ./bom.json \
    --destination "Bengaluru, Karnataka, India" \
    --budget 100000 \
    --max-days 5 \
    --output ./procurement
```

---

## 7. Testing

Run all unit and integration tests across the platform:

```bash
pytest research_agents/bom_optimization_agent/tests/ -v
```

---

## 8. Separation of Concerns

The agent determines the optimal procurement plan, but **does not**:
- Place purchase orders
- Process payments or manage checkout
- Provide calendar scheduling
- Perform user-facing cart actions

This maintains modular separation for downstream fulfillment and project execution systems.
