# WORKLINE Project Format Standard (`.wl`)

## Overview

The `.wl` format defines a modular, human-readable, and machine-indexable open filesystem layout for engineering projects.
The `.wl` filesystem is the **authoritative source of truth** for project data when working locally.

---

## Directory Hierarchy

```
<project-root>/
├── README.wl                         # Primary project entrypoint & index card (v2 Schema)
├── workline.yaml                     # Standard wline CLI compatibility descriptor
├── .wl/                              # Hidden engine metadata
│   ├── manifest.wl                   # Project identity & resource index
│   ├── moss.wl                       # Local retrieval index state & metadata
│   ├── livekit.wl                    # Room binding (Zero secrets)
│   └── index/                        # Local Moss retrieval index artifacts
│
├── requirements/                     # Functional, technical, and constraint requirements
│   ├── functional.wl
│   ├── technical.wl
│   └── constraints.wl
├── architecture/                     # System block diagrams, subsystem definitions
│   ├── system.wl
│   └── components.wl
├── components/                       # Parametric component dossiers (one per MPN)
├── bom/                              # Bill of Materials line items and supplier links
│   ├── bom.wl
│   └── bom.csv
├── research/                         # Literature reviews, academic papers, scientific citations
├── documents/                        # Specifications, compliance standards, notes
├── analysis/                         # Power budgets, thermal simulations, DRC results
│   ├── power.wl
│   ├── thermal.wl
│   └── pcb.wl
├── decisions/                        # Architectural Decision Records (ADRs)
├── tasks/                            # Work breakdown schedules and milestone tasks
├── team/                             # Team member roles, assignments, and contact cards
├── agents/                           # Multi-agent governance policies and receipts
└── history/                          # Event activity log and change provenance
```

---

## `README.wl` — Version 2.0 Specification

`README.wl` combines human readability with strict structured parsing:

```yaml
WORKLINE_PROJECT
================

name: Battery Management System 16S Pro
project_id: BMS-16S-PRO
version: 2.1
status: ACTIVE
domain: power-electronics
description: Industrial 16S LiFePO4 battery management system with active balancing.
schema_version: "2.0"
generated_at: 2026-09-23T10:00:00Z
source_workline_version: 1.0.0

# ── Project Intent ───────────────────────────────────────────────────
intent:
  goal: Design an active-balancing 16S battery management system.
  problem_statement: Ensure cell voltage variance remains below 15mV under 100A discharge.
  target_platform: stm32
  budget_usd: 450.0
  constraints:
    - Maximum PCB dimension 120mm x 80mm
    - Continuous discharge current 80A, peak 150A

# ── Project State ────────────────────────────────────────────────────
state:
  stage: architecture
  phase: active
  completion_pct: 35
  last_updated: 2026-09-23T10:00:00Z
  active_milestone: M2-Schematic-Review

# ── Analysis Entrypoints ─────────────────────────────────────────────
analysis_entrypoint:
  primary: analysis/power.wl
  power_analysis: analysis/power.wl
  thermal_analysis: analysis/thermal.wl
  pcb_analysis: analysis/pcb.wl

# ── LiveKit Realtime Session ─────────────────────────────────────────
livekit:
  room_name: workline-project-BMS-16S-PRO
  enabled: true
  session_ttl_minutes: 60

# ── Moss Local Retrieval Index ────────────────────────────────────────
moss:
  status: READY
  document_count: 54
  indexed_at: 2026-09-23T10:05:00Z
  index_path: .wl/index/

# ── Resource Summary ─────────────────────────────────────────────────
team:
  team_name: Power Electronics Group
  members_count: 3
architecture:
  subsystems: 4
requirements:
  total: 18
components:
  total_mpns: 32
bom:
  total_line_items: 45
research:
  indexed_papers: 6
documents:
  total_docs: 4
analysis:
  reports_count: 3
tasks:
  total_tasks: 12
decisions:
  recorded_decisions: 5
agents:
  configured_agents: 2
history:
  recorded_events: 19
```

---

## `.wlipjt` vs `.wl/`

| Dimension | `.wl/` Filesystem | `.wlipjt` Archive |
| :--- | :--- | :--- |
| **Purpose** | Live workspace and daily editing | Portable snapshot, backup, and cross-team export |
| **Storage Structure** | Plain directory with `.wl` text files | Compressed ZIP archive with TOON-serialized records |
| **Integrity** | Direct OS filesystem operations | Cryptographic `checksums.toon` SHA-256 hash manifest |
| **Secrets Policy** | User-controlled (sanitized by default) | **Strictly Sanitized**: All keys/tokens scrubbed before export |
