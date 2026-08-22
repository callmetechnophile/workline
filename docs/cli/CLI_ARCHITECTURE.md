# Workline CLI Architecture Specification

**Executable Name**: `wline`  
**Current Version**: `0.1.0`  
**Distribution Model**: Local Client Executable (`pip install workline` / `pipx install workline`)

---

## 1. Directory Structure

```
cli/
├── tests/
│   └── test_cli_standalone.py      # Independent CLI test suite
├── wline/
│   ├── api/                        # HTTP client wrappers targeting R1 Gateway
│   ├── commands/                   # Command group implementations
│   │   ├── agent.py
│   │   ├── bom.py
│   │   ├── config.py
│   │   ├── doctor.py               # Diagnostics & doctor command
│   │   ├── git.py
│   │   ├── pcb.py
│   │   └── project.py
│   ├── core/                       # Local state, .wlipjt, paths, and workspace logic
│   │   ├── lifecycle.py
│   │   ├── paths.py
│   │   └── workspace.py
│   ├── ui/                         # Rich banners, tables, and progress spinners
│   │   ├── banner.py
│   │   └── output.py
│   ├── __init__.py
│   └── main.py                     # CLI entrypoint
└── __init__.py
```

---

## 2. Local-First Engineering Model

The CLI prioritizes zero-latency local operations:
- **Local File System**: Direct reading and writing of project configs, `.wlipjt` archives, and build artifacts.
- **Local Version Control**: Full control over local Git repositories, branch management, staging, commits, and tags.
- **Local Configuration**: Stored in `~/.workline/` without exposing private secrets.
- **Remote Compute**: Delegated to R1 Gateway only when AI reasoning, dense vector search, or heavy physical simulations are required.

---

## 3. Render R6 Role (CLI Distribution & Metadata)

- **Purpose**: Render R6 (`backend/services/cli/main.py`) operates as a lightweight **Release & Update Manifest Service**.
- **Endpoints**:
  - `GET /health` — Service health probe.
  - `GET /api/cli/version` — Latest recommended CLI release and minimum compatibility version.
  - `GET /api/cli/manifest` — Update manifests and platform installer links.
- **Execution Location**: The interactive CLI runs **strictly on the user's local terminal**, not as a long-running daemon on Render.
