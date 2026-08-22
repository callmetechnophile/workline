# Workline CLI Architecture & Boundary Audit

**Audit Date**: 2026-08-23  
**Executable Command**: `wline`  
**Location**: `cli/`

---

## 1. Technical Inventory

- **Language**: Python (>=3.9)
- **CLI Framework**: `Typer` (based on Click) with `Rich` formatted tables, trees, and terminal status indicators.
- **Entrypoint**: `cli.wline.main:main` (configured in `pyproject.toml` under `[project.scripts]`).
- **Installed Size**: `0.54 MB` (Source code & assets).
- **Core Dependencies**: `typer`, `rich`, `pydantic`, `httpx`, `pyyaml`.

---

## 2. Command Domain Mapping

| Command Group | Execution Scope | Description |
| :--- | :--- | :--- |
| **`wline init`** | **Local** | Initialize `.workline/` workspace context, `.wlipjt` metadata, and local Git repository. |
| **`wline project`** | **Local / Hybrid** | Manage project lifecycles (`create`, `open`, `list`, `status`, `export`). |
| **`wline git`** | **Local** | Local Git operations (`status`, `commit`, `log`, `branch`, `tag`). |
| **`wline github`** | **Remote** | Remote GitHub repository linking and sync. |
| **`wline doctor`** | **Local** | System diagnostics (Python version, Git presence, config validation). |
| **`wline config`** | **Local** | View and configure workspace settings (`show`, `set`). |
| **`wline status`** | **Local** | Active project lifecycle stage and milestone summary. |
| **`wline version`** | **Local** | Display CLI version, Git SHA, and active schema version. |
| **`wline snapshot`** | **Local** | Create deterministic cryptographic state snapshot linked to Git commit. |
| **`wline release`** | **Local / Remote** | Tag version, bump `.wlipjt` schema, and finalize package. |
| **`wline agent`** | **Remote (via R1)** | Trigger multi-agent research pipelines and monitor agent execution. |
| **`wline bom`** | **Remote (via R1)** | Generate, inspect, and optimize Bill of Materials across vendor catalogs. |
| **`wline pcb`** | **Remote (via R1)** | Run DRC checks, impedance modeling, and PINN placement solvers. |
| **`wline document`** | **Remote (via R1)** | Ingest and chunk technical datasheets into knowledge stores. |

---

## 3. Local vs Remote Boundary

```
  ┌────────────────────────────────────────────────────────┐
  │                    LOCAL WORKSPACE                     │
  │  .wlipjt file  •  Git repository  •  ~/.workline/      │
  └───────────────────────────┬────────────────────────────┘
                              │
                    HTTPS API (Authenticated)
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │               RENDER R1: CORE API GATEWAY              │
  │                        (:10000)                        │
  └───────────────────────────┬────────────────────────────┘
                              │
        ┌──────────────┬──────┴──────┬──────────────┐
        ▼              ▼             ▼              ▼
       R2             R3            R4             R5
    AI Agents      Knowledge    Engineering    Procurement
```
