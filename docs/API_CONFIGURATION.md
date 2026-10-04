# WORKLINE External API Configuration & Credential Management
=============================================================
**Specification Version: 1.0**  
**Classification: Security & Configuration Guide**

---

## 1. Overview

While WORKLINE is fundamentally local-first, optional external services enhance capabilities for remote LLM inference, realtime audio copilot sessions, isolated remote sandboxes, and web research.

All external credentials are administered via `APICredentialManager` and accessed through the unified CLI command:

```bash
wline apis
# or
wline --apis
```

---

## 2. Zero-Secrets Invariant

WORKLINE enforces strict rules regarding credentials:
1. **Never in `.wl` Projects:** No `.env`, secret key, password, or token is ever written to project directories, `.wl` metadata, or backups.
2. **Never in Databases or Vector Indexes:** API keys are never embedded in SurrealDB graph nodes or Qdrant vector collections.
3. **Secure Local Storage:** Credentials are saved in user-scoped platform configurations (`~/.workline/credentials.json` or OS keyring) with restricted permissions (0600 on POSIX).
4. **Automatic Environment Injection:** Upon running `wline <command>`, `APICredentialManager` injects configured credentials into the active process memory environment.

---

## 3. Supported Providers & Configuration Keys

| Provider | Purpose | Configuration Keys |
| :--- | :--- | :--- |
| **Amazon Bedrock** | Primary Foundation Model Inference | `AWS_ACCESS_KEY_ID`<br>`AWS_SECRET_ACCESS_KEY`<br>`AWS_REGION`<br>`BEDROCK_MODEL_ID` |
| **NVIDIA NIM** | High-performance GPU LLM Fallback | `NVIDIA_API_KEY`<br>`NVIDIA_BASE_URL` |
| **GitHub** | Repository synchronization & PR tracking | `GITHUB_TOKEN`<br>`GITHUB_ENTERPRISE_URL` |
| **LiveKit** | Realtime voice & copilot streaming | `LIVEKIT_URL`<br>`LIVEKIT_API_KEY`<br>`LIVEKIT_API_SECRET` |
| **Agent37** | Isolated remote sandbox execution | `AGENT37_API_KEY`<br>`AGENT37_ENDPOINT` |
| **Web Research / TinyFish** | Web search and technical paper retrieval | `TINYFISH_API_KEY`<br>`TINYFISH_ENDPOINT` |

---

## 4. Commands

### Interactive Configuration Wizard
```bash
wline apis
```
Launches an interactive prompt to inspect, add, or update provider credentials.

### Check Status
```bash
wline apis status
```
Displays a sanitized status table of all configured integrations without printing secrets.

### Reset / Purge Credentials
```bash
wline apis reset --provider bedrock
# Or reset all:
wline apis reset --all
```
Securely deletes stored credentials from the local config.
