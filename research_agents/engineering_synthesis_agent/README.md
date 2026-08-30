# EngineeringSynthesisAgent (Agent #5)

**EngineeringSynthesisAgent** is Agent #5 of the WorkflowGuide AI multi-agent engineering platform. It transforms the structured evidence and deep-research outputs produced by **ResearchPaperAgent** (Agent #1), **WebResearchAgent** (Agent #2), **DocumentProcessingAgent** (Agent #3), and **DeepResearchAgent** (Agent #4) into actionable, evidence-backed engineering design decisions, trade-off evaluations, risk assessments, and validation requirements for a specific engineering project.

---

## 1. Multi-Agent Architecture & Position

```
User
  ↓
Research Orchestrator
  ↓
Agent #1 — ResearchPaperAgent (Academic Papers via Freephdlabor)
  ↓
Agent #2 — WebResearchAgent (Engineering Web Evidence via Tavily + Anakin)
  ↓
Agent #3 — DocumentProcessingAgent (PDF/HTML Normalization, Markdown, Chunks, Facts, Entities)
  ↓
Agent #4 — DeepResearchAgent (Amazon Bedrock Cross-Source Reasoning & Evidence Synthesis)
  ↓
Agent #5 — EngineeringSynthesisAgent (Decisions, Trade-offs, Risks, Validation, Traceability)
  ↓
Future Agent #6 (Execution & Synthesis Downstream)
```

---

## 2. Core Staged Pipeline

```
Project Requirements
        ↓
Evidence Validation & Hierarchy Evaluation
        ↓
Technical Finding Extraction
        ↓
Cross-Source Comparison & Trade-off Analysis
        ↓
Requirement Mapping & Qualitative Coverage
        ↓
Engineering Decision Generation
        ↓
Qualitative Risk Analysis
        ↓
Validation Planning & Empirical Experiment Design
        ↓
End-to-End Decision Traceability Generation
        ↓
18-Section Structured Engineering Report & 5-File Artifact Bundle
```

---

## 3. Mandatory Decision Traceability

Every major engineering decision establishes an unbroken lineage:

$$\text{Project Requirement} \longrightarrow \text{Evidence} \longrightarrow \text{Finding} \longrightarrow \text{Trade-off} \longrightarrow \text{Decision} \longrightarrow \text{Validation}$$

```json
{
  "decision_id": "DEC-001",
  "requirement_ids": ["REQ-001", "REQ-002"],
  "evidence_ids": ["ev_p_001", "ev_w_001"],
  "finding_ids": ["FIND-001"],
  "tradeoff_id": "TRADE-001",
  "decision": "NVIDIA Jetson Orin Nano 8GB",
  "reasoning": "Meets 30+ FPS latency requirement with verified 45 FPS benchmark on INT8 TensorRT at 15 W.",
  "validation_ids": ["VAL-001"]
}
```

---

## 4. Source of Truth Partitioning

| Classification | Meaning | Rule |
|---|---|---|
| `SOURCE FACT` | Verbatim technical specification directly extracted from source text. | Must cite exact backing evidence ID (`ev_001`). |
| `DERIVED FINDING` | Technical finding synthesized across multiple verified facts. | Cites multiple backing evidence IDs. |
| `MODEL INFERENCE` | Hypothesis, estimation, or deduction made by LLM reasoning. | Explicitly labeled as AI deduction; never presented as source fact. |
| `ENGINEERING DECISION` | Concrete hardware/software architectural selection. | Backed by trade-off analysis and project requirements. |
| `ENGINEERING RECOMMENDATION` | Actionable guideline or best practice. | Includes rationale, assumptions, and priority. |
| `VALIDATION REQUIREMENT` | Procedure for verifying an engineering decision. | Defines acceptance criteria and test category. |

---

## 5. Artifact Export Engine (Section 36)

When invoked with `--output <directory>`, the agent generates 5 distinct artifacts:

1. `engineering_analysis.json`: Complete machine-readable synthesis object.
2. `engineering_report.md`: Comprehensive 18-section publication-ready Markdown report.
3. `engineering_decisions.json`: Standalone array of engineering design decisions.
4. `engineering_risks.json`: Qualitative risk items with severity and mitigations.
5. `engineering_validation.json`: Verification procedures and empirical experiment plans.

---

## 6. CLI Usage & Development Mode

```bash
# Run offline demo mode
python -m engineering_synthesis_agent --demo --project "Autonomous Search and Rescue Drone"

# Run with custom input bundle and export directory
python -m engineering_synthesis_agent \
    --input ./research_bundle.json \
    --output ./engineering_analysis
```

---

## 7. Testing

Run all unit and integration tests across the platform:

```bash
pytest research_agents/engineering_synthesis_agent/tests/ -v
```

---

## 8. Future Integrations

- **Google ADK & A2A**: Exposes `engineering.analyze`, `engineering.compare`, `engineering.decide`, `engineering.recommend`, `engineering.validate`.
- **SurrealDB Persistence**: `EngineeringDecisionRepository` (`repository.py`) defines abstract persistence methods ready for schema migration.
