# ArmorIQ Cryptographic Delegation & Verification Framework
===========================================================
**Specification Version: 1.0**  
**Classification: Security & Governance Contract**

---

## 1. Overview

**ArmorIQ** is the security, governance, and cryptographic audit framework underpinning all multi-agent workflows in WORKLINE. In an autonomous engineering environment where agents can formulate architectures, select electrical parts, and calculate thermal envelopes, strict provenance and authorization are mandatory.

ArmorIQ provides:
- **Delegation Tokens (`DEL-YYYY-XXXXX`):** Unique, cryptographically signed identifiers for every task delegated from a human user or parent agent to a sub-agent.
- **HMAC-SHA256 Receipts:** Verifiable execution receipts containing inputs, hashes of outputs, timestamps, and executor identifiers.
- **Approval Gates:** Mandatory policy checks preventing unverified mutation of core engineering documents.

---

## 2. Delegation Tokens & Chains

When the Engineering Copilot delegates a sub-task (e.g., BOM cost optimization to `bom_optimization_agent`):
1. An ArmorIQ token `DEL-2026-XXXXX` is minted.
2. The delegation record specifies:
   - `task_id`: Identifier of the engineering task.
   - `parent_agent`: Delegating authority (e.g., `user` or `engineering_copilot`).
   - `target_agent`: Assigned agent (e.g., `bom_optimizer`).
   - `scope`: Permitted operations (e.g., `read_bom`, `query_distributors`, `propose_candidates`).
3. Chains of delegation form an acyclic graph verifying how high-level project goals broke down into discrete agent executions.

---

## 3. Cryptographic Receipts

Upon completing an operation, the executing agent generates a receipt:
- **Receipt ID:** `REC-<timestamp>-<hash>`
- **Delegation ID:** Associated `DEL-2026-XXXXX` token
- **Input Digest:** SHA-256 digest of input parameters and context
- **Output Digest:** SHA-256 digest of generated candidate files or proposed diffs
- **HMAC Signature:** Cryptographic signature guaranteeing receipt integrity

Receipts are appended to `.wl/agents/receipts.wl` and stored in the local SurrealDB audit graph.

---

## 4. Governance & Human Approval Gates

Authoritative project mutations require clearance through ArmorIQ governance gates:
- Changes to `architecture/*.wl`, `requirements/*.wl`, and `bom/*.wl` are classified as **Authoritative Mutations**.
- Autonomous agents can generate and propose changes as draft candidate objects.
- Mutation approval requires either:
  1. An explicit human confirmation via `wline` CLI or the WORKLINE platform UI.
  2. A pre-approved automated policy rule matching strict tolerance criteria (e.g., replacement component has identical footprint, identical pinout, and lower cost).
