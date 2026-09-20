# Workline Canonical CLI (`wline`) Audit

**Document ID:** `WORKLINE-DEBUG-14`  
**Execution Timestamp:** 2026-09-18T01:14:00+05:30  
**Executable:** `wline` (`cli.wline.main`)  

---

## 1. Tested Commands Matrix

| Command | Status | Exit Code | Latency | Output Snippet |
| :--- | :---: | :---: | :---: | :--- |
| `wline --help` | REAL_PASS | Exit Code 0 | 6947.81ms | `Usage: python -m cli.wline.main [OPTIONS] COMMAND [ARGS]...` |
| `wline --version` | REAL_PASS | Exit Code 0 | 6793.68ms | `+----------------------------- WORKLINE VERSION ------------` |
| `wline agents list` | REAL_PASS | Exit Code 0 | 8760.76ms | `WORKLINE INTERNAL AGENTS                            
+------` |
| `wline auth status` | REAL_FAIL | Exit Code 2 | 6746.9ms | `` |
| `wline jobs list` | REAL_FAIL | Exit Code 2 | 6830.13ms | `` |
| `wline system status` | REAL_PASS | Exit Code 0 | 8334.42ms | `+------------------ WORKLINE Engineering Lifecycle Platform ` |

## 2. Command Architecture & Subcommand Naming

- **Root CLI (`wline`):** Fully operational with rich formatted help and version display (`1.0.0-rc1`).
- **`wline system status`:** Successfully collects diagnostics from Control Fabric, Database, and Agent Registry.
- **`wline agents list`:** Successfully lists all registered agents in formatted table.
- **Subcommand Alignment:**
  - `wline jobs list` returned code 2 because `wline job` / `wline jobs` subcommands use `wline job status <id>` rather than a bare `list`.
  - `wline auth status` returned code 2 because the canonical command is `wline auth whoami`.
