# Workline

Workline is an engineering lifecycle orchestration platform for taking projects from requirements to release.

---

## CLI

Workline provides a first-class command-line interface (`wline`) to initialize local engineering workspaces, create structured projects, track engineering lifecycle progress, and configure development settings.

### Installation

Install Workline locally in editable development mode:

```bash
pip install -e .
```

Verify installation:

```bash
wline --help
wline version
```

### Usage

```bash
wline <command>
```

### Available Commands

| Command | Description |
| :--- | :--- |
| `wline` | Displays the Workline header banner and available command catalog. |
| `wline init` | Initializes the default local Workline workspace (`~/Workline`). Safe to run multiple times. |
| `wline project create` | Interactive walkthrough to create a new project with directory hierarchy and manifest. |
| `wline project list` | Discovers and renders all valid Workline projects in the workspace. |
| `wline project open <name>` | Sets the specified project as the active project. |
| `wline project status [name]` | Displays the 36-stage engineering lifecycle status and completion percentage. |
| `wline project delete <name>` | Safely deletes a project directory from the workspace with confirmation. |
| `wline component search "<query>"` | Search components across DigiKey, Mouser, Robu, and Robocraze catalogs. |
| `wline component compare <id1> <id2>` | Side-by-side component specification and deterministic compatibility comparison. |
| `wline procurement search [query]` | Execute multi-vendor component acquisition for project requirements. |
| `wline procurement optimize` | Multi-vendor optimizer comparing landed costs, freight, and vendor consolidation. |
| `wline bom generate` | Generates engineering Bill of Materials with landed cost optimization. |
| `wline bom status [id]` | Displays Bill of Materials line items, freight confidence, and status. |
| `wline bom approve [id]` | Human approval action transitioning BOM from `READY_FOR_REVIEW` to `APPROVED`. |
| `wline agent run <name>` | Executes an ADK engineering agent tree with real-time streaming output. |
| `wline config show` | Displays active workspace path, config file, and current active project. |
| `wline config set workspace <path>` | Configures a custom workspace root location. |
| `wline database health` | Checks SurrealDB and Qdrant database connection health. |
| `wline version` | Displays the installed Workline CLI version. |

---

## Workspace

By default, Workline organizes all engineering projects under a dedicated local directory:

```
~/Workline/
```

When you run `wline init`, Workline ensures this directory exists. If it already exists, your existing data is preserved untouched.

User configuration and the currently active project pointer are stored under:

```
~/.workline/
├── config.yaml
└── active_project
```

---

## Project Structure

Every project created with `wline project create` contains a validated `workline.yaml` manifest and a complete lifecycle directory tree:

```
~/Workline/<project-name>/
│
├── workline.yaml
│
├── requirements/
├── problem/
├── architecture/
├── subsystems/
├── hardware/
├── datasheets/
├── power/
├── interfaces/
├── schematic/
├── bom/
├── pcb/
├── firmware/
├── tests/
├── validation/
├── telemetry/
├── backend/
├── data/
├── ml/
├── documentation/
└── release/
```

### Manifest Schema (`workline.yaml`)

```yaml
name: autonomous-rover
display_name: Autonomous Rover
description: Autonomous agricultural rover
version: 0.1.0
domain: robotics
budget:
  amount: 20000.0
  currency: INR
timeline:
  target_days: 56
complexity: medium
target_platform:
  controller: ESP32-S3
lifecycle:
  current_stage: requirements
  status: not_started
  stages:
    requirements:
      id: requirements
      name: PROJECT REQUIREMENTS
      order: 1
      status: NOT_STARTED
      started_at: null
      completed_at: null
      dependencies: []
    ...
metadata:
  created_at: '2026-08-22T02:30:00Z'
  updated_at: '2026-08-22T02:30:00Z'
```

---

## Lifecycle

Workline enforces a 36-stage sequential engineering lifecycle state model:

