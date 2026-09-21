# WORKLINE Project Filesystem Specification (.wl)
=================================================
**Standard Specification Document: Version 1.0**  
**Author:** WORKLINE Architecture & Systems Engineering  
**Classification:** Open Standard & System Contract  

---

## 1. Abstract & System Role

The **WORKLINE Project Filesystem (`.wl`)** is the open, versioned, portable, and machine-readable filesystem convention for complete engineering projects. 

Modern hardware and robotics projects require heterogeneous context: multi-domain requirements, system block diagrams, component parameters, supplier catalogs, academic papers, thermal analyses, PCB stackups, architectural decisions (ADRs), and autonomous agent execution receipts. 

Trapping this context inside a proprietary database makes projects non-portable and inaccessible to developer CLI workflows. The `.wl` specification establishes an authoritative, deterministic contract connecting:

$$\text{WORKLINE Web} \iff \text{WORKLINE SDK} \iff \text{WORKLINE CLI (wg)} \iff \text{.wl Filesystem} \iff \text{Cloud / Git Providers}$$

Any project packaged as a `.wl` directory or self-contained `.workline.zip` can be opened, analyzed, synthesized, and verified decades into the future without depending on external web services or runtime database state.

---

## 2. Directory Hierarchy

A compliant `.wl` project filesystem conforms to the following directory layout:

```text
<project-root>/
├── README.wl                         # Primary human & machine CLI discovery entry point
│
├── .wl/                              # Manifest, core metadata, and dependency indexes
│   ├── manifest.wl                   # Cryptographic resource map & file inventory
│   ├── project.wl                    # Canonical project identity, domain, and status
│   ├── architecture.wl               # High-level system architecture summary
│   ├── requirements.wl               # Requirements index & compliance verification summary
│   ├── team.wl                       # Team ownership and role hierarchy
│   ├── agents.wl                     # Autonomous agent configurations & governance model
│   ├── dependencies.wl               # Software, firmware, and CAD toolchain dependencies
│   └── metadata.wl                   # File format version and export timestamps
│
├── requirements/                     # Verifiable engineering requirements
│   ├── functional.wl                 # Deterministic functional behaviors
│   ├── technical.wl                  # Parametric specifications, tolerances, and ripple
│   ├── constraints.wl                # Mechanical envelopes, thermals, and operating limits
│   └── acceptance.wl                 # Design gates and quality criteria
│
├── architecture/                     # System architecture & interface topologies
│   ├── system.wl                     # Subsystem blocks, inputs, and outputs
│   ├── components.wl                 # Subsystem-to-MPN architectural bindings
│   ├── services.wl                   # Bus communications, protocols (CAN-FD, SPI, UART)
│   ├── dataflow.wl                   # Signal paths, interrupt lines, and power distribution
│   └── architecture.json             # Full graph-traversable JSON schema
│
├── components/                       # Per-component dossiers
│   ├── index.wl                      # Master index of all project MPNs
│   └── <component-mpn>/              # Directory per distinct component MPN
│       ├── component.wl              # Identity, category, package, lifecycle, RoHS
│       ├── specifications.wl         # Parametric boundaries (voltage, temperature, power)
│       ├── sourcing.wl               # Preferred distributor, distributor P/N, unit cost, MOQ
│       └── datasheet.wl              # Datasheet reference, storage tier, and URL
│
├── bom/                              # Bill of Materials & Procurement
│   ├── bom.wl                        # Structured bill of materials with line items
│   ├── bom.csv                       # Standard RFC-4180 CSV export (DigiKey/Mouser format)
│   └── sourcing.wl                   # Supplier catalog, total procurement cost, lead times
│
├── research/                         # Literature indexing & scientific consensus
│   ├── index.wl                      # Literature catalog and index
│   ├── papers/                       # Individual paper dossiers (<paper-slug>.wl)
│   └── findings.wl                   # Synthesized research takeaways & trade-off resolutions
│
├── documents/                        # Technical specifications & regulatory contracts
│   ├── index.wl                      # Document library catalog
│   └── files/                        # Modular specification documents and compliance checklists
│
├── analysis/                         # Multi-physics and electrical simulation reports
│   ├── power.wl                      # Power rail budget, current consumption, battery runtime
│   ├── thermal.wl                    # Thermal dissipation profile, junction temperatures, cooling
│   ├── pcb.wl                        # Layer stackup, trace clearances, board envelope
│   └── reports/                      # Executive engineering readiness reports
│
├── decisions/                        # Architectural Decision Records (ADRs)
│   ├── index.wl                      # Chronological index of engineering trade-offs
│   └── decisions/                    # Modular ADR files (<adr-id>.wl)
│
├── tasks/                            # Work breakdown, sprints, and Gantt milestones
│   ├── index.wl                      # Task catalog and milestone summary
│   └── tasks/                        # Modular task dossiers (<task-id>.wl)
│
├── agents/                           # Multi-agent governance and cryptographic audit
│   ├── index.wl                      # Configured agent capabilities and LLM backbones
│   ├── delegations.wl                # Directed delegation chain from Root Planner
│   └── receipts.wl                   # ArmorIQ HMAC-SHA256 verifiable receipts
│
├── team/                             # Collaboration, identity, and RBAC policies
│   ├── members.wl                    # Active project members and roles
│   ├── roles.wl                      # Role permission matrix (OWNER, ADMIN, ENGINEER, VIEWER)
│   └── permissions.wl                # Data export authorization rules
│
├── history/                          # Immutable event ledger
│   └── activity.wl                   # Audit trail of design revisions and state changes
│
├── exports/                          # Export records & provenance logs
│   └── index.wl                      # Catalog of past exports and external sync targets
│
├── .gitignore                        # Git exclusion rules for secrets and temporary build files
├── .worklineignore                   # Standard WORKLINE exclusion rules (.wlignore)
└── .wlignore                         # Symlink/mirror of .worklineignore
```

