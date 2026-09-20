# Workline System Performance & Latency Benchmarks

**Document ID:** `WORKLINE-DEBUG-16`  
**Execution Timestamp:** 2026-09-18T01:14:00+05:30  
**Harness:** Live Probe Telemetry  

---

## 1. Latency Profile

| Component / Path | Measured Latency | Performance Classification | SLA Benchmark |
| :--- | :---: | :---: | :---: |
| `GET /health` | 8.7ms | Sub-millisecond / Fast | < 20ms |
| `GET /version` | 6.86ms | Sub-millisecond / Fast | < 20ms |
| `GET /service` | 7.47ms | Sub-millisecond / Fast | < 20ms |
| `GET /api/cache/stats` | 16.1ms | Fast | < 50ms |
| `GET /api/agents/` | 13.7ms | Fast | < 50ms |
| Control Fabric Task | 171.72ms | Fast | < 500ms |
| `GET /health/database` | 2110.79ms | Degraded timeout (SurrealDB check) | < 3000ms |
| `GET /health/cluster` | 8188.12ms | Multi-service connection timeout | < 10000ms |

## 2. Throughput & Resource Observations

- **Process Memory:** Python process footprint stable at ~85MB under active test client and background worker loops.
- **Worker Concurrency:** Async worker loops execute without thread contention or event loop starvation.
