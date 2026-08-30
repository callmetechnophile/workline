# WebResearchAgent (Agent #2)

**WebResearchAgent** is Agent #2 of the WorkflowGuide AI multi-agent engineering platform. Given an engineering project context, it investigates the public web to discover, extract, classify, deduplicate, and rank high-quality engineering evidence (open-source GitHub repositories, component datasheets, manufacturer documentation, application notes, and implementation tutorials) via **Tavily** and **Anakin**.

---

## 1. Architecture

```
WorkflowGuide Orchestrator
        |
        | Future A2A
        |
        v
WebResearchAgent (Google ADK)
        |
        +----------------------+
        |                      |
        v                      v
      Tavily                Anakin
 (Search & Retrieve)    (Scrape & Crawl)
        |                      |
        +----------+-----------+
                   |
                   v
          WebSourceDeduplicator
 (Canonical URL, Fingerprinting)
                   |
                   v
          SourceClassifier & AuthorityEvaluator
 (Types: github, datasheet, manufacturer; Authority: 0.20 - 0.98)
                   |
                   v
          WebRelevanceScorer
 (Multi-Factor Scoring & Verifiable Reasons)
                   |
                   v
          EvidenceExtractor
 (Structured Facts with Strict Provenance)
                   |
                   v
      WebResearchAgentOutput
```

---

## 2. Directory Layout

```
research_agents/
└── web_research_agent/
    ├── __init__.py                # Package exports
    ├── __main__.py                # CLI entry point (`python -m web_research_agent`)
    ├── agent.py                   # Google ADK-compliant WebResearchAgent
    ├── schemas.py                 # Pydantic schemas (Input, Source, Fact, Output, Error)
    ├── config.py                  # Environment config & provider parameters
    ├── repository.py              # ResearchEvidenceRepository interface (SurrealDB prep)
    ├── providers/
    │   ├── __init__.py
    │   ├── base.py                # Base WebResearchProvider & exceptions
    │   ├── tavily.py              # Tavily Search / Extract adapter
    │   └── anakin.py              # Anakin Scrape / Crawl / Browser adapter
    ├── services/
    │   ├── __init__.py
    │   ├── cache.py               # SHA-256 LRU cache for queries & URLs
    │   ├── tool_selector.py       # Deterministic Tool Selection Policy
    │   ├── search.py              # Multi-angle engineering query planner
    │   ├── classification.py      # Source type classifier
    │   ├── authority.py           # Heuristic authority scoring engine
    │   ├── deduplication.py       # Canonical URL & content fingerprint deduplicator
    │   ├── ranking.py             # Relevance scoring engine with verifiable reasons
    │   └── extraction.py          # Fact extraction engine with provenance
    ├── tests/
    │   ├── __init__.py
    │   ├── test_agent.py          # End-to-end agent workflow tests
    │   ├── test_tavily.py         # Tavily provider tests
    │   ├── test_anakin.py         # Anakin provider tests
    │   ├── test_tool_selector.py  # Routing policy tests
    │   ├── test_deduplication.py  # Deduplication tests
    │   ├── test_classification.py # Classification & authority tests
    │   ├── test_ranking.py        # Relevance scoring tests
    │   ├── test_extraction.py     # Fact provenance tests
    │   └── test_cli.py            # CLI development mode tests
    └── README.md                  # This documentation
```

---

## 3. Data Contracts

### Input Schema (`WebResearchAgentInput`)

```json
{
  "project_title": "Autonomous Search and Rescue Drone",
  "project_description": "A drone using computer vision and thermal sensing to locate humans during disaster response.",
  "engineering_domain": "Robotics / UAV / Computer Vision",
  "research_objectives": [
    "thermal human detection",
    "edge inference",
    "autonomous navigation"
  ],
  "components": [
    "Jetson Orin Nano",
    "FLIR Lepton thermal camera"
  ],
  "technologies": [
    "YOLOv8",
    "ROS 2"
  ],
  "constraints": [
    "real-time inference",
    "edge deployment"
  ],
  "keywords": [
    "UAV search and rescue",
    "thermal human detection"
  ],
  "target_sources": [
    "GitHub",
    "manufacturer documentation"
  ],
  "max_sources": 20
}
```

### Output Schema (`WebResearchAgentOutput`)

```json
{
  "status": "success",
  "project": {
    "title": "Autonomous Search and Rescue Drone",
    "domain": "Robotics / UAV / Computer Vision"
  },
  "queries_used": [
    "GitHub Autonomous Search and Rescue Drone YOLO",
    "Jetson Orin Nano datasheet manufacturer documentation",
    "Jetson Orin Nano YOLO implementation example",
    "thermal camera datasheet manufacturer documentation"
  ],
  "sources_found": 12,
  "sources_selected": 2,
  "sources": [
    {
      "source_id": "src_4a78bc91",
      "title": "GitHub - thermal-drone-rescue/yolov8-ros2",
      "url": "https://github.com/thermal-drone-rescue/yolov8-ros2",
      "domain": "github.com",
      "source_type": "github_repository",
      "publisher": "GitHub",
      "relevance_score": 0.88,
      "authority_score": 0.90,
      "authority_reasons": [
        "Public engineering source code repository",
        "Verifiable Git revision control and open source history"
      ],
      "source_tool": "tavily",
      "accessed_at": "2026-08-30T06:45:00Z",
      "content_available": true
    }
  ],
  "facts": [
    {
      "fact": "NVIDIA Jetson Orin Nano delivers 40 TOPS AI performance with 6-core ARM CPU and Ampere GPU.",
      "source_id": "src_4a78bc91",
      "source_url": "https://developer.nvidia.com/embedded/jetson-orin-nano",
      "extraction_method": "tavily",
      "confidence": 0.95,
      "retrieved_at": "2026-08-30T06:45:00Z",
      "category": "compute"
    }
  ],
  "errors": []
}
```

