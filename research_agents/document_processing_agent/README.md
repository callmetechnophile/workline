# DocumentProcessingAgent (Agent #3)

**DocumentProcessingAgent** is Agent #3 of the WorkflowGuide AI multi-agent engineering platform. It ingests academic research papers and technical web documents collected by **ResearchPaperAgent** (Agent #1) and **WebResearchAgent** (Agent #2), and converts them into clean, structured Markdown, layout-aware semantic chunks, and verified engineering facts with strict character/page provenance, preparing them for downstream Amazon Bedrock Deep Research synthesis.

---

## 1. Architecture & Pipeline

```
PDF / HTML / Text Document
        |
        v
DocumentValidator (Format detection, size check, remote fetch)
        |
        v
Parser Layer (PyMuPDF / BeautifulSoup / TextParser)
        |
        +---> Page boundary & Layout block extraction
        +---> Header / Footer / Boilerplate cleaning
        +---> Table & Figure caption extraction
        +---> Link & Reference bibliography parsing
        |
        v
MarkdownBuilder (Normalized Markdown + `<!-- source_page: N -->` tags)
        |
        v
SemanticChunker (Section -> Subsection -> Paragraph hierarchy)
        |
        v
EngineeringEntityExtractor (MCUs, Sensors, Interfaces, Frameworks)
        |
        v
EngineeringFactExtractor & UnitNormalizer (3.3V, 500mA -> 0.5A, 240MHz -> 2.4e8Hz)
        |
        v
QualityEvaluator (Quality Score 0.0 - 1.0, OCR requirement detection)
        |
        v
DocumentProcessingOutput (Structured Evidence ready for Amazon Bedrock)
```

---

## 2. Directory Layout

```
research_agents/
└── document_processing_agent/
    ├── __init__.py                # Package exports
    ├── __main__.py                # CLI entry point (`python -m document_processing_agent`)
    ├── agent.py                   # Google ADK-compliant DocumentProcessingAgent
    ├── schemas.py                 # Pydantic schemas (Input, Output, Section, Chunk, Fact, Entity, Table, Metadata)
    ├── config.py                  # Settings (chunk sizes, OCR threshold, download timeouts)
    ├── repository.py              # ProcessedDocumentRepository interface (SurrealDB prep)
    ├── parsers/
    │   ├── __init__.py
    │   ├── base.py                # Abstract BaseDocumentParser & parser exceptions
    │   ├── pdf_parser.py          # PyMuPDF-based layout, page, table, and metadata extractor
    │   ├── html_parser.py         # BeautifulSoup boilerplate-stripped HTML extractor
    │   └── text_parser.py         # Plain text and raw Markdown parser
    ├── services/
    │   ├── __init__.py
    │   ├── validator.py           # Document type, path/URL validation, and fetcher
    │   ├── markdown_builder.py    # Markdown synthesizer with `<!-- source_page: N -->` annotations
    │   ├── chunker.py             # Semantic hierarchical section/paragraph chunker
    │   ├── entity_extractor.py    # Engineering entity extractor (MCUs, sensors, interfaces)
    │   ├── fact_extractor.py      # Technical statement extractor with provenance
    │   ├── unit_normalizer.py     # Unit detection & normalization (V, mA, MHz, °C, etc.)
    │   └── quality_evaluator.py   # Document quality score evaluator and OCR detector
    ├── tests/
    │   ├── __init__.py
    │   ├── test_pdf_parser.py     # PyMuPDF page boundary & metadata tests
    │   ├── test_html_parser.py    # HTML boilerplate cleaning & hierarchy tests
    │   ├── test_markdown.py       # Markdown synthesis & page annotation tests
    │   ├── test_chunker.py        # Semantic chunking & bounding tests
    │   ├── test_entities.py       # Engineering entity extraction tests
    │   ├── test_facts.py          # Fact extraction & unit normalization tests
    │   ├── test_quality.py        # Quality scoring & OCR requirement detection tests
    │   ├── test_agent.py          # End-to-end agent pipeline tests
    │   └── test_cli.py            # CLI test runner tests
    └── README.md                  # This documentation
```

---

## 3. Data Contracts

### Input Schema (`DocumentProcessingInput`)

