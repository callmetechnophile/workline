# WORKLINE CLI (`wline`) User Guide

The canonical command-line interface for the **WORKLINE / ArmourFlow AI** Autonomous Cyber-Physical Engineering Platform.

---

## 1. Canonical CLI Executable

The user-facing executable is:

```bash
wline
```

Every public command begins with `wline`.

```bash
wline --help
wline --version
```

---

## 2. Command Hierarchy

```text
wline
├── init
├── project
│   ├── create
│   ├── list
│   ├── inspect
│   └── status
├── agents
│   ├── list
│   ├── info <agent-id>
│   ├── capabilities [agent-id]
│   └── health
├── task
│   ├── create
│   ├── run [task-id]
│   ├── status <task-id>
│   ├── cancel <task-id>
│   └── history
├── workflow
│   ├── list
│   ├── create
│   ├── validate <workflow-name>
│   ├── run <workflow-name>
│   ├── status <workflow-id>
│   └── history
└── system
    ├── status
    ├── health
    └── version
```

---

## 3. Platform & System Commands

### `wline system status`
Displays the active environment, platform configuration, registered agent count, and underlying runtime layers. Supports `--json`.

```bash
wline system status
wline system status --json
```

### `wline system health`
Inspects live connectivity and readiness across all platform subsystems (Agent Control Fabric, State/Graph DB, Model Provider, Authorization boundary, and Agent Registry).

```bash
wline system health
wline system health --json
```

### `wline system version`
Outputs CLI version, protocol version, and agents schema version.

```bash
wline system version
wline system version --json
```

---

## 4. Internal 27-Agent Registry Commands (`wline agents`)

The `wline agents` command set manages and inspects the 27 internal WORKLINE domain engineering agents.

### `wline agents list`
Lists all 27 domain engineering agents individually with their real statuses (#01 through #27). Never collapses agents into ranges.

```bash
wline agents list
wline agents list --json
```

### `wline agents info <agent-id>`
Inspects detailed metadata for a specific agent. Supports flexible identifiers such as `14`, `#14`, or `agent.14`.

```bash
wline agents info 14
wline agents info agent.18 --json
```

### `wline agents capabilities [agent-id]`
Lists the capabilities provided by an individual agent or across the entire platform.

```bash
wline agents capabilities 18
wline agents capabilities --json
```

### `wline agents health`
Performs live importability and readiness checks for all 27 internal agents without faking states.

```bash
wline agents health
wline agents health --json
```

---

## 5. Task Orchestration Commands (`wline task`)

All task operations route through the `AgentControlFabric`. The CLI acts as a thin client.

### `wline task create`
Submits a new task to the Control Fabric for an agent or capability.

```bash
wline task create --agent agent.24 --capability dfm_analysis --payload '{"component": "bracket"}'
```

### `wline task run [task-id]`
Submits a task or re-runs an existing task by ID.

```bash
wline task run --agent agent.19 --capability simulation.thermal --payload '{"scenario": "thermal_load"}'
```

### `wline task status <task-id>`
Displays the lifecycle state and output of a submitted task.

```bash
wline task status task_12345
wline task status task_12345 --json
```

### `wline task cancel <task-id>`
Requests cancellation of a queued or running task.

```bash
wline task cancel task_12345
```

### `wline task history`
Lists past task executions and audit logs for a project.

```bash
wline task history --project default
wline task history --json
```

---

## 6. Workflow Dispatch Commands (`wline workflow`)

Manages named capability sequences across domain agents.

### `wline workflow list`
Displays all available named engineering workflows and their associated capabilities.

```bash
wline workflow list
wline workflow list --json
```

### `wline workflow validate <name>`
Validates that a workflow definition has registered agent providers.

```bash
wline workflow validate simulation-study
wline workflow validate simulation-study --json
```

### `wline workflow run <name>`
Executes a workflow through the Agent Control Fabric.

```bash
wline workflow run simulation-study --payload '{"component": "heat_sink"}'
wline workflow run simulation-study --json
```

### `wline workflow status <workflow-id>`
Inspects execution status of a running or completed workflow.

```bash
wline workflow status wf_task_id
```

### `wline workflow history`
Lists recorded workflow runs for a project.

```bash
wline workflow history --json
```

---

## 7. Project Context Commands (`wline project`)

Manages engineering project workspaces and manifests.

- `wline project list [--json]`
- `wline project create [--name <name>]`
- `wline project inspect [name] [--json]`
- `wline project status [name]`

---

## 8. Deterministic Exit Codes

| Exit Code | Meaning |
|---|---|
| `0` | Success |
| `1` | General error |
| `2` | Invalid command / arguments |
| `3` | Configuration error |
| `4` | Authorization failure |
| `5` | Service unavailable |
| `6` | Task failure |
| `7` | Timeout |
| `8` | Cancellation |
| `9` | Validation failure |
