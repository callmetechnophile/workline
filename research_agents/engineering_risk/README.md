# Agent #21: EngineeringRiskAgent (Risk & FMEA Intelligence Engine)

`EngineeringRiskAgent` provides deterministic Failure Mode and Effects Analysis (FMEA), Risk Priority Number (RPN) calculations, fault propagation graph tracing, single-point failure identification, and mitigation tracking for WorkflowGuide AI.

## Capabilities
- **Deterministic FMEA & RPN:** Calculates $RPN = S \times O \times D$ with configurable rating profiles and safety overrides.
- **Fault Propagation & SPF:** Traces multi-hop cascading dependencies and flags single points of failure without redundancy.
- **Mitigation & Residual Risk:** Proposes technical mitigations and tracks residual risk scores upon Agent #18 verification evidence.
- **Change Impact & Reassessment:** Reacts to Agent #16 change requests to invalidate stale risks and generate reassessment plans.
- **Zero Fabrication Policy:** Enforces explicit `UNKNOWN` / `ESTIMATED` declarations for missing empirical failure rates.