```json
{
  "document_id": "paper_sar_001",
  "source_url": "https://arxiv.org/pdf/2405.10123.pdf",
  "local_path": null,
  "document_type": "pdf",
  "title": "Thermal Human Detection on Edge UAVs",
  "project_id": "proj_uav_sar",
  "source_agent": "research_paper_agent",
  "metadata": {}
}
```

### Output Schema (`DocumentProcessingOutput`)

```json
{
  "status": "success",
  "document_id": "paper_sar_001",
  "metadata": {
    "title": "Thermal Human Detection on Edge UAVs",
    "authors": ["Alice Smith", "Bob Jones"],
    "page_count": 8,
    "document_type": "pdf",
    "doi": "10.1109/TRO.2024.001"
  },
  "markdown": "# Thermal Human Detection on Edge UAVs\n\n<!-- source_page: 1 -->\n\n## Abstract\n...",
  "sections": [
    {
      "section_title": "Methodology",
      "level": 2,
      "page_start": 3,
      "page_end": 4,
      "text": "..."
    }
  ],
  "chunks": [
    {
      "chunk_id": "paper_sar_001_chunk_3",
      "document_id": "paper_sar_001",
      "section": "Methodology",
      "page_start": 3,
      "page_end": 4,
      "character_start": 4820,
      "character_end": 6912,
      "token_estimate": 420,
      "text": "..."
    }
  ],
  "entities": [
    {
      "name": "ESP32-S3",
      "category": "microcontroller",
      "page_number": 3,
      "context_snippet": "The system utilizes an ESP32-S3 microcontroller..."
    }
  ],
  "facts": [
    {
      "fact": "The system utilizes an ESP32-S3 microcontroller operating at 3.3 V supply voltage.",
      "entity": "microcontroller",
      "attribute": "operating_voltage",
      "value": "3.3 V",
      "normalized_value": 3.3,
      "normalized_unit": "V",
      "source_document": "paper_sar_001",
      "page": 3,
      "confidence": 0.96
    }
  ],
  "quality_score": 0.94,
  "quality_warnings": [],
  "errors": []
}
```

---

## 4. Key Capabilities

1. **PyMuPDF Page Boundaries**: Extracts text page-by-page, strictly preserving page boundaries (`Page 1`, `Page 2`) instead of flattening into an anonymous text blob.
2. **Page Provenance Annotations**: Every section in Markdown is stamped with `<!-- source_page: N -->`, and every chunk / fact retains exact `page_start`, `page_end`, `character_start`, and `character_end`.
3. **Boilerplate-Stripped HTML Parsing**: Automatically removes navigation menus, cookie banners, tracking scripts, and sidebars.
4. **Hierarchical Semantic Chunking**: Respects Section $\rightarrow$ Subsection $\rightarrow$ Paragraph Group boundaries rather than arbitrary token slicing.
5. **Engineering Entity & Fact Extraction**: Detects microcontrollers, sensors, actuators, protocols, operating voltages, clock speeds, and current limits.
6. **Physical Unit Normalization**: Converts engineering quantities ($500\text{ mA} \rightarrow 0.5\text{ A}$, $240\text{ MHz} \rightarrow 2.4 \times 10^8\text{ Hz}$, $24\text{ V}$) without altering source text.
7. **Document Quality Scoring & OCR Detection**: Computes document health score ($0.0 - 1.0$) and returns `"status": "ocr_required"` if text extraction yields insufficient characters on scanned/image-only PDFs.

---

## 5. Local Execution & CLI

```bash
# Run on local file
python -m document_processing_agent --input ./path/to/paper.pdf --id paper_001

# Run on sample demo document
python -m document_processing_agent --demo
```

---

## 6. Testing

Run all unit and integration tests:

```bash
pytest research_agents/document_processing_agent/tests/ -v
```

---

## 7. Future Downstream Integrations

- **Amazon Bedrock Deep Research Agent**: Ingests semantic chunks and structured engineering facts for synthesis and trade study reasoning.
- **A2A Interface**: Exposes `document.process`, `document.chunk`, `document.extract_facts`.
- **SurrealDB**: `ProcessedDocumentRepository` (`repository.py`) defines methods for storing processed documents, chunks, and facts.
