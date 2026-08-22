# System Testing Plan: Workline (Level 0 through Phase 10K)

## 1. Overview

This document outlines the phased verification plan for Workline / ArmourIQ-Workflow across all functional tiers.

## 2. Test Execution Hierarchy

- **Level 0:** Environment, dependencies, CLI commands, and database connectivity (SurrealDB, Qdrant).
- **Level 1:** Document parsing, structure extraction, and LlamaIndex knowledge ingestion.
- **Level 2:** Knowledge Graph relations, entity links, and graph traversal queries.
- **Level 3:** Deterministic requirement parsing, constraint extraction, and tolerance evaluation.
- **Level 4:** Engineering Decision Support engine, candidate ranking, and trade-off sensitivity analysis.
- **Level 5:** BOM generation, canonical-to-ordering part resolution, and supplier offer optimization.
- **Level 6:** PCB design rules, schematic connectivity, and pre-DRC checker.
- **Level 7:** Multi-physics simulation orchestrator (SPICE, Thermal FD, SI/PI, and PINN surrogate).
- **Level 8:** Cross-validation engine and discrepancy thresholds.
- **Level 9:** Export units, EDA format adapters, and immutable release packaging.
- **Level 10 (10A - 10K):** End-to-end full lifecycle integration scenarios.
