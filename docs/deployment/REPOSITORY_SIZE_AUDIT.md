# Workline Repository Size & Disk Footprint Audit

**Audit Date**: 2026-08-23  
**Measured Repository Total**: **882.16 MB**  

---

## 1. Directory Breakdown on Local Disk

| Path / Directory | Measured Size | Should Git Track? | Should Deployment Include? | Description / Category |
| :--- | :--- | :--- | :--- | :--- |
| **`.git/`** | 3.19 MB | NO (Git Metadata) | NO | Local Git object store & packfiles (`2.55 MiB` pack). |
| **`node_modules/` (root)** | 494.55 MB | **NO** (`.gitignore`) | NO | Workspace tooling, Turbopack, ESLint, TypeScript devDeps. |
| **`frontend/node_modules/`** | 2.18 MB | **NO** (`.gitignore`) | NO | Inset workspace metadata links. |
| **`backend/.venv/`** | 345.28 MB | **NO** (`.gitignore`) | NO (Rebuilt in container) | Local Python 3.11 virtual environment & site-packages. |
| **`backend/` (Source & Data)** | 17.36 MB | **YES** | **YES (Backend Service)** | FastAPI endpoints, agents, PINN, PCB, graph modules, fonts. |
| **`frontend/src/` & `public/`** | 1.57 MB | **YES** | **YES (Vercel Frontend)** | Next.js 16 App Router pages, components, styles, static SVGs. |
| **`frontend/.next/`** | 15.00 MB | **NO** (`.gitignore`) | **YES (Vercel Build Output)**| Compiled standalone server output (12.68 MB) & static assets (1.39 MB). |
| **`cli/`** | 0.54 MB | **YES** | **YES (CLI Tooling)** | `wline` Typer-based developer CLI. |
| **`tests/`** | 1.78 MB | **YES** | NO (CI Only) | 302 unit, integration, and safety test suites. |
| **`docs/`** | 0.20 MB | **YES** | NO (Documentation) | Design systems, architecture specifications, deployment plans. |
| **`podman/`** | 0.01 MB | **YES** | **YES (Local Dev Ops)** | `compose.yml` for SurrealDB and Qdrant container orchestration. |

---

## 2. Git Tracking Verification

- **Total Tracked Files in Git**: 1,588 files
- **Tracked `node_modules` Files**: **0** (Cleanly ignored via `.gitignore`)
- **Tracked `.venv` Files**: **0** (Cleanly ignored via `.gitignore`)
- **Tracked `.next` Files**: **0** (Cleanly ignored via `.gitignore`)
- **Git History Pack Size**: **2.55 MiB** (Zero large binary debt in history).
