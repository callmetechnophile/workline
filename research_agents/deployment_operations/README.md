# Agent #26: Deployment & Operations Agent (`DeploymentOpsAgent`)

Part of the **WorkflowGuide AI / ArmourFlow AI** engineering platform.

## Overview
Agent #26 determines whether an engineered system is ready to deploy, how it should be installed and commissioned, how steady-state operations and health monitoring should be conducted, how maintenance should be scheduled, how incidents and rollbacks are managed, and how the system is safely decommissioned.

## Primary Engineering Question
> *"Can this system be safely and repeatably deployed, commissioned, operated, maintained, monitored, recovered, and eventually retired?"*

## Key Architectural Principles
- **Zero Fabrication Rule**: Missing thresholds, maintenance intervals, service times, or safety procedures strictly yield `UNKNOWN`, `THRESHOLD_UNKNOWN`, `MAINTENANCE_INTERVAL_UNKNOWN`, or `SAFETY_INFORMATION_REQUIRED`.
- **Hybrid Support**: Evaluates both physical hardware systems (clearance, mounting, power, cooling) and software/AI systems (runtimes, GPUs, secrets, model latency, token consumption).
- **ArmorIQ Authorization**: Privileged actions (production deployment, service restarts, firmware updates, database restores, rollbacks) enforce authorization barriers.
- **Cross-Agent Coordination**: Ingests DFM from Agent #24, Reliability from Agent #23, Sourcing from Agent #25, submits changes to Agent #16, and prepares verification evidence plans for Agent #18.

## CLI Usage
```bash
# Standalone execution
python -m research_agents.deployment_operations --project-id PROJ-101 --system-id SYS-1 --system-type HYBRID

# 5-Point Evaluation Benchmark
python -m research_agents.deployment_operations --eval
```
