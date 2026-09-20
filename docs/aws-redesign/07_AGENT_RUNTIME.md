# Workline Agent Runtime, Control Fabric & Execution Engine

**Document ID:** `WORKLINE-AWS-07`  
**Status:** CANONICAL RUNTIME SPECIFICATION  

---

## 1. Agent Control Fabric: Authoritative Orchestrator

The Workline Control Fabric (`armourflow/fabric/fabric.py`) is the authoritative coordinator across all 27 agents and 90 capabilities.

```
                     ┌────────────────────────┐
                     │    Workline API / BFF  │
                     └───────────┬────────────┘
                                 │ Dispatches Task Contract
                                 ▼
                     ┌────────────────────────┐
                     │  Agent Control Fabric  │
                     │  - State Machine       │
                     │  - Capability Matcher  │
                     │  - Idempotency Gate    │
                     └───────────┬────────────┘
                                 │
           ┌─────────────────────┼─────────────────────┐
           │ Enqueue Task        │ Query Graph State   │ Semantic Retrieval
           ▼                     ▼                     ▼
     ┌───────────┐         ┌───────────┐         ┌───────────┐
     │ Amazon SQS│         │ SurrealDB │         │   Qdrant  │
     └─────┬─────┘         └───────────┘         └───────────┘
           │ Long Poll
           ▼
     ┌────────────────────────┐
     │ ECS Agent Worker Pool  │
     │ - Dedicated Containers │
     │ - PyTorch / PINN Env   │
     │ - Agent Registry #1-27 │
     └───────────┬────────────┘
                 │
           ┌─────┴───────────────┐
           ▼                     ▼
     ┌───────────┐         ┌───────────┐
     │ Amazon S3 │         │ LLM Gate  │
     │ (Artifact)│         │ (Bedrock) │
     └───────────┘         └───────────┘
```

---

## 2. Invariant Rules for Agent Communication

1. **NO Direct Python Imports Between Agents:**
   - Agents must never directly import classes or functions from other agent packages in `research_agents/`.
   - Inter-agent collaboration is strictly mediated through the **Control Fabric** using structured, versioned Pydantic schemas.
2. **Authoritative State in SurrealDB:**
   - Every task transition (`SUBMITTED` $\rightarrow$ `QUEUED` $\rightarrow$ `RUNNING` $\rightarrow$ `COMPLETED` / `FAILED`) is committed directly to SurrealDB.
   - Findings, design decisions, and generated Pareto candidates are written into SurrealDB graph tables.
3. **Semantic Retrieval in Qdrant:**
   - Agents query Qdrant for relevant technical datasheets, component specifications, and historical research findings.
4. **Artifact Offloading to S3:**
   - Heavy computation outputs (CAD STEP models, Gerber ZIP archives, thermal field matrices `.npz`, high-resolution heatmaps) are saved to S3.
   - Only the S3 URI, SHA-256 hash, and metadata are persisted in SurrealDB.
5. **Agent Manifest #23 Correction (BUG-002):**
   - Correct `armourflow/registry/manifests/agent.23.json` to properly map to `HardwareThermalAgent` (`research_agents/hardware_thermal_agent/`), fixing the current misdirected pointer to `SecurityThreatModelingAgent`.
