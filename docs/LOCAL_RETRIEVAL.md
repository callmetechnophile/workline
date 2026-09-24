# WORKLINE Local Retrieval Subsystem (Moss)

## Overview

**Moss** is the local semantic retrieval engine embedded directly within the WORKLINE CLI.
Moss is **derived and ephemeral**: it indexes the local `.wl` filesystem to enable sub-second keyword and semantic search without requiring cloud API calls or a running database.

---

## Architectural Principles

1. **The User Owns the Data**: All project data lives in human-readable `.wl` text files.
2. **Local First**: Moss runs entirely in-process using Python standard libraries and lightweight zero-dependency algorithms.
3. **No Cloud Dependencies**: Moss requires **no** external vector cloud APIs or heavy deep-learning model downloads.
4. **Graceful Fallback**: If the Moss index has not been initialized or is damaged, queries automatically fall back to direct token-containment filesystem scans.

---

## Technical Architecture

```
User Query ("12V regulator 2A")
            │
            ▼
┌──────────────────────────────────────────────┐
│               ProjectRetriever               │
└──────────────────────┬───────────────────────┘
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
┌─────────────────────────┐ ┌─────────────────────────┐
│     LocalMossAdapter    │ │   Filesystem Fallback   │
│       (.wl/index/)      │ │ (Used if index missing) │
├─────────────────────────┤ └─────────────────────────┘
│ • BM25 Inverted Index   │
│ • LocalEmbeddingProvider│
│   (384-dim hash vectors)│
│ • Deterministic Boost   │
│   (MPN, Title, Req ID)  │
└─────────────────────────┘
```

---

## Deterministic Boosting

To ensure high-precision results for engineering workflows, `ProjectRetriever` applies deterministic score boosts:

- **Exact MPN Match**: Boosted to `0.98`
- **Title Substring Match**: Boosted to `0.95`
- **Identifier Match** (e.g. `REQ-001`, `ADR-004`): Boosted to `0.99`

---

## Embedding Provider Details

`LocalEmbeddingProvider` generates normalized 384-dimensional dense vectors using deterministic token hash projection and log-distance decay:
- **Zero API Keys**: Runs locally in Python.
- **Reproducible**: Identical text always yields identical vectors across all platforms.
- **Compatible**: Follows the same vector dimension (384d) as standard edge transformers (`all-MiniLM-L6-v2`).
