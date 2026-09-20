# Multi-Agent Architecture: WorkflowGuide AI / ArmourFlow AI

## Overview
WorkflowGuide AI / ArmourFlow AI coordinates 27 specialized engineering and research agents through an orchestrated, cryptographically governed pipeline.

```
USER INTENT
    │
    ▼
PLANNER AGENT (Root Receipt Generated)
    │
    ├──► RESEARCH CLUSTER (A2A Protocol & Bindu SDK)
    │     ├── Deep Research Agent
    │     ├── Tavily Web Search Agent
    │     ├── PhD Literature Agent
    │     └── Cross-Disciplinary Research Agent
    │
    ├──► EXTRACTION & COMPONENT CLUSTER
    │     ├── Component Extraction Agent
    │     ├── Component Planning Agent
    │     └── Supply Chain & Procurement Agent
    │
    ├──► SYNTHESIS & OPTIMIZATION CLUSTER
    │     ├── BOM Generation Agent
    │     ├── Engineering Optimization Agent (Pareto Frontiers)
    │     ├── Hardware Design Agent
    │     └── PCB Design Agent
    │
    ├──► SIMULATION & VALIDATION CLUSTER
    │     ├── Hardware Thermal & EDA Agent
    │     ├── Power Integrity Agent
    │     └── Compliance & Verification QA Agent
    │
    └──► DOCUMENTATION & EXPORT CLUSTER
          ├── Documentation Agent
          └── PDF/CAD/Gantt Export Engine
```

---

## 1. Multi-Agent Frameworks & Interoperability
- **Google ADK (Agent Development Kit):** Used for agent prompt structuring, context windows, and tool function schemas.
- **A2A Protocol (Agent-to-Agent):** Enables peer agent communication where outputs from one agent (e.g., thermal hotspot coordinates from Agent #23) become structured inputs for another (e.g., PCB trace thermal dissipation in Agent #13).
- **Bindu Intelligence SDK:** Connects internal engineering agents with external research entities and cross-domain data sources.
- **AWS Step Functions:** Manages the outer state machine execution, supporting checkpointing, parallel branch joins, and retry policies.

---

## 2. Cryptographic Governance via ArmorIQ SDK
Every delegation between agents is strictly audited and cryptographically verified:
1. **Plan Capture (`capture_plan`):** Generates a root HMAC-signed receipt defining the maximum allowable scope for the user's intent.
2. **Delegation (`delegate`):** Parent agents delegate only a scoped subset of tools to sub-agents. If a child agent requests tools outside its boundary, ArmorIQ halts execution, raises a `ScopeViolationError`, records the violation in CloudWatch, and publishes a `PolicyViolation` event to EventBridge.
3. **Tool Invocation (`invoke_tool`):** Validates the cryptographic receipt signature before executing downstream services.
