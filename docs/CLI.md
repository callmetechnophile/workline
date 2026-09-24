# WORKLINE CLI (`wline`) — Canonical Command Reference

## Overview

The canonical command namespace for the WORKLINE environment is **`wline`**.
There is **NO** separate `wg` CLI.

WORKLINE uses a clean two-stage entry model:
1. **Bootstrap / Activation**:
   ```bash
   workline --activate
   ```
   Initializes the local environment, verifies runtime dependencies, probes core and derived services, sets up the activation session, and prepares `wline`.

2. **Active Environment Operations**:
   ```bash
   wline <command>
   ```
   All subsequent operations (project management, inspection, backup, recovery, diagnostics, integrations) use `wline`.

All domain engineering operations (BOM management, PCB routing, component selection, thermal simulation, formal requirements authoring, trade-off decisions) live inside the **WORKLINE** application and are accessed via `wline open`.

---

## Installation

WORKLINE declares two primary console scripts in `pyproject.toml`:
```toml
[project.scripts]
workline = "cli.wline.workline_entry:main"
wline = "cli.wline.main:main"
```

Install in development / editable mode:
```bash
pip install -e .
```

---

## Architecture Topology

```
                    TERMINAL
                        │
                        │
              workline --activate
                        │
                        ▼
              ┌─────────────────┐
              │     WORKLINE    │
              │ LOCAL ENVIRONMENT│
              └────────┬────────┘
                       │
                       ▼
                    wline
                       │
             ┌─────────┼─────────┐
             │         │         │
             ▼         ▼         ▼
          Project    Runtime   Backup
          Control   Control    /Restore
             │
             ▼
       ┌──────────────────┐
       │ WORKLINE ENGINE  │
       └────────┬─────────┘
                │
       ┌────────┼─────────┐
       ▼        ▼         ▼
   SurrealDB  Retrieval  Agents
                │
          ┌─────┴─────┐
          ▼           ▼
        Moss        Qdrant
          │           │
          └─────┬─────┘
                ▼
         Project Context
                │
       ┌────────┼────────┐
       ▼        ▼        ▼
      MCP      A2A     LiveKit
       │        │        │
       └────────┼────────┘
                ▼
         WORKLINE AGENT
                │
                ▼
        ENGINEERING WORKSPACE
```

---

## 1. Bootstrap: `workline --activate`

Initializes and activates the local WORKLINE environment:
```bash
workline --activate
```

Outputs the environment status table:
```
WORKLINE
------------------------------------------
Runtime        READY     Python 3.13 / wline v1.0.0
Project        READY     RescueSwarm
SurrealDB      READY     Port 8001 reachable
Qdrant         READY     Port 6333 reachable
Moss           READY     Local in-process semantic engine
Agents         READY     Local tool registry & A2A protocol
LiveKit        READY     Local token fallback active
------------------------------------------
WORKLINE environment ACTIVE.
```

If non-essential services (like LiveKit or container ports) are offline, WORKLINE enters **DEGRADED** mode and remains fully functional offline using local files and Moss.

---

## 2. Core Commands (`wline`)

### `wline`
Shows the current WORKLINE environment and active project status.

### `wline new`
Interactive wizard to scaffold a new engineering project.
```bash
wline new
```

### `wline open [project]`
Opens a project, sets it as active in the session, starts the local Docker stack if needed, and launches the WORKLINE web application.
```bash
wline open RescueSwarm
```

### `wline inspect [target]`
Inspects either a live `.wl` project directory or an exported `.wlipjt` archive package.
```bash
wline inspect
wline inspect backup.wlipjt --verbose
```

### `wline status`
Shows current WORKLINE environment, active project, and service reachability.
```bash
wline status
```

### `wline doctor`
Comprehensive multi-point environment diagnostics across 7 critical domains (CLI, Docker, Stack, Project, LLM Gateway, LiveKit, Git).
```bash
wline doctor
```

### `wline backup [path]`
Exports the project into a portable, tamper-evident `.wlipjt` archive.
All secrets (AWS keys, tokens, passwords) are automatically stripped.
```bash
wline backup
wline backup --git --vectors --output ./backups/
```

### `wline restore <project.wl>`
Restores a project from a `.wlipjt` archive or `.wl` bundle.
```bash
wline restore backup.wlipjt --target ./restored/ --strategy restore
```

### `wline sync [project_id]`
Synchronizes `.wl` state between the local workspace and configured storage.
```bash
wline sync
```

### `wline drive`
Google Drive browser-agent backup & restore.
Uses the user's active browser session without requiring Google Drive API keys or OAuth setup.
```bash
wline drive --action backup
wline drive --action restore
```

### `wline version` / `wline --version`
Displays WORKLINE version information.
```bash
wline version
```

---

## 3. External API Configuration: `wline --apis`

The centralized entrypoint to configure external integrations (Amazon Bedrock, NVIDIA NIM, OpenAI, Anthropic, GitHub, Nexar, LiveKit, Tavily) **without** storing secrets in `.wl` project files.

### Interactive Configuration Manager
```bash
wline --apis
# Or:
wline apis
```

### Provider Status
```bash
wline --apis status
```

### Reset Provider Configuration
```bash
wline --apis reset
```

All credentials are saved to machine-local storage at `~/.workline/credentials.json` under named profiles (`default`, `development`, `production`).

---

## 4. Advanced Runtime Controls: `wline runtime ...`

Diagnostic and developer commands for managing internal services:
- `wline runtime status`: Check container services and ports.
- `wline runtime start`: Start Docker Compose services (`surrealdb`, `qdrant`, `redis`, `api`, `worker`).
- `wline runtime stop`: Stop container services.
- `wline runtime restart`: Restart container services.
- `wline runtime logs [service]`: Tail logs for a specific service.
