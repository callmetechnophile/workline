# Local Moss Semantic Retrieval Integration in WORKLINE

**System Architecture Document**  
**Classification:** Core System Contract & Architecture Specification

---

## 1. Executive Summary & Core Principle

WORKLINE uses **Moss** as the on-device semantic retrieval layer for engineering project filesystems (`.wl`). 

> [!IMPORTANT]
> **Fundamental Principle:**
> - The **`.wl` filesystem is the single source of truth**.
> - **Local Moss is derived state**.
> - **Zero cloud search APIs**: Project files and retrieval queries remain entirely on the user's local device.
> - If the local Moss index (`.wl/index/`) is deleted, zero project information is lost. Running `wg index --rebuild` fully reconstructs the retrieval layer.

---

## 2. Architecture Diagram

```text
                    USER DEVICE
====================================================
                 WORKLINE CLI (`wg`)
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
   .WL FILESYSTEM   LOCAL MOSS   LOCAL AGENT
        │             │             │
        │             │             ├── MCP
        │             │             ├── Tools
        │             │             └── LiveKit
        │             │
        │             ▼
        │      Local Retrieval
        │       (sub-10ms)
        ▼
 Engineering Project
 Context / State
====================================================
```

### Retrieval Pipeline

```text
User / Voice Query
        ↓
 WORKLINE Agent / LiveKit
        ↓
  ProjectRetriever
        ↓
  LocalMossAdapter
        ↓
 Local Moss In-Memory Index (.wl/index/)
        ↓
 Bounded Engineering Context + Provenance Citations
```

---

## 3. Why Moss?

Engineering projects contain multi-domain, heterogeneous knowledge:
- Parametric component specifications (voltage, junction temperature, ripple)
- Bills of Materials (BOM) with quantities and supplier part numbers
- Complex architectural trade-offs (ADRs)
- Verifiable technical requirements and compliance limits

Traditional keyword search fails when an engineer asks for an *"orientation sensor"*, but the component dossier specifies an *"MPU-6050 6-Axis MotionTracking IMU"*.

Moss provides:
1. **Sub-10ms Local Retrieval**: In-process execution with zero network round trips.
2. **Hybrid Search**: Combines BM25 lexical tokenization with dense semantic vector scoring.
3. **Deterministic Boosting**: Exact MPN, task ID, and component category matches are automatically prioritized.
4. **Metadata Filtering**: Scopes queries by engineering resource type (`component`, `requirement`, `architecture`, `decision`, `bom`, `task`).

---

## 4. On-Device Storage & Metadata

### 4.1 Derived Local Index (`.wl/index/`)
The local index files reside inside `.wl/index/`:
- `records.json`: Serialized normalized `EngineeringRecord` models.
- `index.json`: Vector embeddings, term frequencies, and inverted index mappings.

This directory is strictly excluded from version control and exports via `.gitignore` and `.wlignore`.

### 4.2 Index Metadata (`.wl/moss.wl`)
The project metadata tracks index health:
```yaml
moss:
  enabled: true
  index_name: workline_proj_auto
  schema_version: 1
  status: READY
  document_count: 1284
  runtime: local
  indexed_at: '2026-09-23T09:32:00Z'
  last_manifest_hash: 5f98a...
```

---

## 5. Incremental & Rebuild Indexing

### Incremental Indexing (`wg index --incremental`)
Determines changed resources by computing SHA-256 hashes against `.wl/manifest.wl`:
1. Scans project files (ignoring secrets).
2. Computes file hashes.
3. Identifies added, modified, and removed files.
4. Only reprocesses affected resources.
5. Updates `.wl/moss.wl` and `.wl/manifest.wl`.

### Clean Rebuild (`wg index --rebuild`)
1. Clears `.wl/index/`.
2. Reads `README.wl` and `.wl/manifest.wl`.
3. Traverses all declared engineering modules.
4. Extracts normalized records and builds vector/lexical indexes.
5. Verifies document count and marks status `READY`.

---

## 6. LiveKit Realtime Integration

LiveKit provides realtime voice and conversational interaction. It communicates strictly through `ProjectRetriever`:

```text
LiveKit Session → LiveKitAgentAdapter → ProjectRetriever → Local Moss
```

- LiveKit sessions maintain ephemeral conversational context (subsystem, recent query).
- Voice interactions never bypass `ProjectRetriever`.
- Voice transcripts are not stored inside project records unless explicitly saved by the user.

---

## 7. Zero-Secrets Invariant

Under no circumstances does Moss index:
- `.env`, `.env.*`
- `credentials*`
- Private keys (`*.pem`, `*.key`, `id_rsa*`)
- Authentication tokens or OAuth secrets

The filesystem scanner applies strict pattern filtering before parsing any file into retrieval memory.