---

## 3. Core Entry Points

### 3.1 `README.wl`
The `README.wl` file is located at the root of the project. It serves as the primary machine-readable overview for the WORKLINE CLI (`wg`) and autonomous AI agents.

Unlike standard Markdown files, `README.wl` uses a structured YAML-like format with reserved section headers:

```yaml
WORKLINE_PROJECT
================

name:
Autonomous Delivery Drone Power Distribution

project_id:
PROJ-AUTO

version:
1.0

status:
ACTIVE

domain:
Hardware Systems & Power Engineering

description:
Autonomous multi-agent engineering research package for high-efficiency power distribution.

generated_at:
2026-09-21T21:42:00Z

source_workline_version:
1.0.0

team:
  team_name: Hardware Engineering
  members_count: 3
  lead_architect: Systems Lead

architecture:
  subsystems: 4
  connections: 6
  specification_summary: Synchronous buck-boost power distribution network.

requirements:
  total: 6
  functional: 3
  technical: 3

components:
  total_mpns: 8
  primary_controller: STM32G474RET6

bom:
  total_line_items: 8
  estimated_cost_usd: 142.50
  currency: USD

research:
  indexed_papers: 4
  literature_summary: Empirical power conversion topologies and thermal profiles.

documents:
  datasheets: 4
  specs: Indexed in documents/files/

analysis:
  power: Computed nominal 36V battery input to 12V, 5V, 3.3V rails
  thermal: Max junction temperature 68.4°C at 25°C ambient
  pcb: 4-Layer High Density FR4 (1.6mm thickness)

tasks:
  total_milestones: 6
  active_tasks: 2

decisions:
  recorded_decisions: 2
  latest_adrs: decisions/index.wl

agents:
  configured_agents: 5
  governance: Scope-bounded cryptographically signed receipts

dependencies:
  hardware: KiCad 8.0+, Altium Designer 24
  firmware: Zephyr RTOS, ARM GCC

filesystem:
  root: .
  manifest: .wl/manifest.wl
  entry: README.wl
  data_modules: requirements/, architecture/, components/, bom/, research/, documents/, analysis/, decisions/, tasks/, team/, agents/, history/
```

### 3.2 `.wl/manifest.wl`
The `.wl/manifest.wl` file provides a machine-verifiable catalog with relative resource paths, line counts, and checksum hashes:

