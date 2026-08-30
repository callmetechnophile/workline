# DeepResearchAgent (Agent #4)

**DeepResearchAgent** is Agent #4 of the WorkflowGuide AI multi-agent engineering platform. It analyzes structured research evidence gathered from **ResearchPaperAgent** (Agent #1), **WebResearchAgent** (Agent #2), and **DocumentProcessingAgent** (Agent #3), and utilizes **Amazon Bedrock** to perform deep cross-source reasoning, component trade studies, contradiction detection, and engineering synthesis.

---

## 1. Architecture & Pipeline

```
     Agent #1 (Papers)         Agent #2 (Web Evidence)      Agent #3 (Processed Docs)
            |                            |                             |
            +----------------------------+-----------------------------+
                                         |
                                         v
                                EvidenceAggregator
                    (Normalizes & validates into EvidenceItems)
                                         |
                                         v
                               CrossSourceComparator
                    (Pre-scans consensus & potential contradictions)
                                         |
                                         v
                               DeepResearchSynthesizer
                               (Amazon Bedrock via Converse API)
                                         |
                                         v
                                 ClaimExtractor
             (Partitions: Facts vs. Model Inference vs. Recommendations)
                                         |
                                         v
                             MarkdownReportFormatter
                       (Synthesizes publication-grade report)
                                         |
                                         v
                            DeepResearchAgentOutput
```

---

## 2. Directory Layout

```
research_agents/
└── deep_research_agent/
    ├── __init__.py                # Package exports
    ├── __main__.py                # CLI entry point (`python -m deep_research_agent`)
    ├── agent.py                   # Google ADK-compliant DeepResearchAgent
    ├── schemas.py                 # Pydantic schemas (Input, Output, EvidenceItem, Claims, TradeStudy, Contradictions, Report)
    ├── config.py                  # Settings (Bedrock Model ID, AWS Region, temperature, token budget)
    ├── repository.py              # SynthesisRepository interface (SurrealDB prep)
    ├── providers/
    │   ├── __init__.py
    │   ├── base.py                # Abstract ReasoningProvider interface & exceptions
    │   ├── bedrock.py             # Amazon Bedrock runtime adapter (boto3 Converse API)
    │   └── mock_provider.py       # Deterministic offline reasoning provider
    ├── services/
    │   ├── __init__.py
    │   ├── evidence_aggregator.py # Unifies evidence from Agents #1, #2, #3 into validated EvidenceItems
    │   ├── claim_extractor.py     # Separates explicit source claims, derived claims, model inference, and recommendations
    │   ├── cross_comparator.py    # Cross-source comparison & contradiction detection
    │   ├── synthesizer.py         # Structured synthesis engine and Bedrock prompt orchestration
    │   └── markdown_formatter.py  # Structured Markdown report builder with provenance
    ├── tests/
    │   ├── __init__.py
    │   ├── test_bedrock_provider.py  # Bedrock adapter & error translation tests
    │   ├── test_evidence.py          # Evidence aggregation, validation, and typing tests
    │   ├── test_claims.py            # Claim separation tests
    │   ├── test_comparator.py        # Cross-source comparison & contradiction detection tests
    │   ├── test_synthesizer.py       # Report synthesis and schema validation tests
    │   ├── test_agent.py             # End-to-end DeepResearchAgent workflow tests
    │   └── test_cli.py               # CLI test mode runner tests
    └── README.md                  # This documentation
```

---

## 3. Strict Claim & Provenance Typing

To ensure engineering rigor, the agent strictly separates claims:

| Claim Type | Meaning | Provenance Requirement |
|---|---|---|
| `explicit_source_claim` | Verbatim technical fact directly present in source text. | Must cite exact backing evidence ID (`ev-001`). |
| `derived_claim` | Deductive conclusion logically combined from two or more facts. | Cites multiple backing evidence IDs (`ev-001`, `ev-002`). |
| `model_inference` | Analytical deduction, feasibility estimate, or hypothesis made by the LLM. | Explicitly marked as AI reasoning; never masquerades as source fact. |
| `engineering_recommendation` | Actionable architectural choice, component selection, or guidance. | Justified with supporting claims and priority level. |

---

## 4. Amazon Bedrock Integration

- **Adapter**: [`providers/bedrock.py`](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/research_agents/deep_research_agent/providers/bedrock.py) invokes Bedrock models using `boto3.client("bedrock-runtime")` and the Converse API.
- **Model Support**: Default model `anthropic.claude-3-5-sonnet-20240620-v1:0` or `amazon.nova-pro-v1:0`.
- **Zero Credential Exposure**: Uses standard AWS environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, or IAM instance profile).

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `BEDROCK_MODEL_ID` | `anthropic.claude-3-5-sonnet-20240620-v1:0` | Amazon Bedrock model identifier |
| `BEDROCK_REGION` | `us-east-1` | AWS region hosting Bedrock runtime |
| `BEDROCK_TEMPERATURE` | `0.2` | Sampling temperature for analytical synthesis |
| `BEDROCK_MAX_TOKENS` | `4096` | Maximum token budget for report generation |
| `BEDROCK_TIMEOUT_SECONDS` | `60.0` | Timeout for Bedrock API calls |

---

## 5. Local Execution & CLI

```bash
# Offline demo run
python -m deep_research_agent --demo --project "Autonomous Search and Rescue Drone" --domain "Robotics"

# Run with custom markdown export
python -m deep_research_agent --demo --output ./synthesis_report.md
```

---

## 6. Testing

Run all unit and integration tests:

```bash
pytest research_agents/deep_research_agent/tests/ -v
```

---

## 7. Future Integrations

- **A2A Interface**: Exposes `research.synthesize`, `research.trade_study`, `research.compare`, `research.claims`, `research.report`.
- **SurrealDB**: `SynthesisRepository` (`repository.py`) defines methods for storing synthesis reports, claims, trade studies, and recommendations.
