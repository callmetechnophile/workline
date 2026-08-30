# EngineeringExecutionAgent (Agent #11)

**EngineeringExecutionAgent** is Agent #11 of the WorkflowGuide AI multi-agent platform. It is the **FIRST agent in the pipeline authorized to execute actual implementation operations** against the target engineering project codebase under **cryptographically enforced ArmorIQ authority**.

---

## 1. Multi-Agent Pipeline Position

```
User
  ↓
Research Orchestrator
  ↓
Agent #1 — ResearchPaperAgent (Academic Research via Freephdlabor)
  ↓
Agent #2 — WebResearchAgent (Engineering Web Evidence via Tavily + Anakin)
  ↓
Agent #3 — DocumentProcessingAgent (PDF/HTML Normalization, Chunks, Facts, Entities)
  ↓
Agent #4 — DeepResearchAgent (Amazon Bedrock Cross-Source Reasoning & Evidence Synthesis)
  ↓
Agent #5 — EngineeringSynthesisAgent (Requirements, Findings, Decisions, Risks)
  ↓
Agent #6 — EngineeringArchitectureAgent (Subsystems, Interfaces, Power, Flows, Graphs)
  ↓
Agent #7 — ComponentPlanningAgent (Engineering BOM, Exact Components, Validation)
  ↓
Agent #8 — BOMOptimizationAgent (BOM Optimization, Suppliers, Landed Cost, Logistics)
  ↓
Agent #9 — EngineeringValidationAgent (Engineering Quality Gate, Design Rules, Verdict)
  ↓
Agent #10 — ProjectExecutionAgent (Work Packages, Task Breakdown, Scheduling)
  ↓
Agent #11 — EngineeringExecutionAgent (Cryptographic ArmorIQ Scoped Implementation)
```

---

## 2. Zero-Implicit-Authority Principle

> [!IMPORTANT]
> **ZERO IMPLICIT AUTHORITY.**  
> Permission is *never* inferred from project context, conversation history, or LLM reasoning. The agent may ONLY execute tasks explicitly present in the authorized implementation plan. Out-of-scope paths, tools, operations, or unapproved component substitutions are immediately denied with `AUTHORIZATION_DENIED`.

### Mandatory Authorization Object
```json
{
  "authorization_id": "AUTH-SAR-EXEC-001",
  "parent_agent_id": "ResearchOrchestrator",
  "authorized_agent_id": "EngineeringExecutionAgent",
  "allowed_tasks": ["TASK-001", "TASK-002"],
  "allowed_tools": ["filesystem", "shell", "test_runner"],
  "allowed_paths": ["firmware/sensors/**", "src/inference/**"],
  "allowed_operations": ["read", "create", "modify", "test"],
  "expires_at": "2026-12-31T23:59:59Z"
}
```

---

## 3. Cryptographic ArmorIQ Authority Flow

Every execution operation flows through ArmorIQ without bypass:

$$\text{User Authorization} \longrightarrow \text{Parent Agent} \longrightarrow \text{ArmorIQ delegate()} \longrightarrow \text{capture\_plan()} \longrightarrow \text{ArmorIQ invoke()} \longrightarrow \text{Tool Call} \longrightarrow \text{Receipt}$$

- `capture_plan()`: Registers task sequence and cryptographic plan receipt before execution.
- `delegate()`: Passes scoped authority from parent to child agents.
- `invoke()`: Cryptographically verifies receipt signatures and tool boundaries before invoking tools.

---

## 4. Scoped Tools & Security Defenses

| Tool | Scoping & Enforcement |
|---|---|
| `filesystem` | Scoped by `allowed_paths` with path normalization, preventing `../` traversal, absolute path escape, and symlink escape. |
| `shell` | Allowlisted command execution (`python`, `pytest`, `make`, `cmake`). Dangerous operators (`;`, `&&`, `|`, `` ` ``) rejected. |
| `test_runner` | Scoped unit and integration test executions. |
| `git` | Default read-only (`status`, `diff`). `commit` and `push` strictly require explicit authorization. |

---

## 5. Pre/Post Change Detection

`ChangeDetector` captures full repository checksum snapshots before and after each task. If any files outside `allowed_paths` are created, modified, or deleted, the task fails immediately with `OUT_OF_SCOPE_MODIFICATION`.

---

## 6. 7-File Artifact Export (Section 62)

When invoked with `--output <directory>`, the agent exports:

1. `execution_result.json`: Complete machine-readable execution dataset.
2. `execution_report.md`: Publication-ready 18-section Markdown report.
3. `execution_graph.json`: Verifiable execution lineage graph.
4. `audit_trail.json`: Chronological cryptographic audit events.
5. `task_results.json`: Completed, failed, and blocked task breakdowns.
6. `changed_files.json`: Exact files created or modified.
7. `authorization_events.json`: Denied operations and authorization events.

---

## 7. CLI Usage & Development Mode

```bash
# Run demo with SAR drone implementation plan and intentional scope-denial test
python -m engineering_execution_agent --demo

# Run dry run
python -m engineering_execution_agent \
    --plan ./implementation_plan.json \
    --authorization ./authorization.json \
    --dry-run

# Run single task
python -m engineering_execution_agent \
    --plan ./implementation_plan.json \
    --authorization ./authorization.json \
    --task TASK-001 \
    --output ./execution_output
```

---

## 8. Automated Testing

```bash
pytest research_agents/engineering_execution_agent/tests/ -v
```
