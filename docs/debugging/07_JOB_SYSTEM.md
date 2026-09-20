# Workline Asynchronous Job System & DLQ Audit

**Document ID:** `WORKLINE-DEBUG-07`  
**Execution Timestamp:** 2026-09-18T01:14:00+05:30  
**Target Module:** `backend.workline.jobs`  

---

## 1. Queue Architecture & State Transitions

```
[QUEUED] ──> [RUNNING] ──> [SUCCEEDED]
                 │
                 ├──> [RETRYING] (attempts < max_retries)
                 │         │
                 │         └──> [QUEUED]
                 │
                 └──> [FAILED] ──> [DEAD_LETTER] (non-retryable or attempts >= max)
```

## 2. Test Execution Data

- **Direct Job Enqueue:** `job_6c85ee48c6ef`
- **Initial State:** `SUCCEEDED`
- **Post-Worker State:** `SUCCEEDED`
- **Terminal Verdict:** **REAL_PASS**

## 3. Error Classification & DLQ Routing

Verified against `tests/workline/test_fabric_and_llm_hardening.py`:
- **Retryable Errors:** Network timeouts, transient connection errors increment `retry_count` and re-queue.
- **Non-Retryable Errors:** `AuthorizationError`, `ContractValidationError` bypass retries and route directly to DLQ.
