# Agent37 Isolated Remote Sandbox Integration
=============================================
**Specification Version: 1.0**  
**Classification: Execution Architecture**

---

## 1. Overview

**Agent37** is an optional, isolated remote execution sandbox used by WORKLINE to perform speculative, untrusted, or heavy-compute tasks without risking local host security or corrupting authoritative project state.

> [!IMPORTANT]
> Agent37 is **NOT** the core engineering runtime of WORKLINE. WORKLINE is fundamentally local-first. Agent37 is an auxiliary execution sandbox delegated on-demand.

---

## 2. Security Boundaries & Invariants

To maintain the integrity of WORKLINE engineering projects:
1. **No Authoritative State Mutation:** Agent37 has strictly **read-only** or sandboxed write access. It cannot write directly to production BOMs, system architecture, or local SurrealDB.
   - Denied scopes: `bom_write`, `architecture_write`, `database_write`, `git_push`.
   - Allowed scopes: `web`, `browser`, `pdf_download`, `simulation_run`.
2. **Ephemeral Sandboxes:** Each delegated task runs in a freshly provisioned, short-lived container sandbox identified by a UUID.
3. **Artifact Verification Gates:** Output artifacts (such as scraped datasheets, candidate component alternatives, or simulation logs) are collected by `Agent37Adapter` and presented to WORKLINE for verification before being committed to the `.wl` project filesystem.
4. **Credential Isolation:** Agent37 only receives scoped, temporary tokens. Long-lived credentials are never passed into the sandbox.

---

## 3. Architecture & Adapter

The `Agent37Adapter` (`backend/workline/agents/agent37_adapter.py`) manages the lifecycle:

```
  ┌─────────────────┐       Execute Task       ┌──────────────────────┐
  │   AgentRouter   │ ───────────────────────> │    Agent37Adapter    │
  └─────────────────┘                          └──────────┬───────────┘
                                                          │ Provision
                                                          ▼
                                               ┌──────────────────────┐
                                               │   Agent37 Sandbox    │
                                               │   (Isolated Pod)     │
                                               └──────────┬───────────┘
                                                          │ Collect Artifacts
                                                          ▼
  ┌─────────────────┐      Human / Policy      ┌──────────────────────┐
  │ Production .wl  │ <─────────────────────── │  Verification Gate   │
  └─────────────────┘         Approval         └──────────────────────┘
```

---

## 4. Configuration

Agent37 credentials are configured via the WORKLINE API Manager:
```bash
wline apis
# or
wline --apis
```
Under **Agent37 Sandbox**, configure:
- `AGENT37_API_KEY`: API Key for the Agent37 sandbox controller.
- `AGENT37_ENDPOINT`: Custom controller endpoint (defaults to `https://api.agent37.io/v1`).
