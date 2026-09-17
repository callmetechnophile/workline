# Environment & Configuration Audit Report: ArmourFlow AI / WorkflowGuide AI

**Platform Version:** `1.0.0 (development)`  
**Audit Timestamp:** `2026-09-06T03:30:00Z`  
**Security Classification:** Non-Confidential Architecture Audit (Zero Secrets Exposed)

---

## 1. Executive Summary

This report establishes the complete inventory, purpose, security classification, consumer mapping, and validation state of all platform environment variables within the unified **ArmourFlow AI / WorkflowGuide AI** engineering platform.

The configuration layer enforces strict adherence to the **Zero-Fabrication** and **Zero-Secret-Leakage** platform invariants:
- Secrets (API keys, secret keys, recovery phrases) are strictly redacted in all diagnostic outputs, CLI panels, log messages, and persistent artifacts.
- No dummy credentials or fake engineering values are injected.
- Missing optional external integrations fall back transparently to explicit offline/deterministic degradation paths (`DATA_INSUFFICIENT`, `OFFLINE_FALLBACK`, `DISABLED`) rather than halting execution or fabricating results.

---

## 2. Platform Environment Variables Matrix

| Variable Name | Categorized Subsystem | Purpose | Required / Optional | Consuming Subsystem(s) | Secret / Non-Secret | Validation Rule | Runtime Status |
|---|---|---|---|---|---|---|---|
| `APP_ENV` | Application | Runtime operational mode (`development`, `staging`, `production`) | Required | Platform Settings, Diagnostics | Non-Secret | Must be valid `EnvironmentMode` enum | `development` (Active) |
| `APP_NAME` | Application | Canonical platform application name | Required | Platform Settings, CLI, Logs | Non-Secret | Non-empty string | `ArmourFlow AI` (Active) |
| `APP_VERSION` | Application | Canonical platform semver version | Required | Platform Settings, CLI, Harness | Non-Secret | Valid semver format | `1.0.0` (Active) |
| `PORT` | Application | HTTP/gRPC listening port for services | Optional | Platform Settings, Web Server | Non-Secret | Integer (1–65535) | `10000` (Configured) |
| `HOST` | Application | Network interface binding host | Optional | Platform Settings, Web Server | Non-Secret | Valid IP or hostname string | `0.0.0.0` (Configured) |
| `LOG_LEVEL` | Application | Application logging granularity | Optional | Loguru, Logging Config | Non-Secret | One of `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` (Active) |
| `CLI_OUTPUT_FORMAT` | ArmourFlow CLI | Terminal output formatter style | Optional | ArmourFlow CLI (`armourflow.cli`) | Non-Secret | One of `rich`, `json`, `plain` | `rich` (Active) |
| `CLI_DEFAULT_PROJECT`| ArmourFlow CLI | Fallback project scope for CLI commands | Optional | ArmourFlow CLI (`armourflow.cli`) | Non-Secret | Non-empty alphanumeric string | `default` (Active) |
| `ADK_ENABLED` | Google ADK | Flag enabling Google ADK orchestration | Optional | Google ADK Runtime, Fabric Adapter | Non-Secret | Boolean (`true`/`false`) | `true` (Active) |
| `ADK_RUNTIME` | Google ADK | ADK runtime engine identifier | Optional | Google ADK Runtime (`GoogleADKRuntime`) | Non-Secret | Non-empty string | `google_adk_v1` (Active) |
| `CONTROL_FABRIC_ENDPOINT` | Control Fabric | Internal IPC/event bus URI for Control Fabric | Required | Agent Control Fabric, Router, Dispatcher | Non-Secret | Valid URI string (`internal://` or `http://`) | `internal://control-fabric` (Active) |
| `CONTROL_FABRIC_TIMEOUT` | Control Fabric | Max seconds allowed for fabric task execution | Optional | Agent Control Fabric (`AgentControlFabric`) | Non-Secret | Positive float | `60.0`s (Active) |
| `SURREALDB_URL` | Data & State | SurrealDB WebSocket/RPC connection URL | Required | SurrealDB Client, Repositories | Non-Secret | Valid `ws://`, `wss://`, `http://`, `https://` | `ws://localhost:8000/rpc` (Active Fallback) |
| `SURREALDB_NAMESPACE` | Data & State | SurrealDB tenant isolation namespace | Required | SurrealDB Client (`PlatformDatabaseClient`) | Non-Secret | Non-empty alphanumeric string | `workline` (Active) |
| `SURREALDB_DATABASE` | Data & State | SurrealDB active graph database name | Required | SurrealDB Client (`PlatformDatabaseClient`) | Non-Secret | Non-empty alphanumeric string | `workline` (Active) |
| `SURREALDB_USER` | Data & State | SurrealDB administrative user name | Required | SurrealDB Client (`PlatformDatabaseClient`) | Non-Secret | Non-empty string | `root` (Configured) |
| `SURREALDB_PASSWORD` | Data & State | SurrealDB database authentication password | Required | SurrealDB Client (`PlatformDatabaseClient`) | **Secret** | Masked / Redacted; non-empty | Masked (Configured) |
| `AWS_REGION` | Amazon Bedrock | AWS default operational region | Required | Bedrock Provider, AWS SDK | Non-Secret | Valid AWS region string | `us-east-1` (Active) |
| `BEDROCK_REGION` | Amazon Bedrock | Amazon Bedrock runtime inference region | Required | Bedrock Provider (`BedrockModelProvider`) | Non-Secret | Valid AWS region string | `us-east-1` (Active) |
| `BEDROCK_MODEL_ID` | Amazon Bedrock | Primary model ID for agent reasoning | Optional | Bedrock Provider (`BedrockModelProvider`) | Non-Secret | Bedrock model identifier | `anthropic.claude-3-5-sonnet-20241022-v2:0` (Active) |
| `BEDROCK_FAST_CODE_MODEL_ID` | Amazon Bedrock | Low-latency model ID for quick analysis | Optional | Bedrock Provider (`BedrockModelProvider`) | Non-Secret | Bedrock model identifier | `anthropic.claude-3-5-haiku-20241022-v1:0` (Active) |
| `BEDROCK_REASONING_MODEL_ID` | Amazon Bedrock | High-depth model ID for complex trade studies | Optional | Bedrock Provider (`BedrockModelProvider`) | Non-Secret | Bedrock model identifier | `anthropic.claude-3-5-sonnet-20241022-v2:0` (Active) |
| `BEDROCK_EMBEDDING_MODEL_ID` | Amazon Bedrock | Vector embedding model for knowledge graph | Optional | Bedrock Provider (`BedrockModelProvider`) | Non-Secret | Bedrock model identifier | `amazon.titan-embed-text-v2:0` (Active) |
| `A2A_ENABLED` | A2A Protocol | Inter-agent direct communication bridge flag | Optional | A2A Bridge (`A2AInteroperabilityBridge`) | Non-Secret | Boolean (`true`/`false`) | `true` (Active) |
| `A2A_ENDPOINT` | A2A Protocol | A2A internal messaging router endpoint | Optional | A2A Bridge (`A2AInteroperabilityBridge`) | Non-Secret | Valid URI string | `internal://a2a-gateway` (Active) |
| `A2A_TIMEOUT` | A2A Protocol | Inter-agent call timeout in seconds | Optional | A2A Bridge (`A2AInteroperabilityBridge`) | Non-Secret | Positive float | `30.0`s (Active) |
| `BINDU_ENABLED` | Bindu Gateway | External decentralized agent protocol gateway | Optional | Bindu Adapter (`BinduExternalAdapter`) | Non-Secret | Boolean (`true`/`false`) | `true` (Active) |
| `BINDU_ENDPOINT` | Bindu Gateway | Bindu network gateway API endpoint | Optional | Bindu Adapter (`BinduExternalAdapter`) | Non-Secret | Valid HTTP/HTTPS URI | `http://localhost:8080/bindu` (Active) |
| `BINDU_API_KEY` | Bindu Gateway | Bindu payment & identity authentication key | Optional | Bindu Adapter (`BinduExternalAdapter`) | **Secret** | Masked / Redacted string | Not Configured (Optional) |
| `TAVILY_ENABLED` | External Search | Web extraction and real-time research search | Optional | Central Tavily Client (`CentralTavilyClient`) | Non-Secret | Boolean (`true`/`false`) | `true` (Active) |
| `TAVILY_API_KEY` | External Search | Tavily REST API research authentication key | Optional | Central Tavily Client (`CentralTavilyClient`) | **Secret** | Masked / Redacted string | Offline Fallback (Active) |
| `TAVILY_BASE_URL` | External Search | Tavily API endpoint | Optional | Central Tavily Client (`CentralTavilyClient`) | Non-Secret | Valid HTTPS URI | `https://api.tavily.com` (Configured) |
| `TAVILY_TIMEOUT_SECONDS` | External Search | Timeout for web research requests | Optional | Central Tavily Client (`CentralTavilyClient`) | Non-Secret | Positive float | `15.0`s (Active) |
| `FREEPHDLABOR_ENABLED` | Academic Search | Research-paper and literature discovery | Optional | Central FreePHDLabor Client | Non-Secret | Boolean (`true`/`false`) | `true` (Active) |
| `FREEPHDLABOR_BASE_URL` | Academic Search | FreePHDLabor API endpoint | Optional | Central FreePHDLabor Client | Non-Secret | Valid HTTPS URI | `https://api.freephdlabor.com/v1` (Configured) |
| `FREEPHDLABOR_API_KEY` | Academic Search | Academic paper discovery API key | Optional | Central FreePHDLabor Client | **Secret** | Masked / Redacted string | Not Configured (Optional) |
| `FREEPHDLABOR_TIMEOUT_SECONDS`| Academic Search| Paper discovery timeout in seconds | Optional | Central FreePHDLabor Client | Non-Secret | Positive float | `15.0`s (Active) |
| `ANAKIN_ENABLED` | Deep Scraping | Anakin deep web crawler service flag | Optional | Central Anakin Client (`CentralAnakinClient`) | Non-Secret | Boolean (`true`/`false`) | `false` (Disabled by policy) |
| `ANAKIN_BASE_URL` | Deep Scraping | Anakin crawling gateway endpoint | Optional | Central Anakin Client (`CentralAnakinClient`) | Non-Secret | Valid HTTPS URI | `https://api.anakin.ai/v1` (Configured) |
| `ANAKIN_API_KEY` | Deep Scraping | Anakin authentication key | Optional | Central Anakin Client (`CentralAnakinClient`) | **Secret** | Masked / Redacted string | Not Configured (Optional) |
| `ANAKIN_TIMEOUT_SECONDS` | Deep Scraping | Anakin crawling request timeout | Optional | Central Anakin Client (`CentralAnakinClient`) | Non-Secret | Positive float | `20.0`s (Configured) |
| `ANAKIN_MCP_ENABLED` | Deep Scraping | Anakin Model Context Protocol server bridge | Optional | Central Anakin Client (`CentralAnakinClient`) | Non-Secret | Boolean (`true`/`false`) | `false` (Disabled by policy) |
| `ARMORIQ_ENABLED` | Security & Auth | ArmorIQ security & authorization enforcement | Required | ArmorIQ Boundary (`ArmorIQBoundary`) | Non-Secret | Boolean (`true`/`false`) | `true` (Enforcing) |
| `ARMOURIQ_BASE_URL` | Security & Auth | ArmorIQ authorization server URL | Optional | ArmorIQ Boundary (`ArmorIQBoundary`) | Non-Secret | Valid HTTPS URI | `https://api.armouriq.io` (Configured) |
| `ARMORIQ_SECRET_KEY` | Security & Auth | ArmorIQ tenant cryptographic signature key | Optional | ArmorIQ Boundary (`ArmorIQBoundary`) | **Secret** | Masked / Redacted string | Masked (Configured) |
| `ARMOURIQ_API_KEY` | Security & Auth | ArmorIQ API access key | Optional | ArmorIQ Boundary (`ArmorIQBoundary`) | **Secret** | Masked / Redacted string | Masked (Configured) |
| `HARNESS_ENABLED` | Benchmark Evals | Automated evaluation harness active flag | Optional | Universal Evaluation Harness (`UniversalEvaluationHarness`) | Non-Secret | Boolean (`true`/`false`) | `true` (Active) |
| `HARNESS_ENDPOINT` | Benchmark Evals | Harness execution coordinator endpoint | Optional | Universal Evaluation Harness (`UniversalEvaluationHarness`) | Non-Secret | Valid URI string | `internal://harness` (Active) |
| `HARNESS_API_KEY` | Benchmark Evals | Evaluation benchmark reporter API key | Optional | Universal Evaluation Harness (`UniversalEvaluationHarness`) | **Secret** | Masked / Redacted string | Not Configured (Optional) |

---

## 3. Secret Masking & Protection Verification

1. **CLI Diagnostics:** Running `python -m armourflow.cli system diagnostics` displays 12 diagnostic checks. Every secret key is strictly masked (`[green]CONFIGURED[/] (Redacted)` or `[yellow]NOT_CONFIGURED[/]`).
2. **Persistence Guarantee:** No plain-text API keys or credentials are written to SurrealDB nodes or cached graph state.
3. **Template Standardization:** The repository root `.env.example` provides complete, non-sensitive default values matching the 13 categories defined above.
