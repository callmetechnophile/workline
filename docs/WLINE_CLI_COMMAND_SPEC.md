# Workline CLI (wline) — Canonical Command Specification

**Version:** 1.0.0  
**Status:** SPECIFIED & ARCHITECTURALLY VERIFIED  
**Repository:** [github.com/callmetechnophile/workline](https://github.com/callmetechnophile/workline)

---

## 1. CLI Philosophy & Architectural Principles

The Workline CLI (`wline`) is the unified command-line interface for the Workline Engineering Lifecycle Platform. It provides hardware, embedded, and cyber-physical engineering teams with an automated, observable, and multi-agent workflow environment.

### Core Architectural Invariants:
1. **The CLI is a User Interface (Presentation Layer):**
   The CLI is strictly an interface client. It **never** acts as the agent runtime, orchestrator, database engine, job queue, background worker, authorization boundary, or LLM inference gateway.
2. **Canonical Public Executable Identity:**
   The single, authoritative command-line executable name is:
   ```bash
   wline
   ```
   Every public command begins with `wline`. No public commands or secondary binaries are permitted under names such as `armourflow`, `armourflow-cli`, or `workflowguide`. The `armourflow` package namespace is strictly preserved as an internal Python module compatibility layer to prevent breaking imports across the 27 domain agents.
3. **Control Fabric & Asynchronous Dispatch Boundary:**
   The CLI interacts exclusively with application services, FastAPI REST/GraphQL endpoints, or the `AgentControlFabric`. It **never** imports domain agent classes directly to execute domain tasks.
   ```text
   User
    ↓
   wline (CLI Parser & Presentation)
    ↓
   Workline Application Services / REST Gateway
    ↓
   Agent Control Fabric (armourflow.fabric.fabric)
    ↓
   Asynchronous Job Queue (backend.workline.jobs.queue.LocalJobQueue)
    ↓
   Job Worker Pipeline (default_job_worker with bounded exponential backoff)
    ↓
   Authoritative Domain Agents (1..27) / External Interoperability Gateway
   ```
4. **Decoupled Internal vs. External Agent Management:**
   - `wline agents ...` (plural): Manages Workline's 27 internal domain engineering agents registered in the Authoritative Agent Registry.
   - `wline agent ...` (singular): Manages external agent interoperability via A2A, Bindu, and Corsair protocols.
5. **Deterministic Output & Exit Codes:**
   Every command supports formatted human-readable ANSI output for interactive terminals and clean, schema-consistent JSON (`--json`) for automation pipelines and CI/CD.

---

## 2. Global Options

The following options are recognized across commands:

| Option | Flag | Description | Default |
|---|---|---|---|
| `--help` | `-h` | Display context-sensitive command help and argument syntax | `False` |
| `--version` | `-v` | Display CLI version, platform version, and Git commit hash | `False` |
| `--json` | | Output pure deterministic JSON without banners or ANSI codes | `False` |
| `--project` | `-p` | Specify target project identifier (overrides active project) | Active workspace project |
| `--config` | | Path to custom workspace configuration file | `~/.workline/config.json` |
| `--quiet` | `-q` | Suppress non-essential informational and decorative messages | `False` |
| `--verbose` | | Enable diagnostic debug logs and stack traces | `False` |

---

## 3. Exit Codes Schema

Every command returns a deterministic, machine-verifiable exit code:

| Exit Code | Identifier | Description |
|---|---|---|
| `0` | `SUCCESS` | Operation completed successfully |
| `1` | `GENERAL_ERROR` | Unhandled runtime exception or general internal failure |
| `2` | `INVALID_ARGUMENTS` | Missing argument, unknown flag, or malformed payload |
| `3` | `CONFIG_ERROR` | Missing configuration, invalid path, or uninitialized workspace |
| `4` | `AUTH_FAILURE` | Missing/invalid authentication token, expired session, or authorization denied |
| `5` | `SERVICE_UNAVAILABLE` | Backend gateway, SurrealDB, Qdrant, or Bedrock unreachable |
| `6` | `TASK_FAILURE` | Asynchronous task or worker job execution failed |
| `7` | `TIMEOUT` | Operation, remote RPC, or task execution deadline exceeded |
| `8` | `CANCELLATION` | Task or workflow cancelled by user or signal |
| `9` | `VALIDATION_FAILURE` | Contract check, DRC failure, or schema violation |
| `10`| `DEPENDENCY_MISSING` | Required system binary (e.g. `git`, `kicad`) missing from PATH |

---

## 4. Canonical Command Hierarchy Tree

```text
wline
├── --help
├── --version (-v)
├── init                          [Initialize workspace or project with Git & metadata]
│
├── system                        [Platform health, diagnostics, and runtime status]
│   ├── status                    # Overall platform status, registered agents, runtime layers
│   ├── health                    # Live component health probes (fabric, DB, models, security)
│   ├── version                   # CLI, protocol, and schema version details
│   ├── info                      # Detailed platform configuration and gateway endpoints
│   └── diagnostics               # 13-checkpoint configuration validator
│
├── auth                          [Secure cloud authentication]
│   ├── login                     # Authenticate with Workline Cloud / Clerk token
│   ├── logout                    # Terminate local authentication session
│   ├── whoami                    # Inspect active authentication identity and gateway
│   ├── status                    # Cloud connectivity and session status
│   └── token                     # Display active token hint (masked, never raw secrets)
│
├── config                        [Workspace configuration management]
│   ├── get <key>                 # Retrieve configuration value
│   ├── set <key> <value>         # Update configuration key
│   ├── list                      # List all configuration settings (alias: show)
│   └── path                      # Print configuration and workspace paths
│
├── project                       [Engineering project lifecycle management]
│   ├── create                    # Create new project manifest & directory structure
│   ├── list                      # List all projects in workspace
│   ├── open <name>               # Set active working project
│   ├── inspect [name]            # Detailed manifest inspection
│   ├── status [name]             # Lifecycle breakdown and current stage progress
│   ├── delete <name>             # Delete project from workspace
│   ├── export [file]             # Export project archive (.wlipjt)
│   ├── import <file>             # Import project archive (.wlipjt)
│   ├── inspect-package <file>    # Read-only inspect .wlipjt package
│   ├── verify <file>             # Verify cryptographic SHA-256 checksums
│   ├── info [target]             # Summary of project or .wlipjt package
│   ├── diff <pkgA> <pkgB>        # Compare two .wlipjt package archives
│   └── backup                    # Create timestamped package backup
│
├── agents                        [Internal 27-Agent Control Fabric Registry]
│   ├── list                      # List all 27 domain agents individually
│   ├── info <agent-id>           # Detailed manifest, capabilities, and dependencies
│   ├── capabilities [agent-id]   # Indexed platform capabilities
│   ├── health                    # Live readiness & import verification
│   └── status <agent-id>         # Runtime status & circuit-breaker state
│
├── agent                         [External Agent Interoperability (A2A / Bindu)]
│   ├── list                      # List registered external agents
│   ├── discover                  # Query external registry for remote agents
│   ├── info <agent-id>           # Inspect external agent trust score & protocol
│   ├── capabilities <agent-id>   # Query remote capability declarations
│   ├── register                  # Register remote agent endpoint
│   ├── unregister <agent-id>     # Remove remote agent registration
│   ├── task <agent-id> <cap>     # Submit subtask to external agent
│   ├── status <task-id>          # Check status of external agent task
│   └── cancel <task-id>          # Cancel active external agent task
│
├── task                          [Control Fabric Asynchronous Task Lifecycle]
│   ├── create                    # Submit and enqueue task to Job Queue (asynchronous)
│   ├── run                       # Submit and wait/stream task execution
│   ├── status <task-id>          # Inspect task lifecycle state, result, or error
│   ├── cancel <task-id>          # Cancel queued or running task
│   ├── retry <task-id>           # Re-enqueue failed task
│   ├── history                   # Project task audit trail (alias: list)
│   └── inspect <task-id>         # Deep inspection including provenance & attempts
│
├── workflow                      [Named Engineering Multi-Agent Workflows]
│   ├── list                      # Catalogue of built-in named workflows
│   ├── inspect <workflow>        # Inspect workflow DAG and capability bindings
│   ├── create <name>             # Register custom workflow definition
│   ├── validate <name>           # Validate capability and agent requirements
│   ├── run <name>                # Dispatch workflow via Control Fabric
│   ├── status <workflow-id>      # Track execution of workflow run
│   ├── cancel <workflow-id>      # Cancel running workflow
│   └── history                   # View historical workflow runs for project
│
├── artifact                      [Engineering Artifact Management]
│   ├── list                      # List generated project artifacts
│   ├── inspect <artifact-id>     # View artifact metadata, hashes, and provenance
│   ├── download <artifact-id>    # Export artifact file to local path
│   └── delete <artifact-id>      # Delete generated artifact
│
├── document                      [Document Intelligence & Technical Authoring]
│   ├── ingest <file>             # Ingest datasheet/spec (Docling + spaCy + Qdrant)
│   ├── list                      # List project documents
│   ├── inspect <document-id>     # View parsed sections and entities (alias: info)
│   ├── search <query>            # Semantic search across document nodes
│   ├── generate                  # Generate technical document via agent.27
│   ├── review <document-id>      # Review technical document via agent.27
│   └── delete <document-id>      # Delete document record
│
├── engineering                   [Specialist Domain Engineering Commands]
│   ├── simulation                # Run physics/thermal simulation via agent.19
│   ├── optimize                  # Multi-objective Pareto optimization via agent.20
│   ├── dfm                       # Design-for-manufacturability analysis via agent.24
│   ├── bom                       # BOM generation and landed cost via agent.08
│   ├── pcb                       # PCB layout and DRC validation via agent.23
│   └── verification              # Requirements compliance verification via agent.18
│
├── pcb                           [Deep PCB CAD & PINN Physics Operations]
│   ├── create                    # Initialize authoritative PCB project from BOM
│   ├── validate                  # Run DRC, clearance, and electrical rules check
│   ├── optimize                  # Thermal component placement optimization
│   ├── export                    # Export manufacturing Gerbers / IPC-2581
│   ├── inspect                   # Layer stackup and thermal parameters
│   └── pinn                      # Physics-Informed Neural Network commands
│       ├── train                 # Train neural thermal surrogate model
│       ├── validate              # Validate model accuracy against FEM solver
│       └── predict               # Ultra-fast thermal field inference
│
├── bom                           [Bill of Materials & Sourcing Optimization]
│   ├── generate                  # Synthesize BOM from project requirements
│   ├── status [bom-id]           # Inspect BOM item breakdown and costs
│   ├── approve [bom-id]          # Lock BOM for procurement
│   └── export [bom-id]           # Export CSV/JSON BOM
│
├── component                     [Hardware Component Sourcing & Validation]
│   ├── search <query>            # Multi-vendor search (DigiKey, Mouser, Robu)
│   ├── compare <id1> <id2>       # Side-by-side component comparison
│   └── validate <id> -r <req>    # Validate component against engineering constraint
│
├── procurement                   [Vendor Sourcing & Landed Cost Optimizer]
│   ├── search [query]            # Sourcing run across active project BOM
│   └── optimize                  # Analyze shipping, split-order, and cost tradeoffs
│
├── order                         [Hardware Procurement Orders & Fulfillment]
│   ├── create <bom-id>           # Generate Order Plan from approved BOM
│   ├── preview <order-id>        # Review line items, shipping, taxes
│   ├── approve <order-id>        # Authorize order for placement
│   ├── pay <order-id>            # Authorize payment session (x402 / gateway)
│   ├── status <order-id>         # Check vendor fulfillment and tracking
│   ├── list                      # List project procurement orders
│   └── cancel <order-id>         # Cancel pending vendor order
│
├── payment                       [Payment Session Inspection]
│   └── status <payment-id>       # View payment session status and settlement (read-only)
│
├── security                      [Cyber-Physical Security & Compliance]
│   ├── audit                     # Run ArmorIQ boundary and compliance audit
│   ├── scan                      # Targeted STRIDE/PASTA threat model via agent.22
│   ├── status                    # Inspect active policy scopes and boundaries
│   └── findings                  # View open security findings
│
├── knowledge                     [Engineering Knowledge Graph & Memory]
│   ├── search <query>            # Semantic search across ADRs, specs, and lessons
│   ├── summarize                 # Executive project knowledge summary
│   ├── export                    # Export knowledge base to JSON/Markdown
│   └── graph                     # Graph traversal and entity relations
│       ├── related <entity-id>   # 1-hop and 2-hop entity relations
│       ├── evidence <entity-id>  # Provenance and source documentation
│       └── traverse <entity-id>  # Deep relationship path traversal
│
├── decision                      [Architecture Decision Records (ADRs)]
│   ├── create                    # Record new engineering decision
│   ├── approve <decision-id>     # Approve proposed decision
│   ├── supersede <id> --by <id>  # Mark decision superseded by newer ADR
│   ├── list                      # List decisions for active project
│   └── info <decision-id>        # Inspect decision rationale and evidence
│
├── requirement                   [Engineering Requirements & Verification]
│   ├── create                    # Define formal engineering requirement
│   ├── list                      # List project requirements
│   ├── evaluate <req-id>         # Evaluate constraints against design state
│   └── status <req-id>           # Requirement validation status
│
├── finding                       [Engineering Findings & Validation Anomalies]
│   ├── create                    # Record anomaly or validation failure
│   ├── list                      # List open engineering findings
│   ├── resolve <finding-id>      # Mark finding resolved with explanation
│   └── info <finding-id>         # Inspect finding details
│
├── lesson                        [Engineering Lessons Learned]
│   ├── create                    # Record lesson learned with root cause
│   ├── list                      # List lessons learned for project
│   └── info <lesson-id>          # Inspect lesson recommendations
│
├── team                          [Collaboration & Access Control]
│   ├── list                      # List team members and assigned roles
│   └── invitation                # Cryptographic invite management
│       ├── create                # Generate AES-256-GCM invite URL
│       ├── list                  # List active invitation tokens
│       ├── revoke <token>        # Revoke invitation token
│       └── join <token>          # Accept invitation and join team
│
├── git                           [Project Local Version Control Utility]
│   ├── status                    # Working tree and commit status
│   ├── commit <msg>              # Stage and commit project changes
│   ├── log                       # View recent commits
│   ├── branch                    # List, create, or switch Git branches
│   ├── push                      # Push commits to remote origin
│   ├── pull                      # Pull commits from remote origin
│   └── tag                       # Tag release versions
│
├── github                        [GitHub Remote Repository Integration]
│   ├── auth                      # Configure GitHub Personal Access Token
│   ├── init <repo>               # Create remote GitHub repository
│   ├── connect <url>             # Link existing remote repository
│   ├── push                      # Push project to GitHub
│   └── status                    # Check GitHub synchronization
│
├── generate                      [Visual & Diagram Artifact Generation]
│   ├── image                     # Generate technical visual diagram (Bedrock/Titan)
│   ├── architecture              # Generate SVG architecture diagram
│   ├── deck                      # Generate technical presentation deck
│   ├── list                      # List generated visual assets
│   └── inspect <artifact-id>     # View visual artifact metadata
│
├── eval                          [Agent Evaluation & Benchmark Harness]
│   ├── run                       # Execute benchmark suite against agents
│   └── report                    # Generate agent evaluation scorecard
│
├── cache                         [Knowledge Cache Diagnostics (Admin)]
│   ├── stats                     # L1 memory and L2 disk cache metrics
│   ├── clean                     # Clear expired TTL records
│   ├── clear                     # Flush all cached knowledge
│   └── inspect <key>             # Inspect specific cache key
│
├── database                      [Data Layer Management (Admin)]
│   ├── status                    # SurrealDB and Qdrant health
│   ├── migrate                   # Migrate SQLite to SurrealDB graph
│   └── validate                  # Parity validation across data stores
│
├── sync                          [Project Cloud Synchronization]
└── doctor                        [Local Environment & Runtime Diagnostics]
```

---

## 5. Detailed Canonical Command Specifications

### 5.1 System (`wline system`)

#### `wline system status`
- **Purpose:** Inspect top-level platform runtime status, registered agents count, and configured service backends.
- **Inputs:** None
- **Options:** `--json`
- **Output:** Platform name, CLI version, registered agents count, Control Fabric status, State Layer status, Model Provider, API layers.
- **Exit Codes:** `0` (Success), `5` (Service Unavailable).
- **Backend:** `armourflow.fabric`, `armourflow.registry`, `armourflow.data.client`.
- **Authorization:** Public / Unauthenticated.
- **Execution:** Synchronous read.
- **Example:**
  ```bash
  $ wline system status --json
  {
    "platform": "WORKLINE",
    "cli_version": "1.0.0",
    "environment": "development",
    "registered_agents": 27,
    "control_fabric": "AgentControlFabric",
    "state_layer": "SurrealDB + Qdrant",
    "model_provider": "Amazon Bedrock (NVIDIA fallback)",
    "pending_tasks": 0
  }
  ```

#### `wline system health`
- **Purpose:** Probe real live connectivity and health across all core subsystems.
- **Inputs:** None
- **Options:** `--json`
- **Output:** Component health table (Control Fabric, State DB, Model Provider, ArmorIQ Boundary, Agent Registry).
- **Exit Codes:** `0` (All healthy/ready), `5` (Critical service degraded).
- **Backend:** `fabric.health_check()`, `surreal_db.is_connected()`, `models.health_check()`.
- **Authorization:** Public.
- **Execution:** Synchronous read.

#### `wline system diagnostics`
- **Purpose:** Run deep 13-checkpoint configuration and connectivity validation suite.
- **Inputs:** None
- **Options:** `--json`
- **Output:** Granular report of 13 configuration points (`SurrealDBConfig`, `QdrantConfig`, `BedrockConfig`, `NvidiaConfig`, `TavilyConfig`, etc.).
- **Exit Codes:** `0` (All configured), `3` (Missing critical configuration).
- **Backend:** `armourflow.config.validation.ConfigurationValidator`.
- **Authorization:** Public.
- **Execution:** Synchronous read.

---

### 5.2 Task Lifecycle (`wline task`)

#### `wline task create`
- **Purpose:** Enqueue a task to the asynchronous Job Queue via the Control Fabric with durable idempotency.
- **Inputs:** None (target defined via flags)
- **Options:**
  - `--agent`, `-a`: Target agent identifier (e.g. `agent.19`, `19`, `EngineeringSimulationAgent`)
  - `--capability`, `-c`: Target capability name (e.g. `simulation.digital_twin`)
  - `--project`, `-p`: Project identifier
  - `--payload`: JSON string or `@filepath` containing task arguments
  - `--idempotency-key`: Durable idempotency deduplication key
  - `--json`: Output result as pure JSON
- **Output:** Task ID, status (`QUEUED` / `RUNNING`), timestamp.
- **Exit Codes:** `0` (Created/Queued), `2` (Invalid payload/args), `4` (Authorization denied), `5` (Queue offline).
- **Backend:** `AgentControlFabric.submit_task(sync_wait=False)` -> `LocalJobQueue.enqueue()`.
- **Authorization:** Authenticated user with Project `MEMBER` or `ENGINEER` role.
- **Execution:** Asynchronous.
- **Example:**
  ```bash
  $ wline task create --agent agent.19 --payload '{"scenario":"thermal_stress","ambient_c":45.0}' --json
  {
    "task_id": "task_01J8F9...",
    "state": "QUEUED",
    "target_agent_id": "agent.19",
    "project_id": "mars-rover-v2",
    "created_at": "2026-09-18T00:15:00Z"
  }
  ```

#### `wline task status <task-id>`
- **Purpose:** Retrieve the live state, progress, and result of an enqueued or completed task.
- **Inputs:** `<task-id>` (String, required)
- **Options:**
  - `--watch`, `-w`: Stream/poll status changes until task reaches terminal state
  - `--json`: Output as pure JSON
- **Output:** Current state (`QUEUED`, `RUNNING`, `WAITING_FOR_USER`, `COMPLETED`, `FAILED`, `CANCELLED`), error message or result payload.
- **Exit Codes:** `0` (Terminal COMPLETED), `2` (Task ID not found), `6` (Task FAILED), `8` (Task CANCELLED).
- **Backend:** `AgentControlFabric.get_task(task_id)` / SQLite idempotency store.
- **Authorization:** Project member.
- **Execution:** Synchronous read (or polling loop with `--watch`).

#### `wline task cancel <task-id>`
- **Purpose:** Request immediate cancellation of a queued or running task.
- **Inputs:** `<task-id>` (String, required)
- **Options:** `--json`
- **Output:** Cancellation confirmation and final status.
- **Exit Codes:** `0` (Cancelled), `2` (Not found), `6` (Cannot cancel terminal task).
- **Backend:** `AgentControlFabric.cancel_task(task_id)`.
- **Authorization:** Task creator or Project `ADMIN`.
- **Execution:** Synchronous command.

---

### 5.3 Internal Agents (`wline agents`)

#### `wline agents list`
- **Purpose:** Authoritative enumeration of all 27 internal domain engineering agents.
- **Inputs:** None
- **Options:** `--json`
- **Output:** Individual table listing ID (`#01`..`#27`), Name, Status (`READY`/`DEGRADED`), Execution Level, and top capabilities. **Never collapses or aggregates agents.**
- **Exit Codes:** `0` (Success).
- **Backend:** `armourflow.registry.registry.AuthoritativeAgentRegistry.list_agents()`.
- **Authorization:** Public / All users.
- **Execution:** Synchronous read.

#### `wline agents info <agent-id>`
- **Purpose:** Show comprehensive manifest metadata for an internal agent.
- **Inputs:** `<agent-id>` (Accepts `1`, `01`, `#14`, `agent.14`, `Agent #14`, or name)
- **Options:** `--json`
- **Output:** ID, legacy alias, name, version, status, execution level, entrypoint, description, dependencies, permissions, and all declared capabilities.
- **Exit Codes:** `0` (Found), `2` (Invalid agent ID; valid range 1–27).
- **Backend:** `AuthoritativeAgentRegistry.get_agent()`.
- **Authorization:** Public.
- **Execution:** Synchronous read.

#### `wline agents health`
- **Purpose:** Live import and readiness check for all 27 internal agents.
- **Inputs:** None
- **Options:** `--json`
- **Output:** Readiness report showing import verification, missing dependencies, or syntax errors per agent.
- **Exit Codes:** `0` (All 27 ready), `1` (One or more degraded).
- **Backend:** `AuthoritativeAgentRegistry.check_health()`.
- **Authorization:** Public.
- **Execution:** Synchronous read.

---

### 5.4 External Agent Interoperability (`wline agent`)

#### `wline agent list`
- **Purpose:** List registered remote external agents (Bindu, Corsair, A2A).
- **Inputs:** None
- **Options:** `--protocol`, `-p` (Filter by `BINDU_A2A` or `CORSAIR`), `--json`
- **Output:** Agent ID, protocol, status, version, trust score, capability count.
- **Exit Codes:** `0` (Success).
- **Backend:** `backend.workline.interoperability.registry.agent_registry.list_agents()`.
- **Authorization:** Authenticated user.
- **Execution:** Synchronous read.

#### `wline agent task <agent-id> <capability>`
- **Purpose:** Delegate an engineering subtask to a remote external agent.
- **Inputs:** `<agent-id>`, `<capability>`
- **Options:** `--team`, `-t`, `--yes`, `-y` (Bypass interactive confirmation), `--json`
- **Output:** External task ID, status, provenance duration, output hash, risk assessment.
- **Exit Codes:** `0` (Completed), `2` (Unknown external agent or capability), `4` (Authorization / policy rejected).
- **Backend:** `backend.workline.interoperability.gateway.interoperability_gateway.submit_task()`.
- **Authorization:** Authenticated user with explicit human-in-the-loop confirmation (or `--yes`).
- **Execution:** Asynchronous dispatch with synchronous completion wait.

---

### 5.5 Workflow Lifecycle (`wline workflow`)

#### `wline workflow list`
- **Purpose:** List catalogue of available named engineering workflows.
- **Inputs:** None
- **Options:** `--json`
- **Output:** Workflow name, primary capability, target agent, description, steps.
- **Exit Codes:** `0` (Success).
- **Backend:** In-memory workflow catalogue (`simulation-study`, `design-for-manufacturability`, `optimization-loop`, `threat-model`, `tech-documentation`, `evidence-synthesis`, `compliance-audit`).
- **Authorization:** Public.
- **Execution:** Synchronous read.

#### `wline workflow run <name>`
- **Purpose:** Dispatch a named multi-agent workflow sequence through the Control Fabric.
- **Inputs:** `<name>` (Workflow identifier, required)
- **Options:** `--project`, `-p`, `--payload`, `--json`
- **Output:** Generated workflow task ID, lifecycle state, intermediate outputs, and consolidated result panel.
- **Exit Codes:** `0` (Success), `2` (Unknown workflow name), `5` (Fabric failure), `6` (Execution failure).
- **Backend:** `AgentControlFabric.submit_task(target_capability=wf.capability)`.
- **Authorization:** Project member.
- **Execution:** Asynchronous enqueue with optional wait.

---

### 5.6 Document Intelligence (`wline document`)

#### `wline document ingest <file-path>`
- **Purpose:** Ingest component datasheet or specification document through Docling structural parsing, spaCy entity enrichment, LlamaIndex node creation, Qdrant vector indexing, and SurrealDB provenance recording.
- **Inputs:** `<file-path>` (Path to PDF, MD, or TXT document, required)
- **Options:** `--project`, `-p`, `--id`, `--json`
- **Output:** Document ID, sections extracted, entities discovered, indexing status.
- **Exit Codes:** `0` (Success), `2` (File not found), `9` (Parsing error).
- **Backend:** `backend.workline.documents.service.document_service.ingest_document()`.
- **Authorization:** Project member.
- **Execution:** Synchronous parsing pipeline.

#### `wline document generate`
- **Purpose:** Generate formal technical documentation (reports, SOPs, design specs) via `agent.27` (`TechDocAgent`).
- **Inputs:** None
- **Options:** `--title`, `-t`, `--type` (`technical_report`, `sop`, `design_spec`), `--project`, `-p`, `--payload`, `--json`
- **Output:** Generated document ID, status (`DRAFT`/`PUBLISHED`), document markdown.
- **Exit Codes:** `0` (Success), `6` (Agent execution failure).
- **Backend:** `AgentControlFabric.submit_task(target_agent_id="agent.27", target_capability="create_document")`.
- **Authorization:** Project member.
- **Execution:** Asynchronous Control Fabric task.

---

### 5.7 Engineering Domain Operations

#### `wline engineering simulation`
- **Purpose:** Run digital twin or thermal/mechanical simulation study via `agent.19` (`EngineeringSimulationAgent`).
- **Options:** `--component`, `-c`, `--scenario`, `-s` (`static_load`, `thermal`, `fatigue`), `--project`, `-p`, `--payload`, `--json`
- **Backend:** Fabric -> `agent.19`.

#### `wline engineering optimize`
- **Purpose:** Run multi-objective Pareto design optimization loop via `agent.20` (`EngineeringOptimizationAgent`).
- **Options:** `--design`, `-d`, `--objectives`, `-o` (e.g. `weight,cost,efficiency`), `--project`, `-p`, `--payload`, `--json`
- **Backend:** Fabric -> `agent.20`.

#### `wline engineering dfm`
- **Purpose:** Perform Design-for-Manufacturability (DFM) and assembly (DFA) inspection via `agent.24` (`ManufacturingDFMAgent`).
- **Options:** `--component`, `-c`, `--process`, `--project`, `-p`, `--payload`, `--json`
- **Backend:** Fabric -> `agent.24`.

---

### 5.8 PCB Engineering & Physics-Informed Neural Networks (`wline pcb`)

#### `wline pcb create`
- **Purpose:** Build authoritative PCB project from BOM with layer stackup, footprints, and thermal model.
- **Options:** `--project`, `-p`, `--width`, `-w`, `--height`, `-h`, `--json`
- **Backend:** `backend.workline.pcb.services.pcb_service.create_pcb_project()`.

#### `wline pcb validate`
- **Purpose:** Run Design Rule Check (DRC), trace clearances, netlist connectivity, and thermal power limits.
- **Options:** `--project`, `-p`, `--json`
- **Backend:** `pcb_validation_service.validate_pcb_design()`.

#### `wline pcb pinn train`
- **Purpose:** Train Physics-Informed Neural Network (PINN) surrogate model on 2D steady-state heat conduction equation.
- **Options:** `--project`, `-p`, `--epochs`, `-e`, `--json`
- **Backend:** `backend.workline.pcb.services.physics_service.train_surrogate()`.

#### `wline pcb pinn predict <x> <y> <power>`
- **Purpose:** Real-time inferential thermal prediction at coordinate $(x, y)$ in milliseconds.
- **Backend:** `physics_service.predict_temperature()`.

---

### 5.9 Bill of Materials & Procurement (`wline bom`, `wline procurement`, `wline order`)

#### `wline bom generate`
- **Purpose:** Synthesize optimized Bill of Materials from project requirements using `procurement_engine`.
- **Backend:** `backend.workline.procurement.engine.procurement_engine.generate_project_bom()`.

#### `wline order create <bom-id>`
- **Purpose:** Generate itemized Order Plan and split-vendor draft orders from an approved BOM.
- **Backend:** `backend.workline.orders.service.order_service.create_order_plan()`.

#### `wline order approve <order-id>`
- **Purpose:** Formally authorize draft order for placement.
- **Backend:** `order_service.approve_order()`.

#### `wline order pay <order-id>`
- **Purpose:** Authorize settlement session through x402 agent payment gateway.
- **Security Constraint:** Raw private keys and wallet seeds are **never exposed**; session returns cryptographic receipt token.

---

### 5.10 Security & Threat Modeling (`wline security`)

#### `wline security audit`
- **Purpose:** Execute full platform compliance and ArmorIQ policy boundary health audit.
- **Backend:** `armourflow.security.armoriq.get_security_boundary()` + `agent.22`.

#### `wline security scan`
- **Purpose:** Run targeted STRIDE or PASTA cyber-physical threat scan against component or agent target.
- **Options:** `--target`, `-t`, `--model`, `-m` (`STRIDE`, `PASTA`, `DREAD`), `--project`, `-p`
- **Backend:** Fabric -> `agent.22` (`SecurityThreatModelingAgent`).

---

### 5.11 Environment Diagnostics (`wline doctor`)

#### `wline doctor`
- **Purpose:** Comprehensive local environment verification.
- **Checks:**
  1. CLI version and installation integrity
  2. Python runtime version ($\ge 3.9$)
  3. Git executable on system PATH
  4. Local configuration file (`config.json`)
  5. Active project workspace context
  6. R1 Gateway connectivity (`http://localhost:10000`)
- **Exit Codes:** `0` (All pass), `1` (One or more critical failures).

---

## 6. Complete Inventory & Classification of All Existing Commands

| Current Command | Implementation File | Backend Service / Layer | Status | Action / Replacement |
|---|---|---|---|---|
| `wline init` | `commands/init.py` | `project_repo_manager`, `workspace` | **ACTIVE** | Keep as canonical root command |
| `wline system status` | `commands/system.py` | `fabric`, `registry`, `db_client` | **ACTIVE** | Canonical platform status |
| `wline system health` | `commands/system.py` | `fabric`, `surreal_db`, `models` | **ACTIVE** | Canonical platform health |
| `wline system version` | `commands/system.py` | `cli.wline.__version__` | **ACTIVE** | Canonical version info |
| `wline system diagnostics`| `commands/system.py` | `ConfigurationValidator` (13 checks) | **ACTIVE** | Canonical diagnostics suite |
| `wline auth login` | `commands/auth.py` | `workspace_config` | **ACTIVE** | Needs credential persistence hardening |
| `wline auth logout` | `commands/auth.py` | `workspace_config` | **ACTIVE** | Keep |
| `wline auth whoami` | `commands/auth.py` | `workspace_config` | **ACTIVE** | Keep |
| `wline config show` | `commands/config.py` | `workspace_config` | **ACTIVE** | Alias to `wline config list` |
| `wline config set` | `commands/config.py` | `update_workspace_config` | **ACTIVE** | Expand to safe keys |
| `wline project list` | `commands/project.py` | `list_projects` | **ACTIVE** | Keep |
| `wline project create` | `commands/project.py` | `create_project` | **ACTIVE** | Keep |
| `wline project open` | `commands/project.py` | `set_active_project_name` | **ACTIVE** | Keep |
| `wline project inspect` | `commands/project.py` | `find_project` | **ACTIVE** | Keep |
| `wline project status` | `commands/project.py` | `render_lifecycle_status` | **ACTIVE** | Canonical project status |
| `wline project delete` | `commands/project.py` | `delete_project_dir` | **ACTIVE** | Keep |
| `wline project export` | `commands/project.py` | `export_service` | **ACTIVE** | Canonical package export |
| `wline project import` | `commands/project.py` | `import_service` | **ACTIVE** | Canonical package import |
| `wline project diff` | `commands/project.py` | `PackageInspector.diff` | **ACTIVE** | Keep |
| `wline project backup` | `commands/project.py` | `backup_service` | **ACTIVE** | Keep |
| `wline agents list` | `commands/agents.py` | `AuthoritativeAgentRegistry` | **ACTIVE** | Canonical internal agent list |
| `wline agents info` | `commands/agents.py` | `AuthoritativeAgentRegistry` | **ACTIVE** | Canonical internal agent info |
| `wline agents capabilities`| `commands/agents.py` | `AuthoritativeAgentRegistry` | **ACTIVE** | Canonical capability query |
| `wline agents health` | `commands/agents.py` | `AuthoritativeAgentRegistry` | **ACTIVE** | Canonical live health |
| `wline agent list` | `commands/agent.py` | `interoperability.agent_registry` | **ACTIVE** | Canonical external agent list |
| `wline agent discover` | `commands/agent.py` | `interoperability.agent_registry` | **ACTIVE** | Canonical discovery |
| `wline agent info` | `commands/agent.py` | `interoperability.agent_registry` | **ACTIVE** | Canonical external agent info |
| `wline agent capabilities` | `commands/agent.py` | `interoperability.agent_registry` | **ACTIVE** | Canonical external capabilities |
| `wline agent register` | `commands/agent.py` | `interoperability.agent_registry` | **ACTIVE** | Canonical registration |
| `wline agent unregister` | `commands/agent.py` | `interoperability.agent_registry` | **ACTIVE** | Canonical unregistration |
| `wline agent task` | `commands/agent.py` | `interoperability_gateway` | **ACTIVE** | Canonical external delegation |
| `wline agent cancel` | `commands/agent.py` | `interoperability_gateway` | **ACTIVE** | Canonical external cancel |
| `wline agent status` | `commands/agent.py` | `interoperability_gateway` | **ACTIVE** | External task status check |
| `wline agent run` | `commands/agent.py` | Legacy `agent_runtime` | **LEGACY** | Deprecate in favor of `wline task run` |
| `wline agent approve` | `commands/agent.py` | Legacy `agent_runtime` | **LEGACY** | Deprecate in favor of `wline decision approve` |
| `wline agent history` | `commands/agent.py` | Legacy `agent_runtime` | **LEGACY** | Deprecate in favor of `wline task history` |
| `wline task create` | `commands/task.py` | `AgentControlFabric` + `JobQueue` | **ACTIVE** | Canonical async task submission |
| `wline task run` | `commands/task.py` | `AgentControlFabric` | **ACTIVE** | Canonical sync task run |
| `wline task status` | `commands/task.py` | `AgentControlFabric` | **ACTIVE** | Canonical task status |
| `wline task cancel` | `commands/task.py` | `AgentControlFabric` | **ACTIVE** | Canonical task cancel |
| `wline task history` | `commands/task.py` | `AgentControlFabric` | **ACTIVE** | Canonical task audit history |
| `wline workflow list` | `commands/workflow.py` | Workflow catalogue | **ACTIVE** | Canonical workflow list |
| `wline workflow create` | `commands/workflow.py`| Workflow catalogue | **ACTIVE** | Canonical workflow registration |
| `wline workflow validate` | `commands/workflow.py`| `AgentRegistry` | **ACTIVE** | Canonical workflow check |
| `wline workflow run` | `commands/workflow.py` | `AgentControlFabric` | **ACTIVE** | Canonical workflow dispatch |
| `wline workflow status` | `commands/workflow.py` | `AgentControlFabric` | **ACTIVE** | Canonical workflow status |
| `wline workflow history` | `commands/workflow.py` | `AgentControlFabric` | **ACTIVE** | Canonical workflow history |
| `wline document ingest` | `commands/document.py` | `document_service` | **ACTIVE** | Canonical document ingestion |
| `wline document list` | `commands/document.py` | `document_service` | **ACTIVE** | Canonical document list |
| `wline document info` | `commands/document.py` | `document_service` | **ACTIVE** | Canonical document inspect |
| `wline document search` | `commands/document.py` | `document_service` | **ACTIVE** | Canonical semantic document search |
| `wline document delete` | `commands/document.py` | `document_service` | **ACTIVE** | Canonical document delete |
| `wline documents generate`| `commands/documents.py`| Fabric -> `agent.27` | **ACTIVE** | Merge under `wline document generate` |
| `wline documents list` | `commands/documents.py`| SurrealDB `document` table | **DEPRECATED**| Use `wline document list` |
| `wline documents review` | `commands/documents.py`| Fabric -> `agent.27` | **ACTIVE** | Merge under `wline document review` |
| `wline engineering simulation`| `commands/engineering.py`| Fabric -> `agent.19` | **ACTIVE** | Canonical simulation study |
| `wline engineering optimize` | `commands/engineering.py`| Fabric -> `agent.20` | **ACTIVE** | Canonical Pareto optimization |
| `wline engineering dfm` | `commands/engineering.py`| Fabric -> `agent.24` | **ACTIVE** | Canonical DFM analysis |
| `wline pcb create` | `commands/pcb.py` | `pcb_service` | **ACTIVE** | Canonical PCB create |
| `wline pcb validate` | `commands/pcb.py` | `pcb_validation_service` | **ACTIVE** | Canonical PCB DRC |
| `wline pcb optimize` | `commands/pcb.py` | `pcb_optimization_service` | **ACTIVE** | Canonical PCB optimization |
| `wline pcb export` | `commands/pcb.py` | `pcb_service` | **ACTIVE** | Canonical PCB export |
| `wline pcb pinn train` | `commands/pcb.py` | `physics_service` | **ACTIVE** | Canonical PINN training |
| `wline pcb pinn predict` | `commands/pcb.py` | `physics_service` | **ACTIVE** | Canonical PINN inference |
| `wline bom generate` | `commands/bom.py` | `procurement_engine` | **ACTIVE** | Canonical BOM generate |
| `wline bom status` | `commands/bom.py` | `procurement_engine` | **ACTIVE** | Canonical BOM status |
| `wline bom approve` | `commands/bom.py` | `procurement_engine` | **ACTIVE** | Canonical BOM lock |
| `wline bom export` | `commands/bom.py` | `procurement_engine` | **ACTIVE** | Canonical BOM export |
| `wline component search` | `commands/component.py`| `procurement_engine.search` | **ACTIVE** | Canonical component search |
| `wline component compare`| `commands/component.py`| `procurement_engine` | **ACTIVE** | Canonical component compare |
| `wline component validate`| `commands/component_validation.py`| `validation_service` | **ACTIVE** | Merge into `wline component validate` |
| `wline procurement search`| `commands/procurement.py`| `procurement_engine` | **ACTIVE** | Canonical procurement search |
| `wline procurement optimize`| `commands/procurement.py`| `procurement_engine` | **ACTIVE** | Canonical procurement optimize |
| `wline order create` | `commands/order.py` | `order_service` | **ACTIVE** | Canonical order plan |
| `wline order preview` | `commands/order.py` | `order_service` | **ACTIVE** | Canonical financial preview |
| `wline order approve` | `commands/order.py` | `order_service` | **ACTIVE** | Canonical order authorization |
| `wline order pay` | `commands/order.py` | `order_service` / x402 | **ACTIVE** | Canonical settlement |
| `wline order status` | `commands/order.py` | `order_service` | **ACTIVE** | Canonical order status |
| `wline order list` | `commands/order.py` | `order_service` | **ACTIVE** | Canonical order list |
| `wline order cancel` | `commands/order.py` | `order_service` | **ACTIVE** | Canonical order cancel |
| `wline payment status` | `commands/payment.py` | `order_service.session_manager` | **ACTIVE** | Canonical payment check (read-only) |
| `wline security audit` | `commands/security.py` | ArmorIQ + `agent.22` | **ACTIVE** | Canonical compliance audit |
| `wline security scan` | `commands/security.py` | Fabric -> `agent.22` | **ACTIVE** | Canonical STRIDE/PASTA scan |
| `wline knowledge search`| `commands/knowledge.py`| `knowledge_service` | **ACTIVE** | Canonical knowledge semantic search |
| `wline knowledge summarize`| `commands/knowledge.py`| `knowledge_summarizer` | **ACTIVE** | Canonical knowledge summary |
| `wline knowledge export`| `commands/knowledge.py`| `knowledge_service` | **ACTIVE** | Canonical knowledge export |
| `wline knowledge decisions`| `commands/knowledge.py`| `knowledge_service` | **DEPRECATED**| Use `wline decision list` |
| `wline knowledge requirements`| `commands/knowledge.py`| `validation_service` | **DEPRECATED**| Use `wline requirement list` |
| `wline knowledge findings`| `commands/knowledge.py`| `knowledge_service` | **DEPRECATED**| Use `wline finding list` |
| `wline knowledge lessons`| `commands/knowledge.py`| `knowledge_service` | **DEPRECATED**| Use `wline lesson list` |
| `wline decision create` | `commands/decision.py` | `knowledge_service` | **ACTIVE** | Canonical ADR create |
| `wline decision approve` | `commands/decision.py` | `knowledge_service` | **ACTIVE** | Canonical ADR approve |
| `wline decision supersede`| `commands/decision.py` | `knowledge_service` | **ACTIVE** | Canonical ADR supersede |
| `wline decision list` | `commands/decision.py` | `knowledge_service` | **ACTIVE** | Canonical ADR list |
| `wline decision info` | `commands/decision.py` | `knowledge_service` | **ACTIVE** | Canonical ADR info |
| `wline requirement create`| `commands/requirement.py`| `validation_service` | **ACTIVE** | Canonical requirement create |
| `wline requirement list` | `commands/requirement.py`| `validation_service` | **ACTIVE** | Canonical requirement list |
| `wline requirement evaluate`| `commands/requirement.py`| `validation_service` | **ACTIVE** | Canonical constraint check |
| `wline requirement status`| `commands/requirement.py`| `validation_service` | **ACTIVE** | Canonical requirement status |
| `wline finding create` | `commands/finding.py` | `knowledge_service` | **ACTIVE** | Canonical finding create |
| `wline finding list` | `commands/finding.py` | `knowledge_service` | **ACTIVE** | Canonical finding list |
| `wline finding resolve` | `commands/finding.py` | `knowledge_service` | **ACTIVE** | Canonical finding resolve |
| `wline finding info` | `commands/finding.py` | `knowledge_service` | **ACTIVE** | Canonical finding info |
| `wline lesson create` | `commands/lesson.py` | `knowledge_service` | **ACTIVE** | Canonical lesson create |
| `wline lesson list` | `commands/lesson.py` | `knowledge_service` | **ACTIVE** | Canonical lesson list |
| `wline lesson info` | `commands/lesson.py` | `knowledge_service` | **ACTIVE** | Canonical lesson info |
| `wline entity find` | `commands/entity.py` | `knowledge_graph_service` | **ACTIVE** | Canonical entity search |
| `wline entity inspect` | `commands/entity.py` | `knowledge_graph_service` | **ACTIVE** | Canonical entity inspect |
| `wline entity resolve` | `commands/entity.py` | `EntityResolver` | **INTERNAL** | Developer entity testing tool |
| `wline entity conflicts`| `commands/entity.py` | `knowledge_graph_service` | **ACTIVE** | Canonical conflict audit |
| `wline graph related` | `commands/graph.py` | `knowledge_graph_service` | **ACTIVE** | Canonical graph relations |
| `wline graph evidence` | `commands/graph.py` | `knowledge_graph_service` | **ACTIVE** | Canonical evidence provenance |
| `wline graph traverse` | `commands/graph.py` | `knowledge_graph_service` | **ACTIVE** | Canonical multi-depth traversal |
| `wline graph query` | `commands/graph.py` | Raw SurrealQL execution | **INTERNAL** | Developer/Admin only; reject raw access |
| `wline team list` | `commands/team.py` | `invitation_service` | **ACTIVE** | Canonical team list |
| `wline team invitation create`| `commands/team.py` | `invitation_service` | **ACTIVE** | Canonical encrypted invite |
| `wline git status` | `commands/git.py` | `git_service` | **ACTIVE** | Local VCS utility |
| `wline git commit` | `commands/git.py` | `git_service` | **ACTIVE** | Local VCS utility |
| `wline git log` | `commands/git.py` | `git_service` | **ACTIVE** | Local VCS utility |
| `wline git branch` | `commands/git.py` | `git_service` | **ACTIVE** | Local VCS utility |
| `wline git push` | `commands/git.py` | `git_service` | **ACTIVE** | Local VCS utility |
| `wline git pull` | `commands/git.py` | `git_service` | **ACTIVE** | Local VCS utility |
| `wline github auth` | `commands/github.py` | GitHub Token storage | **ACTIVE** | Remote integration utility |
| `wline github init` | `commands/github.py` | GitHub API | **ACTIVE** | Remote integration utility |
| `wline github push` | `commands/github.py` | Git remote push | **ACTIVE** | Remote integration utility |
| `wline generate image` | `commands/generate.py` | `generation_service` (Bedrock Titan) | **ACTIVE** | Canonical diagram generator |
| `wline generate architecture`| `commands/generate.py`| `generation_service` (SVG) | **ACTIVE** | Canonical architecture visual |
| `wline generate deck` | `commands/generate.py` | `generation_service` (Gamma outline) | **ACTIVE** | Canonical deck generator |
| `wline eval run` | `commands/eval.py` | `UniversalEvaluationHarness` | **ACTIVE** | Benchmark harness (Admin) |
| `wline eval report` | `commands/eval.py` | `UniversalEvaluationHarness` | **ACTIVE** | Evaluation scorecard (Admin) |
| `wline cache stats` | `commands/cache.py` | `knowledge_cache` | **ACTIVE** | Cache telemetry (Admin) |
| `wline cache clean` | `commands/cache.py` | `knowledge_cache` | **ACTIVE** | Cache maintenance (Admin) |
| `wline database status`| `commands/database.py`| `surreal_db`, `qdrant_manager` | **ACTIVE** | DB telemetry (Admin) |
| `wline database migrate`| `commands/database.py`| Migration scripts | **ACTIVE** | DB migration tool (Admin) |
| `wline doctor` | `commands/doctor.py` | Subprocess & PATH checks | **ACTIVE** | Canonical environment diagnostics |
| `wline sync` | `commands/sync.py` | Workspace sync check | **ACTIVE** | Cloud workspace synchronizer |
| `wline version` | `commands/version.py` | `project_repo_manager` | **ACTIVE** | Root version command |
| `wline snapshot` | `commands/version.py` | `project_repo_manager` | **ACTIVE** | Deterministic state snapshot |
| `wline release` | `commands/version.py` | `project_repo_manager` | **ACTIVE** | Tag release & bump version |
| `wline status` | `commands/status.py` | Alias to `project status` | **DEPRECATED**| Use `wline project status` |
| `wline login` | `commands/auth.py` | Root alias to `auth login` | **ACTIVE** | Root convenience shortcut |
| `wline logout` | `commands/auth.py` | Root alias to `auth logout`| **ACTIVE** | Root convenience shortcut |
| `wline whoami` | `commands/auth.py` | Root alias to `auth whoami`| **ACTIVE** | Root convenience shortcut |