```yaml
WORKLINE_PROJECT_MANIFEST
==========================
schema_version: 1.0
export_version: 2026-09-21T21:42:00Z
generated_at: 2026-09-21T21:42:00Z
source_workline_version: 1.0.0

project:
  id: PROJ-AUTO
  name: Autonomous Delivery Drone Power Distribution
  version: 1.0
  domain: Hardware Systems & Power Engineering
  status: ACTIVE

resources:
  requirements:
    path: requirements/
    count: 4
  architecture:
    path: architecture/
    count: 5
  components:
    path: components/
    count: 8
  bom:
    path: bom/
    count: 3
  research:
    path: research/
    count: 4
  documents:
    path: documents/
    count: 2
  analysis:
    path: analysis/
    count: 4
  decisions:
    path: decisions/
    count: 2
  tasks:
    path: tasks/
    count: 6
  team:
    path: team/
    count: 3
  agents:
    path: agents/
    count: 5
  history:
    path: history/
    count: 12
  exports:
    path: exports/
    count: 1

total_files: 38
total_bytes: 58240
```

---

## 4. CLI Project Discovery Rules

The WORKLINE CLI (`wg`) discovers and inspects projects using deterministic lookups:

1. **Root Detection**:
   The CLI checks the specified folder for `README.wl`. If missing, it checks for `.wl/manifest.wl`. If neither is found, it reports that the path is not a valid WORKLINE project.
2. **Schema Verification**:
   The CLI reads `schema_version` from `.wl/manifest.wl`. If `schema_version == "1.0"`, standard parsing occurs.
3. **Resource Traversal**:
   The CLI uses the `resources:` block in `.wl/manifest.wl` to traverse subdirectories without hardcoding assumptions about directory layouts.
4. **Command Bindings**:
   - `wg open <path>`: Parses `README.wl` and outputs human-readable project status.
   - `wg inspect <path>`: Validates all resource checksums and schema invariants.
   - `wg bom <path>`: Reads `bom/bom.csv` and displays cost totals and supplier allocations.
   - `wg research <path>`: Lists all papers from `research/index.wl` and syntheses from `research/findings.wl`.
   - `wg export <path> --zip`: Bundles the current directory into `<project-name>.workline.zip`.

---

## 5. Strict Zero-Secrets Invariant

> [!CAUTION]
> **CRITICAL SECURITY REQUIREMENT:** Under NO circumstance may secret credentials, private keys, authentication cookies, or OAuth tokens be exported into the `.wl` filesystem.

### Rules:
1. **API Keys**: Any provider that requires keys (e.g. AWS, Clerk, GitHub) must have its credentials replaced with:
   ```yaml
   service: AWS
   configuration: configured
   credentials: NOT_EXPORTED
   ```
2. **Git Ignore**: Every exported `.wl` directory automatically includes `.gitignore` and `.worklineignore` excluding `.env`, `*.key`, `*.pem`, `private/`, and `cache/`.
3. **Cryptographic Receipts**: Agent receipts in `agents/receipts.wl` contain public HMAC signatures and hashes; private salt keys and seed material remain exclusively in server-side secret vaults.

---

## 6. Cloud Storage & Git Synchronization

The `.wl` filesystem format maps natively to cloud storage and version control targets:

| Provider | Target Path Convention | Synchronization Protocol |
| :--- | :--- | :--- |
| **Google Drive** | `WORKLINE/Projects/<project-name>/` | Folder tree mirror with manifest checksum validation |
| **GitHub** | `<account>/workline-<project-name>:main` | Git commit: `WORKLINE: sync project v{version}` |
| **GitLab** | `<namespace>/<project-name>:main` | Standard Git push/pull over HTTPS OAuth |
| **Bitbucket** | `<workspace>/<project-name>:main` | Standard Git push/pull over HTTPS OAuth |
| **Local ZIP** | `<project-name>.workline.zip` | Deflate-compressed single-file archive |

---

## 7. Restoration & Collision Strategies

When restoring a `.wl` package into an active WORKLINE workspace, users choose from three deterministic strategies:

1. **MERGE (Default / Recommended)**:
   - Merges newly added BOM components and requirements.
   - Updates modified fields where remote version is newer.
   - Preserves existing local activity logs and private annotations.
2. **CREATE NEW**:
   - Clones the project with an updated ID suffix (`<id>-COPY`) and name suffix (`(Restored)`).
   - Leaves the active project untouched.
3. **REPLACE**:
   - Completely overwrites the workspace state with the imported package after explicit user confirmation.

---

## 8. Versioning & Extensibility

- Current specification version: **`1.0`**
- Additional custom modules can be placed in top-level directories provided they are declared in `.wl/manifest.wl` under the `resources:` block.
- Backwards compatibility: Future schema versions (`1.1+`) must retain compatibility with `1.0` `README.wl` and `.wl/manifest.wl` parsing contracts.
