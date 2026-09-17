# Technical Documentation Agent — Design Reference

## Architecture
All service calls flow through `TechDocAgent.run()`. The agent dispatches to the service layer.
LLM (Bedrock / MockDocProvider) is invoked ONLY for prose generation in `DocumentEngine`.
All deterministic metadata (IDs, revisions, status, authority, timestamps) is set by Python code.

## Zero-Fabrication Invariant
1. `DocumentEngine.create()` assigns `status=DRAFT`, `authority=UNKNOWN` unless explicit claim provided.
2. Authority claims are validated against `AuthorityLevel` enum — invalid strings → `UNKNOWN`.
3. Never auto-elevates: `ASSUMPTION` is never promoted to `VERIFIED` or `AUTHORITATIVE` silently.
4. Missing data returns `UNKNOWN` or `DATA_REQUIRED`, never a fabricated value.

## Self-Approval Block
`RevisionEngine.transition()` checks: if `target_status in (APPROVED, PUBLISHED)` and `approver == doc.author`, returns `SELF_APPROVAL_DENIED`.

## ArmorIQ Authorization
`PublicationWorkflow.publish()` checks `armoriq_authorized` flag for channels:
- `CONTROLLED_VAULT`
- `EXTERNAL_RELEASE`
- `REGULATORY_SUBMISSION`

`INTERNAL_REVIEW` channel does NOT require ArmorIQ authorization.

## Conflict Detection
`ContradictionDetector.detect()` checks: authority rank divergence ≥ 3, duplicate type+title, section content length divergence ≥ 5×.
All resolutions are returned as `CONFLICT_DETECTED` — the caller decides what to do.

## Quality Scoring
`QualityValidator.validate()` deducts penalty for:
| Issue | Penalty |
|---|---|
| No sections | 0.40 |
| Unknown/Assumption authority | 0.15 |
| No traceability links | 0.10 |
| Stale/Reassessment freshness | 0.15 |
| Each unresolved conflict | 0.20 |
| Approved/Published without approver | 0.20 |

Minimum thresholds (policy constants in `config.py`):
- Review: 0.60
- Approval: 0.75
- Publish: 0.80
