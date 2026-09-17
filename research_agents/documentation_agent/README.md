# Agent #27 — Technical Documentation & Engineering Publication Agent

Part of the **WorkflowGuide AI / ArmourFlow AI** engineering platform.

## Purpose
Creates, manages, reviews, approves, and publishes engineering documents while enforcing:
- **Zero Fabrication invariant** — LLM generates prose only; all metadata is deterministic
- **Self-approval block** — authors cannot approve their own documents
- **ArmorIQ authorization** — controlled publication requires explicit authorization
- **Conflict detection** — contradictions returned as `CONFLICT_DETECTED`, never auto-resolved
- **Authority integrity** — authority levels never silently elevated (ASSUMPTION ≠ FACT)

## Document Types (25+)
System Requirements Spec, ICD, Design Description, Architecture Document, Trade Study,
ECN, Drawing Package, Test Plan, Test Report, VCME, FMEA, FTA, Reliability Prediction,
Hazard Analysis, Threat Model, Security Assessment, Operations Manual, Maintenance Procedure,
Deployment Guide, Project Plan, Lessons Learned, and more.

## Document Lifecycle
```
DRAFT → IN_REVIEW → APPROVED → PUBLISHED → SUPERSEDED → ARCHIVED
              ↓
    REVIEW_CHANGES_REQUIRED → DRAFT
              ↓
           WITHDRAWN → ARCHIVED
```

## Operations
| Operation | Description |
|---|---|
| `create_document` | Create a new document with LLM-generated prose sections |
| `get_document` | Retrieve a document by ID |
| `list_documents` | List all documents for a project |
| `review_document` | Submit for review (DRAFT → IN_REVIEW) |
| `approve_document` | Approve (requires different user than author) |
| `publish_document` | Publish (controlled channels require ArmorIQ auth) |
| `check_traceability` | View/report traceability links |
| `detect_conflicts` | Detect contradictions between two documents |
| `compare_documents` | Side-by-side diff of two documents |
| `export_document` | Export as JSON, Markdown, PDF (placeholder), DOCX (placeholder) |
| `quality_check` | Score and flag a document for quality issues |

## Usage
```bash
python -m research_agents.documentation_agent --project-id PROJ-001 --operation create_document \
  --doc-type FMEA_REPORT --title "Thermal FMEA"

python -m research_agents.documentation_agent --eval
```

## Platform Integration
- **SurrealDB**: persistent document store
- **Amazon Bedrock**: LLM prose generation
- **ArmorIQ**: authorization for controlled publication
- **A2A**: receives tasks from lifecycle orchestrator, risk agent, compliance agent
- **Agent Control Fabric**: routing, event, task lifecycle
