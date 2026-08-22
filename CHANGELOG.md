# Changelog

All notable changes to the Workline engineering orchestration platform are documented in this file.

## [v1.0.0-rc1] - 2026-08-22

### Release Candidate Summary
- **Systems Validation:** 100% test pass rate (302/302 tests passing across Level 0 through Level 10K).
- **Core Architecture:** Level 0 (Environment) through Level 10K (Release Readiness).
- **Security Audit:** Zero credential leakage, multi-tenant project isolation, strict role-based order approvals.

### Added
- **Multi-Physics Simulation Orchestrator & Cross-Validation:** SPICE DC solver, 2D Finite-Difference thermal reference solver, SI/PI solver, PINN surrogate prediction cross-validation with automatic tolerance categorization (`PASS` $\le 5\%$, `WARNING` $5\%-15\%$, `FAIL` $>15\%$).
- **PCB Design Subsystem:** Board geometry, layer stackups, electrical pin typing, net connectivity, pre-DRC trace/clearance verification, KiCad/Altium EDA neutral serialization.
- **BOM & Procurement Engine:** Canonical-to-ordering MPN resolution, distributor offer comparison (DigiKey, Mouser, Robu, Robocraze, Nexar), volume tier pricing, no-substitution rule.
- **Deterministic Requirement Validation:** Exact numeric engineering comparisons with unit parsing and tolerance bounds.
- **Engineering Decision Engine:** Multi-criteria weighted scoring, uncertainty evaluation, sensitivity analysis, human review gates.
- **Multi-Agent Engine & Interoperability:** ADK runtime session orchestration, Bindu A2A protocol, Corsair external agent integration.
- **Knowledge Infrastructure:** SurrealDB entity-relationship graph, Qdrant vector retrieval, Docling & spaCy parsing, tiered L1/L2 cache.
- **x402 Procurement:** Machine-to-machine payment request generation and mock verification with idempotency protection.
- **Release Engine:** Deterministic `.wlipjt` snapshot serialization with SHA-256 integrity verification.
