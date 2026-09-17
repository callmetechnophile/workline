# ADR-005: 3-Tier Action Separation & Lifecycle Governance Gates

## Status
Accepted

## Context
To ensure engineering safety and compliance, autonomous agents must never commit financial purchases or release unverified hardware designs autonomously.

## Decision
Implement strict governance:
1. 3-Tier Action Separation (`backend/workline/security/`):
   - Tier 1: `RECOMMENDATION` (autonomous reads, proposals, optimizations)
   - Tier 2: `AUTHORIZED_ACTION` (explicit signoff by human reviewer/engineer)
   - Tier 3: `EXECUTED_ACTION` (state mutation, physical order dispatch)
2. Lifecycle Stage Gates (`backend/workline/pipeline/gates.py`):
   - Simulation Gate: Releases blocked if physics/thermal simulation fails or temperature > 105°C.
   - Sourcing Gate: Orders blocked if BOM contains obsolete/EOL components or lacks human signoff.

## Consequences
- Strict compliance with safety standards.
- Clear separation between agent intelligence and authoritative executive signoff.
