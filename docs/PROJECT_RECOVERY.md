# WORKLINE Project Recovery & Backup

## Overview

WORKLINE provides robust, zero-loss project preservation and disaster recovery through portable `.wlipjt` archives.
Backups can be generated locally via `wg backup` or exported from the WORKLINE web platform.

---

## The Recovery Pipeline

```
  ┌────────────────────────────────────────────────────────┐
  │              Input Package (.wlipjt)                   │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │   Step 1: Cryptographic Verification (PackageInspector)│
  │   • Verifies ZIP structure                             │
  │   • Validates SHA-256 digests in checksums.toon        │
  │   • Checks manifest.toon schema version                │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │   Step 2: Unpacking & Ingestion (ImportService)         │
  │   • Strategies: `restore` (overwrite), `merge`, `new`  │
  │   • Reconstitutes .wl directory structure              │
  │   • Regenerates README.wl and manifest.wl              │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │   Step 3: Service & Index Health Check                 │
  │   • Checks local Moss index status                     │
  │   • Probes Qdrant vector collection state              │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │   Step 4: Optional Retrieval Rebuild                   │
  │   • Prompts user or executes --rebuild-index           │
  │   • Re-indexes all .wl files into .wl/index/           │
  └────────────────────────────────────────────────────────┘
```

---

## Security & Sanitization

Before an archive is written, `SecuritySanitizer` automatically scrubs sensitive values:
- AWS access keys and secret keys (`AKIA...`)
- Bearer tokens and JWT authorization headers
- Third-party API keys (Octopart, Nexar, OpenAI, Anthropic, LiveKit)
- Database credentials and connection passwords

---

## Common Recovery Scenarios

### Restoring to an Alternate Directory
```bash
wg restore backup_2026-09-23.wlipjt --target ~/Projects/bms-restored --yes
```

### Full Re-index on Restore
```bash
wg restore backup.wlipjt --rebuild-index
```