```
PROJECT REQUIREMENTS
        ↓
PROBLEM DEFINITION
        ↓
OPERATING LIMITS
        ↓
SYSTEM ARCHITECTURE
        ↓
SUBSYSTEM DECOMPOSITION
        ↓
COMPONENT SELECTION
        ↓
DATASHEET VALIDATION
        ↓
POWER ARCHITECTURE
        ↓
GPIO / INTERFACE MAPPING
        ↓
SCHEMATIC
        ↓
BOM
        ↓
FIRMWARE ARCHITECTURE
        ↓
DRIVER IMPLEMENTATION
        ↓
UNIT TESTING
        ↓
POWER-ON VALIDATION
        ↓
PERIPHERAL BRING-UP
        ↓
SENSOR CALIBRATION
        ↓
ACTUATOR VALIDATION
        ↓
CONTROL ALGORITHM
        ↓
SAFETY LOGIC
        ↓
INTEGRATION TEST
        ↓
FAILURE-INJECTION TEST
        ↓
SIMULATED DATA PIPELINE
        ↓
TELEMETRY PROTOCOL
        ↓
BACKEND
        ↓
DATABASE
        ↓
DASHBOARD
        ↓
DATASET GENERATION
        ↓
DATA CLEANING
        ↓
FEATURE ENGINEERING
        ↓
TIME-SERIES MODEL
        ↓
FUTURE EXPECTANCY
        ↓
PERFORMANCE ANALYSIS
        ↓
DOCUMENTATION
        ↓
FINAL VALIDATION
        ↓
RELEASE
```

Each stage tracks:
* `id`: Unique stage identifier
* `name`: Human-readable stage title
* `order`: Position in lifecycle sequence (1 to 36)
* `status`: `NOT_STARTED` | `IN_PROGRESS` | `BLOCKED` | `COMPLETED` | `FAILED`
* `started_at` & `completed_at`: Timestamps
* `dependencies`: Preceding prerequisite stages

---

## Development

### Running the CLI Locally

Ensure dependencies are installed in your virtual environment:

```bash
pip install -e .
```

Run test suite:

```bash
pytest tests/cli -v
```

### Running the Web Application

**Backend Server (FastAPI):**

```bash
uvicorn backend.main:app --reload --port 8000
```

**Frontend Client (Next.js + TypeScript 7):**

```bash
cd frontend
npm run typecheck   # Typecheck using canonical TypeScript 7 compiler
npm run dev         # Development server
npm run build       # Production build
```

---

## Multi-Agent Architecture

Workline features an autonomous, hierarchical multi-agent engine powered by **Google ADK** (`google-adk`).

```
              WORKLINE ROOT AGENT
                 Google ADK
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
        PLANNING TREE        RESEARCH TREE
       Domain Researcher     Research Agent
        Timeline Agent       Innovation Agent
             │                   │
             └─────────┬─────────┘
                       │
             HUMAN DECISION CHECKPOINT
            [Continue Research / Start Build]
                       │
                       ▼
             HARDWARE BUILDER TREE
                 Builder Agent
                       │
     ┌───────────────┬─┴─────────────┬───────────────┐
     ▼               ▼               ▼               ▼
Listing Agent  Sorting Agent   Finance Agent   Component Agent
     │               │               │               │
Connection     Power Agent     Firmware Agent     PCB Agent
     │               │               │               │
     └───────────────┴───────┬───────┴───────────────┘
                             ▼
                      Validation Agent
                             ▼
                         BOM Agent
```

### Data & State Separation

* **Google ADK**: Internal agent orchestration, session management, runner dispatch, and event tracking.
* **SurrealDB**: Authoritative primary structured state, lifecycle stages, and multi-relational engineering graph (`CONTAINS`, `SATISFIES`, `CONNECTS_TO`, `POWERED_BY`, `BLOCKS`).
* **Qdrant**: Derived semantic vector store for technical documentation, academic papers, datasheets, and circuit design patterns.

