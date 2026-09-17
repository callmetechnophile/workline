# ADR-002: Durable Agent State, Checkpoints & Secret Scrubbing

## Status
Accepted

## Context
Autonomous agents executing complex multi-step workflows (BOM optimization, compliance checking, DFM analysis) could not pause, resume, or provide auditable step-by-step telemetry. Furthermore, tool execution traces could inadvertently log API credentials or proprietary component secrets.

## Decision
Introduce `backend/workline/agent_state/` providing:
1. `AgentRun` aggregate tracking runs, steps, decisions, and outputs.
2. Step-level `ToolExecution` logging with duration metrics and secret field redaction (`redacted_fields`).
3. `AgentCheckpoint` snapshots for pause/resume capabilities.
4. Explicit `AgentDecision` records capturing confidence scores, reasoning chains, and alternative options considered.

## Consequences
- Full observability into agent cognition and tool execution without exposing sensitive secrets.
- Checkpoints provide reproducible debugging for agent failures.
