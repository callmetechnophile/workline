# Workline CLI Service & Extraction Report

**Audit Date**: 2026-08-23  
**Status**: **CLI READY**  

---

## 1. Previous vs. Current CLI Location
- **Location**: Cleanly encapsulated inside `cli/wline/` and `cli/tests/`.
- **Packaging Entrypoint**: `wline = "cli.wline.main:main"` in `pyproject.toml`.

---

## 2. Command Inventory
- **Local Lifecycle**: `init`, `project`, `git`, `status`, `version`, `snapshot`, `release`, `config`, `doctor`.
- **Remote Operations (via R1)**: `agent`, `research`, `bom`, `pcb`, `document`, `graph`, `decision`.

---

## 3. Local vs. Remote Division of Responsibility
- **Local Responsibilities**:
  - Direct creation, reading, and signing of `.wlipjt` project archives.
  - Native local Git commits, branches, and semantic version tagging.
  - Local configuration caching in `~/.workline/`.
  - Offline validation of hardware project schemas.
- **Remote Responsibilities (via R1 Gateway)**:
  - Deep datasheet crawling via Scrapling (R2).
  - Gemini 2.0 multi-agent reasoning (R2).
  - SurrealDB graph traversal and Qdrant semantic vector lookup (R3).
  - High-intensity PINN physics surrogates and thermal equations (R4).
  - Multi-supplier price resolution and x402 payment signing (R5).

---

## 4. API Contract & Security
- **Strict Gateway Route**: The CLI connects exclusively to R1 Gateway over HTTPS (`WORKLINE_API_URL`).
- **Zero Secret Leakage**: The CLI binary contains zero database credentials, private API keys, or supplier secrets.

---

## 5. Render R6 Justification & Architecture
- **Decision**: **R6 DISTRIBUTION & METADATA SERVICE**.
- **Rationale**: The interactive CLI executes on the developer's local workstation. Hosting a persistent shell session on Render is an anti-pattern. R6 provides update manifests, version resolution, and verification checksums (`backend/services/cli/main.py`).

---

## 6. Verification & Test Results
- **CLI Test Suite (`cli/tests/test_cli_standalone.py`)**: **5/5 PASSED** ✅
  - `test_cli_version_flag`: PASSED
  - `test_cli_help_flag`: PASSED
  - `test_cli_doctor_command`: PASSED
  - `test_cli_config_show`: PASSED
  - `test_r6_cli_distribution_service`: PASSED
- **Backend Full Regression (`pytest tests -q`)**: **311/311 PASSED (100%)** ✅
- **Remaining Issues**: **None**.
