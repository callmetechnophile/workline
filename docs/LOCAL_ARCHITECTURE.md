# WORKLINE Local-First Architecture

## Overview

WORKLINE employs a **local-first, cloud-capable** architecture for hardware, systems, and embedded engineering.
The architecture strictly delineates between:
1. **The Source of Truth**: The local `.wl` filesystem representation owned completely by the user.
2. **The Gateway / Doorway**: The thin `wg` CLI that manages lifecycle, bootstrapping, and local launching.
3. **The Retrieval Subsystem**: Dual-mode local intelligence (offline Moss BM25 + deterministic hashing vs. online Qdrant vector search).
4. **The Engineering Platform**: The full WORKLINE application (FastAPI backend + Next.js frontend + SurrealDB graph database).

---

## Architectural Component Topology

```
                  ┌────────────────────────────────────────┐
                  │          Developer / Engineer          │
                  └──────────────────┬─────────────────────┘
                                     │
                             (CLI / Terminal)
                                     ▼
                   ┌──────────────────────────────────────┐
                   │               wg CLI                 │
                   │        (Thin Doorway & Runner)       │
                   └──────┬──────────┬──────────┬─────────┘
                          │          │          │
         ┌────────────────┘          │          └────────────────┐
         ▼                           ▼                           ▼
┌──────────────────┐       ┌──────────────────┐       ┌────────────────────┐
│  ProjectManager  │       │ ProjectRetriever │       │   Docker Compose   │
│  & Filesystem    │       │ (Dual-Mode Engine)│      │  (Stack Orchestr)  │
└────────┬─────────┘       └─────────┬────────┘       └──────────┬─────────┘
         │                           │                           │
         │                   ┌───────┴────────┐                  │
         ▼                   ▼                ▼                  ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌───────────────────┐
│ Portable .wl FS  │ │ Local Moss   │ │ Qdrant Stack │ │ WORKLINE Services │
│ (Source of Truth)│ │ (.wl/index/) │ │ (Port 6333)  │ │ (SurrealDB, Redis,│
│                  │ │ BM25+Embeds  │ │ Vector Store │ │  API:8000, Web)   │
└──────────────────┘ └──────────────┘ └──────────────┘ └───────────────────┘
```

---

## Retrieval Modes

`ProjectRetriever` provides context retrieval for local agent interactions, tests, and CLI queries across three operational modes:

| Mode | Target | Characteristics | Fallback Behavior |
| :--- | :--- | :--- | :--- |
| `local` | `LocalMossAdapter` (`.wl/index/`) | 100% offline, zero-network, BM25 + 384-dim hash embeddings | Direct project filesystem scan if index is empty |
| `stack` | `QdrantManager` (`http://localhost:6333`) | High-capacity HNSW vector search against active container | Degrades to `local` mode if Qdrant port is unreachable |
| `auto` *(Default)* | Automatic Selection | Probes Qdrant TCP port; uses stack if live, else local Moss | Smoothly degrades to filesystem scan if needed |

---

## LLM Gateway Fallback Strategy

The `LLMGateway` (`backend.workline.llm.gateway`) guarantees that local execution never hangs due to missing external credentials:

```
[Request] ──► 1. Amazon Bedrock (Primary: Claude 3.5 Sonnet / Haiku)
                    │ (If AWS_ACCESS_KEY_ID missing or API fails)
                    ▼
              2. NVIDIA NIM (Secondary text inference via NVIDIA_API_KEY)
                    │ (If NVIDIA_API_KEY missing or API fails)
                    ▼
              3. LocalMockProvider (100% deterministic offline mock)
```

---

## LiveKit Realtime Voice Architecture

The realtime agent communication layer is powered by **LiveKit**:
- Rooms are deterministically scoped to projects: `workline-project-{project_id}`.
- Zero secrets are persisted in `.wl` files (environment variables `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET` are read at runtime).
- An offline token fallback allows local audio simulation without live LiveKit servers.
- LiveKit agents query `ProjectRetriever` directly for real-time document grounding.
