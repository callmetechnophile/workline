# Workline CLI (wline) — Comprehensive Test Specification Matrix

**Specification Standard:** WLINE-CLI-TEST-v1.0  
**Associated Command Spec:** [WLINE_CLI_COMMAND_SPEC.md](WLINE_CLI_COMMAND_SPEC.md)  
**Associated Registry:** [cli/wline/command_registry.yaml](../cli/wline/command_registry.yaml)

---

## 1. Test Architecture & Quality Gates

Every canonical command within the Workline CLI is required to satisfy a standardized 9-point verification suite:

1. **Help Test (`--help` / `-h`):** Verifies command documentation, argument syntax, option flags, and that execution cleanly returns exit code `0`.
2. **Argument Validation Test:** Verifies invalid arguments, missing required parameters, or malformed payloads trigger explicit error messages and return exit code `2` (`INVALID_ARGUMENTS`).
3. **Authentication Test:** Verifies unauthenticated invocations against protected cloud endpoints return exit code `4` (`AUTH_FAILURE`).
4. **Authorization Test:** Verifies role-based access control (RBAC) boundaries (e.g. `MEMBER` vs `ADMIN`) and ArmorIQ policy boundaries reject unauthorized actions with exit code `4`.
5. **Successful Execution Test:** Verifies nominal execution produces the expected human-readable output and returns exit code `0` (`SUCCESS`).
6. **Backend Failure Handling:** Verifies unreachable backend gateways, database failures, or circuit-breaker trips fail gracefully with exit code `5` (`SERVICE_UNAVAILABLE`).
7. **Timeout Handling:** Verifies prolonged network RPCs or agent execution exceeding deadlines terminate deterministically with exit code `7` (`TIMEOUT`).
8. **Deterministic JSON Cleanliness:** Verifies `--json` output contains strictly valid, parseable JSON with zero ANSI color escape codes, zero ASCII banners, and zero unhandled tracebacks.
9. **Exit Code Parity:** Verifies CLI returns the exact exit code specified in the canonical schema across both normal and error branches.

---

## 2. Canonical Command Test Matrix

