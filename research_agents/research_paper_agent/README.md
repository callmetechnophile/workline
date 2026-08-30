# ResearchPaperAgent (Agent #1)

**ResearchPaperAgent** is Agent #1 of the WorkflowGuide AI multi-agent engineering platform. Given an engineering project description, it autonomously plans search angles, queries **Freephdlabor**, filters, deduplicates, ranks by multi-factor relevance, detects PDF availability, and returns structured research metadata for downstream engineering agents.

---

## 1. Architecture

```
WorkflowGuide Orchestrator
        |
        | A2A (future integration)
        |
        v
ResearchPaperAgent (Google ADK)
        |
        v
QueryPlanner (Multi-Angle Technical Queries)
        |
        v
QueryCache (SHA-256 LRU In-Memory Cache)
        |
        v
FreephdlaborProvider (Authoritative Acquisition Adapter)
        |
        v
PaperDeduplicator (Deterministic DOI / Title / URL Matching)
        |
        v
RelevanceScorer (Multi-Factor Scoring & Verifiable Reasons)
        |
        v
PaperNormalizer (PDF Link Detection & Schema Normalization)
        |
        v
Structured Research Results (ResearchPaperAgentOutput)
```

---

## 2. Directory Layout

```
research_agents/
└── research_paper_agent/
    ├── __init__.py                # Package exports
    ├── __main__.py                # CLI entry point
    ├── agent.py                   # Google ADK-compliant ResearchPaperAgent
    ├── schemas.py                 # Pydantic data contracts (Input, Output, Errors)
    ├── config.py                  # Environment variable configuration
    ├── prompts.py                 # Query planning & rubric definitions
    ├── repository.py              # ResearchRepository interface (SurrealDB prep)
    ├── providers/
    │   ├── __init__.py
    │   ├── base.py                # BasePaperProvider abstract class & exceptions
    │   └── freephdlabor.py        # Authoritative Freephdlabor adapter
    ├── services/
    │   ├── __init__.py
    │   ├── cache.py               # Lightweight deterministic query cache
    │   ├── search.py              # Multi-angle query planner
    │   ├── deduplication.py       # Deterministic DOI / title / URL deduplication
    │   ├── ranking.py             # Multi-factor relevance scoring engine
    │   └── retrieval.py           # Result normalizer & PDF link validator
    ├── tests/
    │   ├── __init__.py
    │   ├── test_agent.py          # End-to-end agent tests
    │   ├── test_freephdlabor.py   # Provider adapter & status code tests
    │   ├── test_deduplication.py  # DOI & title deduplication tests
    │   ├── test_ranking.py        # Relevance scoring tests
    │   ├── test_query_generation.py # Query planner tests
    │   └── test_cli.py            # CLI test runner tests
    └── README.md                  # This documentation
```

---

## 3. Data Contracts

### Input Schema (`ResearchPaperAgentInput`)

```json
{
  "project_title": "Autonomous Search and Rescue Drone",
  "project_description": "A drone using computer vision and thermal sensing to locate humans in disaster environments.",
  "engineering_domain": "Robotics / Computer Vision",
  "research_objectives": [
    "human detection",
    "thermal imaging",
    "autonomous navigation"
  ],
  "components": [
    "Jetson Orin Nano",
    "thermal camera"
  ],
  "technologies": [
    "YOLO",
    "computer vision"
  ],
  "constraints": [
    "real-time inference",
    "edge deployment"
  ],
  "keywords": [
    "thermal human detection",
    "UAV search and rescue"
  ],
  "max_papers": 20
}
```

### Output Schema (`ResearchPaperAgentOutput`)

```json
{
  "status": "success",
  "project": {
    "title": "Autonomous Search and Rescue Drone",
    "domain": "Robotics / Computer Vision"
  },
  "queries_used": [
    "thermal human detection Robotics",
    "UAV search and rescue Robotics",
    "YOLO thermal camera Robotics",
    "real-time inference YOLO"
  ],
  "papers_found": 15,
  "papers_selected": 3,
  "papers": [
    {
      "paper_id": "10.1109/ICRA.2024.001",
      "title": "Deep Thermal Object Detection for Autonomous Search and Rescue UAVs",
      "authors": ["Jane Doe", "John Smith"],
      "abstract": "Thermal sensor integration with YOLOv8 for edge UAV human rescue mission detection.",
      "publication_date": "2024-03-15",
      "doi": "10.1109/ICRA.2024.001",
      "venue": "IEEE ICRA",
      "source": "freephdlabor",
      "paper_url": "https://ieeexplore.ieee.org/document/001",
      "pdf_url": "https://ieeexplore.ieee.org/stamp/001.pdf",
      "pdf_available": true,
      "citation_count": 22,
      "keywords": ["thermal vision", "UAV", "YOLOv8"],
      "relevance_score": 0.88,
      "relevance_reasons": [
        "Title directly addresses: thermal human detection",
        "Investigates target research objective: human detection",
        "Evaluates target technology: YOLO",
        "Recent academic publication (2024)"
      ]
    }
  ],
  "errors": []
}
```

