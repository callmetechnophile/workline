# ADR-001: Asynchronous Execution Engine & Dead-Letter Queue (DLQ)

## Status
Accepted

## Context
Long-running workloads in Workline (PINN physics training, thermal simulations, multi-vendor procurement queries, document parsing) previously executed synchronously within HTTP requests, leading to request timeouts, poor UI responsiveness, and vulnerability to network disruptions.

## Decision
Introduce a dedicated asynchronous job engine (`backend/workline/jobs/`) with:
1. Pydantic `Job` schema defining uniform execution lifecycle states (`PENDING`, `QUEUED`, `RUNNING`, `SUCCEEDED`, `FAILED`, `CANCELLED`, `RETRYING`, `DEAD_LETTER`).
2. Pluggable `JobQueue` contract with thread-safe `LocalJobQueue` for local single-process development and tests.
3. Decoupled `JobWorker` with exponential backoff retries and automatic DLQ escalation after exhaustion of retries.
4. Clean REST endpoints mounted at `/api/jobs` for job submission, query, and cancellation.

## Consequences
- Long-running endpoints now return HTTP 202 Accepted with a Job ID.
- Failures do not crash the web server.
- Faulty jobs are isolated in DLQ for engineering post-mortems.
