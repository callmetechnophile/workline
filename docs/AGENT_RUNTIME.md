# WORKLINE Agent Runtime Architecture
===================================
**Specification Version: 1.0**  
**Classification: Core Runtime Contract**

---

## 1. Overview

The **WORKLINE Agent Runtime** provides a deterministic, local-first execution environment for autonomous and semi-autonomous engineering agents. The runtime coordinates specialized agents spanning system architecture, component planning, bill of materials (BOM) optimization, literature synthesis, and knowledge graph persistence.

```
                         USER
                          │
                          ▼
                  ┌──────────────┐
                  │   WORKLINE   │
                  │   PLATFORM   │
                  └──────┬───────┘
                         │
        ┌────────────────┼─────────────────┐
        │                │                 │
        ▼                ▼                 ▼
 Project Model      Agent Runtime      Workspace UI
        │                │
        │       ┌────────┼─────────┐
        │       │        │         │
        │      MCP      A2A      LiveKit
        │       │        │         │
        │       └────────┼─────────┘
        │                │
        ▼                ▼
   SurrealDB        Agent Router
                         │
              ┌──────────┼───────────┐
              │                      │
              ▼                      ▼
        Local Agents             Agent37
                                  Sandbox
              │                      │
              └──────────┬───────────┘
                         ▼
                  ProjectRetriever
                         │
                ┌────────┴────────┐
                ▼                 ▼
             Local Moss         Qdrant
          retrieval layer    vector database
```

---

## 2. Core Agents

The local runtime hosts specialized domain agents:
1. **Engineering Copilot (`engineering_copilot`):** Coordinates multi-step reasoning, architectural synthesis, and user dialogue.
2. **Component Planning Agent (`component_planning_agent`):** Handles parametric component selection, footprint constraints, and multi-source alternatives.
3. **BOM Optimization Agent (`bom_optimization_agent`):** Manages bill of materials cost curves, distributor stock checks, lead-time minimization, and lifecycle risk.
4. **Deep Research Agent (`deep_research_agent`):** Autonomous literature ingestion, scientific paper indexing, and technical trade-off evaluation.
5. **Engineering Knowledge Graph Agent (`engineering_knowledge_graph_agent`):** Manages relational graph structures, entity linking, and SurrealDB persistence.

---

## 3. Agent Router (`AgentRouter`)

The central dispatch engine for agent tasks is the `AgentRouter` (`backend/workline/agents/router.py`). When an agent task is triggered, the router evaluates:
- **Task Type:** Code analysis, web discovery, parametric optimization, documentation generation.
- **Data Sensitivity:** Internal proprietary schematics vs public datasheets.
- **Security Scope:** Authoritative mutations vs speculative exploration.

Based on this evaluation, the task is dispatched to one of three targets:
- `LOCAL`: Executed on the local machine using local LLMs or configured Bedrock/NIM providers.
- `AGENT37`: Dispatched to the isolated remote sandbox for untrusted or high-compute workloads (e.g., arbitrary web scraping, untrusted code execution).
- `EXTERNAL`: Delegated to approved external APIs.

---

## 4. Communication Protocols

Agents communicate through two standardized interfaces:
- **Model Context Protocol (MCP):** Exposes local project tools, file system operations, and database queries through structured JSON-RPC interfaces.
- **Agent-to-Agent (A2A):** Structured message exchanges, delegation chains, and collaborative problem-solving contracts.
- **LiveKit Realtime Protocol:** Voice and video channels for interactive human-in-the-loop copilot interactions.

---

## 5. Security & Zero-Secrets Invariant

1. **Zero Secret Persistence:** Agents NEVER store raw API keys, session tokens, or passwords in `.wl` project files, SurrealDB nodes, or Qdrant embeddings.
2. **Credential Injection:** Credentials are provided at runtime via `APICredentialManager` into ephemeral in-memory environment variables.
3. **Audit Trail:** Every action taken by an agent is tracked with an ArmorIQ delegation ID and logged in the immutable project history.