| Canonical Command | Help Test | Argument Validation | Auth Test | Authz Test | Nominal Success | Backend Failure | Timeout Test | JSON Output | Exit Code Parity | Test Implementation Status |
|---|---|---|---|---|---|---|---|---|---|---|
| `wline init` | Pass (`--help` exits 0) | Missing/bad name (2) | N/A (Local) | N/A | Manifest + Git initialized (0) | FS permission error (1) | N/A | Deterministic payload | Tested (`test_wline_spec_compliance.py`) | **VERIFIED** |
| `wline system status` | Pass (`--help` exits 0) | Unknown flags (2) | N/A (Public) | N/A | Fabric, agents count, layers (0) | Fabric singleton failure (5) | N/A | Clean JSON, 27 agents | Tested (`test_wline_spec_compliance.py`) | **VERIFIED** |
| `wline system health` | Pass (`--help` exits 0) | Unknown flags (2) | N/A (Public) | N/A | Probes all 5 components (0) | Degraded DB / Models (5) | Probe timeout (7) | Clean JSON report | Tested (`test_wline_spec_compliance.py`) | **VERIFIED** |
| `wline system version` | Pass (`--help` exits 0) | Unknown flags (2) | N/A (Public) | N/A | CLI, schema, protocol (0) | N/A | N/A | Clean JSON object | Tested (`test_wline_spec_compliance.py`) | **VERIFIED** |
| `wline system diagnostics`| Pass (`--help` exits 0) | Unknown flags (2) | N/A (Public) | N/A | 13 configuration checks (0) | Missing critical config (3) | N/A | Clean JSON array | Tested (`test_wline_canonical.py`) | **VERIFIED** |
| `wline auth login` | Pass (`--help` exits 0) | Empty token (1/2) | Invalid Bearer (4)| N/A | Saves token to config (0) | Gateway unreachable (5) | HTTP timeout (7) | Status message | Needs automated mock token | **SPECIFIED** |
| `wline auth logout` | Pass (`--help` exits 0) | N/A | N/A | N/A | Session purged (0) | File write error (1) | N/A | Status message | Needs session test | **SPECIFIED** |
| `wline auth whoami` | Pass (`--help` exits 0) | N/A | Unauth local vs cloud | N/A | Identity panel displayed (0) | N/A | N/A | Clean JSON identity | Needs session test | **SPECIFIED** |
| `wline config list` | Pass (`--help` exits 0) | Unknown flags (2) | N/A | N/A | Workspace & config paths (0) | Corrupt config (3) | N/A | Table / JSON | Tested (`test_commands.py`) | **VERIFIED** |
| `wline config set` | Pass (`--help` exits 0) | Invalid key (1/2) | N/A | N/A | Key updated in config (0) | Read-only config (1) | N/A | Status message | Tested (`test_commands.py`) | **VERIFIED** |
| `wline project list` | Pass (`--help` exits 0) | Unknown flags (2) | N/A | N/A | Table of workspace projects (0)| FS unreadable (1) | N/A | Clean JSON array | Tested (`test_wline_spec_compliance.py`) | **VERIFIED** |
| `wline project create` | Pass (`--help` exits 0) | Duplicate name (1/2) | N/A | N/A | Manifest & dirs created (0) | Disk full / write error (1) | N/A | Manifest summary | Tested (`test_lifecycle.py`) | **VERIFIED** |
| `wline project open` | Pass (`--help` exits 0) | Non-existent name (1/2)| N/A | N/A | Sets active project in config (0)| N/A | N/A | Status message | Tested (`test_lifecycle.py`) | **VERIFIED** |
| `wline project inspect` | Pass (`--help` exits 0) | Non-existent name (2) | N/A | N/A | Manifest panel displayed (0) | Corrupt manifest (3) | N/A | Clean JSON manifest | Tested (`test_wline_spec_compliance.py`) | **VERIFIED** |
| `wline project status` | Pass (`--help` exits 0) | No active project (1) | N/A | N/A | Lifecycle stages rendered (0) | N/A | N/A | Table / JSON | Tested (`test_lifecycle.py`) | **VERIFIED** |
| `wline project delete` | Pass (`--help` exits 0) | Unknown project (1/2) | N/A | Owner check | Deletes project directory (0) | File locked (1) | N/A | Confirmation | Tested (`test_lifecycle.py`) | **VERIFIED** |
| `wline project export` | Pass (`--help` exits 0) | Unknown project (1) | N/A | N/A | Generates .wlipjt archive (0) | Package build error (1) | N/A | Package metadata | Tested (`test_manifest.py`) | **VERIFIED** |
| `wline project import` | Pass (`--help` exits 0) | Bad package path (1) | N/A | N/A | Restores project into workspace| Corrupt archive (9) | N/A | Import panel | Tested (`test_manifest.py`) | **VERIFIED** |
| `wline agents list` | Pass (`--help` exits 0) | Unknown flags (2) | N/A (Public) | N/A | All 27 agents listed (0) | Registry failure (5) | N/A | 27 JSON records | Tested (`test_canonical_27_agents.py`) | **VERIFIED** |
| `wline agents info <id>`| Pass (`--help` exits 0) | Invalid ID e.g. 31 (2)| N/A (Public) | N/A | Manifest panel displayed (0) | Not found (2) | N/A | Manifest JSON | Tested (`test_canonical_27_agents.py`) | **VERIFIED** |
| `wline agents capabilities`| Pass (`--help` exits 0)| Invalid agent ID (2) | N/A (Public) | N/A | Indexed capability list (0) | Not found (2) | N/A | Capability index | Tested (`test_canonical_27_agents.py`) | **VERIFIED** |
| `wline agents health` | Pass (`--help` exits 0) | Unknown flags (2) | N/A (Public) | N/A | Live import verification (0) | Broken entrypoint (1) | N/A | Health table / JSON | Tested (`test_canonical_27_agents.py`) | **VERIFIED** |
| `wline agent list` | Pass (`--help` exits 0) | Invalid protocol (2) | Token check (4) | N/A | External registered agents (0) | Gateway offline (5) | N/A | Table / JSON | Tested (`test_commands.py`) | **VERIFIED** |
| `wline agent discover` | Pass (`--help` exits 0) | Invalid filter (2) | Token check (4) | N/A | Discovers network agents (0) | Remote discovery error(5)| Discovery timeout (7)| Discovery list | Tested (`test_commands.py`) | **VERIFIED** |
| `wline agent info` | Pass (`--help` exits 0) | Unknown agent ID (1) | Token check (4) | N/A | Trust score & protocol (0) | Not found (1) | N/A | Details panel | Tested (`test_commands.py`) | **VERIFIED** |
| `wline agent task` | Pass (`--help` exits 0) | Bad capability (1) | Token check (4) | Policy check | Enqueues to InteropGateway (0) | Delegation rejected (4) | RPC timeout (7) | Execution summary | Tested (`test_commands.py`) | **VERIFIED** |
| `wline agent cancel` | Pass (`--help` exits 0) | Bad task ID (1) | Token check (4) | Owner check | Cancels external task (0) | Already finished (1) | N/A | Status message | Tested (`test_commands.py`) | **VERIFIED** |
| `wline task create` | Pass (`--help` exits 0) | Invalid JSON/target (2)| Token check (4) | Role check | Enqueues to JobQueue (0) | Queue offline (5) | N/A | Task ID + QUEUED state| Tested (`test_fabric_and_llm_hardening.py`) | **VERIFIED** |
| `wline task run` | Pass (`--help` exits 0) | Invalid JSON/target (2)| Token check (4) | Role check | Executes and renders output (0)| Worker crash (6) | Task timeout (7) | Result panel / JSON | Tested (`test_wline_spec_compliance.py`) | **VERIFIED** |
| `wline task status` | Pass (`--help` exits 0) | Non-existent ID (2) | Token check (4) | Member check | Returns live task state (0) | DB lookup failure (5) | Watch deadline (7) | Task state JSON | Tested (`test_wline_spec_compliance.py`) | **VERIFIED** |
| `wline task cancel` | Pass (`--help` exits 0) | Non-existent ID (2) | Token check (4) | Owner check | Marks state CANCELLED (0) | Terminal task error (6) | N/A | Status message | Tested (`test_wline_spec_compliance.py`) | **VERIFIED** |
| `wline task history` | Pass (`--help` exits 0) | Invalid limit (2) | Token check (4) | Member check | Project task history list (0)| DB error (5) | N/A | Task list JSON | Tested (`test_wline_spec_compliance.py`) | **VERIFIED** |
| `wline workflow list` | Pass (`--help` exits 0) | Unknown flags (2) | N/A (Public) | N/A | Catalogue of 7 workflows (0) | N/A | N/A | Catalogue JSON | Tested (`test_wline_spec_compliance.py`) | **VERIFIED** |
| `wline workflow validate`| Pass (`--help` exits 0)| Unknown workflow (2) | N/A (Public) | N/A | Validates capability bindings | Missing agent cap (9) | N/A | Validation JSON | Tested (`test_wline_spec_compliance.py`) | **VERIFIED** |
| `wline workflow run` | Pass (`--help` exits 0) | Malformed payload (2) | Token check (4) | Member check | Dispatches workflow pass (0) | Step agent failure (6) | Workflow timeout (7)| Workflow result JSON| Tested (`test_wline_spec_compliance.py`) | **VERIFIED** |
| `wline workflow status` | Pass (`--help` exits 0)| Bad workflow task ID(2)| Token check (4)| Member check | Inspects workflow task (0) | Not found (2) | N/A | State panel / JSON | Tested (`test_wline_spec_compliance.py`) | **VERIFIED** |
| `wline document ingest` | Pass (`--help` exits 0)| File not found (1/2) | Token check (4) | Member check | Docling + spaCy + Qdrant (0) | Corrupt PDF / parse (9) | Extraction timeout(7)| Ingestion summary | Tested (`test_commands.py`) | **VERIFIED** |
| `wline document list` | Pass (`--help` exits 0) | Bad project ID (2) | Token check (4) | Member check | Ingested documents list (0) | SurrealDB error (5) | N/A | Document table | Tested (`test_commands.py`) | **VERIFIED** |
| `wline document generate`| Pass (`--help` exits 0)| Malformed payload (2) | Token check (4)| Member check | TechDocAgent synthesis (0) | Bedrock failure (5) | Agent timeout (7) | Generated doc panel | Tested (`test_wline_canonical.py`) | **VERIFIED** |
| `wline engineering simulation`| Pass (`--help` exits 0)| Bad payload (1/2) | Token check (4)| Member check | Runs simulation via agent.19 | Agent error (6) | Solver timeout (7) | Simulation results | Tested (`test_wline_canonical.py`) | **VERIFIED** |
| `wline engineering optimize`| Pass (`--help` exits 0)| Bad objectives (1/2)| Token check (4)| Member check | Runs Pareto loop via agent.20| Infeasible space (6) | Solver timeout (7) | Pareto frontier | Tested (`test_wline_canonical.py`) | **VERIFIED** |
| `wline engineering dfm` | Pass (`--help` exits 0)| Bad component ref (1/2)| Token check (4)| Member check | Runs DFM check via agent.24 | Rule solver error (6) | Analysis timeout (7)| DFM report panel | Tested (`test_wline_canonical.py`) | **VERIFIED** |
| `wline pcb create` | Pass (`--help` exits 0) | Invalid dimensions (1)| Token check (4) | Member check | Creates PCB project unit (0) | Missing BOM (1) | N/A | PCB project summary | Tested (`test_commands.py`) | **VERIFIED** |
| `wline pcb validate` | Pass (`--help` exits 0) | Bad project (1) | Token check (4) | Member check | Runs DRC and net checks (0) | DRC violations (9) | N/A | DRC violation table | Tested (`test_commands.py`) | **VERIFIED** |
| `wline pcb pinn train` | Pass (`--help` exits 0) | Bad epochs (1) | Token check (4) | Member check | Trains neural thermal model | Convergence fail (1) | Epoch timeout (7) | Loss & epochs table | Tested (`test_commands.py`) | **VERIFIED** |
| `wline pcb pinn predict` | Pass (`--help` exits 0)| Non-numeric coords (1)| Token check (4)| Member check | Millisecond thermal eval (0) | Untrained model (1) | N/A | Predicted degrees C | Tested (`test_commands.py`) | **VERIFIED** |
| `wline bom generate` | Pass (`--help` exits 0) | No active project (1) | Token check (4) | Member check | Sourcing BOM synthesized (0) | Sourcing engine (5) | Vendor API timeout(7)| BOM items table | Tested (`test_commands.py`) | **VERIFIED** |
| `wline bom approve` | Pass (`--help` exits 0) | Non-existent BOM (1) | Token check (4) | Engineer check| Locks BOM for ordering (0) | Already locked (1) | N/A | Status message | Tested (`test_commands.py`) | **VERIFIED** |
| `wline component search`| Pass (`--help` exits 0)| Empty query (2) | N/A (Public) | N/A | Multi-vendor search candidates| Vendor API down (5) | Network timeout (7) | Candidate listings | Tested (`test_commands.py`) | **VERIFIED** |
| `wline order create` | Pass (`--help` exits 0) | Unapproved BOM (1) | Token check (4) | Engineer check| Generates split vendor orders | Pricing mismatch (1) | N/A | Order plan panels | Tested (`test_commands.py`) | **VERIFIED** |
| `wline order approve` | Pass (`--help` exits 0) | Unknown order ID (1) | Token check (4) | Admin check | Authorizes order placement (0)| Inadequate funds (4) | N/A | Approval receipt | Tested (`test_commands.py`) | **VERIFIED** |
| `wline order pay` | Pass (`--help` exits 0) | Unknown order ID (1) | Token check (4) | Admin check | x402 payment session settled | Gateway rejection (4)| Settlement timeout | Settlement receipt | Tested (`test_commands.py`) | **VERIFIED** |
| `wline payment status` | Pass (`--help` exits 0)| Unknown session (0/1)| Token check (4)| Member check | Displays tx hash & timestamps | N/A | N/A | Session panel | Tested (`test_commands.py`) | **VERIFIED** |
| `wline security audit` | Pass (`--help` exits 0)| Bad scope (1) | Token check (4) | Admin check | ArmorIQ boundary + agent.22 | Policy fault (4) | Audit timeout (7) | Audit report | Tested (`test_wline_canonical.py`) | **VERIFIED** |
| `wline security scan` | Pass (`--help` exits 0) | Bad target/model (1) | Token check (4) | Admin check | STRIDE/PASTA threat scan (0) | Threat solver (6) | Scan timeout (7) | Threat matrix | Tested (`test_wline_canonical.py`) | **VERIFIED** |
| `wline doctor` | Pass (`--help` exits 0) | Unknown flags (2) | N/A (Local) | N/A | 6 local runtime checks (0) | Missing Git/Python (1) | Gateway probe (7) | Diagnostic table | Tested (`test_commands.py`) | **VERIFIED** |

---

## 3. Test Execution Commands

```bash
# 1. Run all existing canonical wline CLI tests
pytest tests/cli/ -v

# 2. Run individual test suites
pytest tests/cli/test_canonical_27_agents.py -v
pytest tests/cli/test_wline_spec_compliance.py -v
pytest tests/cli/test_wline_canonical.py -v
pytest tests/cli/test_commands.py -v
pytest tests/cli/test_lifecycle.py -v
pytest tests/cli/test_manifest.py -v
pytest tests/cli/test_workspace.py -v

# 3. Run async fabric and LLM hardening integration tests
pytest tests/workline/test_fabric_and_llm_hardening.py -v
```