---

## 4. Environment Variables

| Variable | Default | Description |
|---|---|---|
| `FREEPHDLABOR_API_KEY` | `""` | API Key for Freephdlabor authentication |
| `FREEPHDLABOR_BASE_URL` | `https://api.freephdlabor.com/v1` | Freephdlabor search endpoint base URL |
| `FREEPHDLABOR_TIMEOUT_SECONDS` | `15.0` | HTTP request timeout in seconds |
| `FREEPHDLABOR_MAX_RETRIES` | `3` | Max HTTP retry attempts on retryable errors |
| `RESEARCH_DEFAULT_MAX_PAPERS` | `20` | Default paper limit if omitted in input |
| `RESEARCH_MAX_PAPERS_CAP` | `50` | Hard cap limit on returned papers |
| `RESEARCH_CACHE_ENABLED` | `true` | Enable/disable in-memory query cache |
| `RESEARCH_CACHE_TTL` | `3600` | In-memory cache TTL in seconds |
| `RESEARCH_LOG_LEVEL` | `INFO` | Structured logging verbosity |

---

## 5. Local Execution & CLI

### CLI Test Mode
Run the agent directly from the command line:

```bash
# Live search mode (queries configured FREEPHDLABOR_BASE_URL)
python -m research_paper_agent \
    --project "Autonomous Search and Rescue Drone" \
    --domain "Robotics" \
    --objective "thermal human detection" \
    --max-papers 10

# Mock test mode (simulates realistic candidates offline without external network)
python -m research_paper_agent \
    --mock \
    --project "Autonomous Search and Rescue Drone" \
    --domain "Robotics" \
    --objective "thermal human detection" \
    --max-papers 5
```

### Python SDK Usage

```python
import asyncio
from research_agents.research_paper_agent import (
    ResearchPaperAgent,
    ResearchPaperAgentInput,
)

async def main():
    agent = ResearchPaperAgent()
    output = await agent.run(
        ResearchPaperAgentInput(
            project_title="Autonomous Search and Rescue Drone",
            project_description="UAV system with thermal computer vision on edge hardware.",
            engineering_domain="Robotics / Computer Vision",
            research_objectives=["thermal human detection"],
            components=["Jetson Orin Nano"],
            technologies=["YOLOv8"],
            max_papers=10,
        )
    )
    for paper in output.papers:
        print(f"[{paper.relevance_score:.2f}] {paper.title} (PDF: {paper.pdf_available})")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 6. Testing

Run all unit and integration tests:

```bash
pytest research_agents/research_paper_agent/tests/ -v
```

Test coverage includes:
- **Agent lifecycle & limits**: limit capping, empty queries, synchronization
- **Freephdlabor adapter**: status codes (401, 429, 500, timeouts), sparse payload parsing
- **Deduplication**: DOI normalization, alphanumeric title matching, URL canonicalization
- **Relevance ranking**: scoring bounds $[0.0, 1.0]$, multi-factor alignment, verifiable reasons
- **Query planning**: multi-angle query generation and noise cleanup
- **CLI test runner**: rich table rendering and arg parsing

---

## 7. Future Integrations

### A2A Integration
The agent exposes the following standard capabilities ready for A2A routing:
- `research.search`
- `research.retrieve`
- `research.list`

### Bindu Integration
An adapter boundary is established in `agent.py` so that Bindu runtime wrappers can invoke `run()` or `run_sync()` without modifying core research acquisition logic.

### ArmorIQ Integration
The `RequestContext` model carries `user_id`, `project_id`, `agent_id`, `parent_agent_id`, `authorization_context`, and `execution_id` through every query lifecycle, allowing seamless policy checks and audit receipt generation.

### SurrealDB Integration
The abstract `ResearchRepository` interface (`repository.py`) defines standard persistence methods (`save_paper`, `save_project_paper_relationship`, `save_research_run`, `get_paper`, `get_project_papers`). In this phase, `InMemoryResearchRepository` is provided for tests; connecting SurrealDB requires implementing this single interface.