---

## 4. Deterministic Tool Selection Policy

| Task Type | Target | Selected Tool | Action |
|---|---|---|---|
| Broad web search | Keywords / concepts | **Tavily Search** | Searches web indices and returns top technical candidates |
| Target webpage extraction | Known URL | **Anakin Scrape** | Performs JavaScript-rendered DOM extraction and markdown parsing |
| Multi-page documentation | Doc site base URL | **Anakin Crawl** | Recursively traverses documentation trees up to target depth |
| Vendor / Datasheet | Product URLs | **Tavily $\rightarrow$ Anakin** | Tavily discovers datasheets, Anakin parses complex vendor specs |
| Academic discovery | arXiv, papers | **Agent #1 Delegation** | Emits routing notice to `ResearchPaperAgent` (Freephdlabor) |

---

## 5. Provenance & Authority Evaluation

### Source Classification
Classifies URLs into 15 supported engineering categories:
`official_documentation`, `manufacturer`, `datasheet`, `application_note`, `github_repository`, `engineering_project`, `technical_article`, `tutorial`, `technical_blog`, `standard`, `vendor`, `product_page`, `documentation`, `forum`, `other`.

### Authority Scoring Matrix
- Standards bodies (`ieee.org`, `ietf.org`): **0.98**
- Official manufacturer docs & datasheets (`ti.com`, `st.com`, `nvidia.com`): **0.95**
- Official GitHub repositories (`github.com`): **0.90**
- Academic institution domains (`.edu`, `.ac.uk`): **0.90**
- Established technical articles: **0.80**
- Developer forums (`eevblog.com`, `reddit.com`): **0.40**

---

## 6. Environment Variables

| Variable | Default | Description |
|---|---|---|
| `TAVILY_API_KEY` | `""` | API Key for Tavily web search |
| `TAVILY_BASE_URL` | `https://api.tavily.com` | Tavily API endpoint |
| `TAVILY_TIMEOUT_SECONDS` | `15.0` | Timeout for Tavily calls |
| `ANAKIN_API_KEY` | `""` | API Key for Anakin scraper/crawler |
| `ANAKIN_BASE_URL` | `https://api.anakin.ai/v1` | Anakin API endpoint |
| `ANAKIN_TIMEOUT_SECONDS` | `20.0` | Timeout for Anakin scraping calls |
| `WEB_RESEARCH_DEFAULT_MAX_SOURCES` | `20` | Default sources returned |
| `WEB_RESEARCH_MAX_SOURCES_CAP` | `50` | Maximum source cap |
| `WEB_RESEARCH_CACHE_ENABLED` | `true` | Enable/disable query cache |
| `WEB_RESEARCH_CACHE_TTL` | `3600` | In-memory cache TTL in seconds |

---

## 7. Local Execution & CLI

```bash
# Live execution
python -m web_research_agent \
    --project "Autonomous Search and Rescue Drone" \
    --domain "Robotics" \
    --objective "thermal human detection" \
    --max-sources 10

# Mock test execution (offline)
python -m web_research_agent \
    --mock \
    --project "Autonomous Search and Rescue Drone" \
    --domain "Robotics" \
    --objective "thermal human detection" \
    --max-sources 5
```

---

## 8. Testing

Run all unit and integration tests:

```bash
pytest research_agents/web_research_agent/tests/ -v
```

Coverage includes:
- **Tavily adapter**: search, extract, rate limits, timeouts, auth failures
- **Anakin adapter**: scraping, crawling, JS rendering, errors
- **Tool selector**: deterministic routing and academic query delegation
- **Deduplication**: canonical URL, tracking param stripping (`utm_*`), content fingerprinting
- **Classification & Authority**: 15 source types and heuristic authority scoring
- **Relevance ranking**: scoring bounds $[0.0, 1.0]$ and verifiable reasons
- **Evidence extraction**: fact extraction and provenance retention
- **CLI test runner**: rich table rendering and fact display

---

## 9. Future Integrations

- **A2A Interface**: Exposes `web.search`, `web.extract`, `web.crawl`, `web.research`, `web.source`.
- **Bindu**: Callable wrapper boundary around `run()` and `run_sync()`.
- **ArmorIQ**: Every request supports `user_id`, `project_id`, `agent_id`, `parent_agent_id`, `execution_id`, `authorization_context`, `tool_scope` for governance and delegation.
- **SurrealDB**: `ResearchEvidenceRepository` (`repository.py`) defines future persistence methods (`save_source`, `save_fact`, `save_project_source_relationship`, `get_project_sources`, `get_source_facts`).
