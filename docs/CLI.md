# WORKLINE CLI (`wg`) User & Reference Guide

**WORKLINE CLI (`wg`)** is the standalone developer command-line interface for portable engineering projects. It operates directly over the `.wl` filesystem with an embedded, on-device **Local Moss Semantic Retrieval Layer**.

---

## 1. Quick Start

### Installation & Verification
```bash
# Verify CLI installation
wg --version
wg doctor
```

### Initializing a New Project
```bash
# Initialize an engineering project
wg init autonomous-drone --domain "Hardware Systems & Power Engineering"

# Enter project directory
cd autonomous-drone

# Open and verify project
wg open
```

---

## 2. Command Reference

### Core Project Commands

| Command | Description | Example |
| :--- | :--- | :--- |
| `wg init <name>` | Initialize standard `.wl` filesystem structure | `wg init my-drone -d "Robotics"` |
| `wg open [path]` | Detect and open active WORKLINE project | `wg open` |
| `wg inspect [path]` | Telemetry overview of resources and Moss index | `wg inspect` |
| `wg check [path]` | Cryptographic manifest and zero-secrets audit | `wg check` |
| `wg doctor` | Comprehensive workspace & system diagnostics | `wg doctor` |

### Local Moss Retrieval & AI Commands

| Command | Description | Example |
| :--- | :--- | :--- |
| `wg index` | Build full local Moss semantic retrieval index | `wg index` |
| `wg index --incremental` | Index only modified/added resources via hashes | `wg index --incremental` |
| `wg index --rebuild` | Clear derived index and rebuild from `.wl` files | `wg index --rebuild` |
| `wg index --watch` | Realtime watch mode for file changes | `wg index --watch` |
| `wg index status` | View index document counts and health | `wg index status` |
| `wg search "<query>"` | Hybrid semantic + lexical search over project | `wg search "12V regulator" -t component` |
| `wg context "<query>"` | Retrieve structured context bundle within budget | `wg context "power distribution"` |
| `wg ask "<question>"` | Grounded AI Q&A with verified file citations | `wg ask "Why did we choose TPS62160?"` |
| `wg voice [--text]` | Realtime conversational LiveKit agent session | `wg voice --text` |

### Domain Resource Inspection

| Command | Description |
| :--- | :--- |
| `wg requirements` | Inspect functional, technical, and constraint requirements |
| `wg architecture` | View system block diagram and subsystem interfaces |
| `wg components` | View component dossiers and Manufacturer Part Numbers (MPN) |
| `wg bom` | Inspect Bill of Materials, quantities, and cost estimates |
| `wg tasks` | Filter tasks by status (`--status open`) and assignee (`--assignee rahul`) |
| `wg decisions` | View Architectural Decision Records (ADRs) |
| `wg research` | Search research literature dossiers and findings |
| `wg documents` | View technical specifications and datasheets |
| `wg analysis` | View power budget, thermal dissipation, and PCB stackup reports |
| `wg agents` | View configured domain agents and cryptographic audit receipts |
| `wg team` | View team members, roles, and export policies |

### Portability & Packaging

| Command | Description | Example |
| :--- | :--- | :--- |
| `wg export [--zip]` | Bundle project into `.workline.zip` (excludes secrets & index) | `wg export --zip` |
| `wg import <path>` | Extract `.workline.zip` and automatically rebuild Moss index | `wg import drone.workline.zip` |
| `wg sync` | Reconcile manifest hashes and update local retrieval | `wg sync` |
| `wg git [status\|diff]` | Run Git operations with strict `.wlignore` rules | `wg git status` |

---

## 3. Invariant Guarantees

1. **Zero-Secrets Policy**:
   `.env`, credentials, private keys (`*.key`, `*.pem`), and tokens are strictly excluded from indexing, exports, and search.
2. **Offline-First Resilience**:
   The CLI and local Moss retrieval run 100% locally. Pass `wg --offline` to enforce zero external network calls.
3. **Rebuildability**:
   If the `.wl/index/` directory is deleted, running `wg index --rebuild` fully reconstructs all semantic retrieval capabilities from the authoritative `.wl` filesystem.
