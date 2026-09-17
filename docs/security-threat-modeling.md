# WorkflowGuide AI: Security & Threat Modeling Architecture (Agent #22)

## 1. System Security Overview
WorkflowGuide AI employs a defense-in-depth architecture across 22 collaborative agents. Agent #22 (`SecurityThreatModelingAgent`) provides continuous threat intelligence, attack surface mapping, and automated regression detection.

## 2. Trust Boundaries & Security Zones
- **Public Ingress:** Public APIs and Web UI separated by TLS 1.3, rate-limiting, and HMAC-SHA256 JWT tokens.
- **Control Fabric Boundary:** Dispatches tasks to worker agents with strict Pydantic contract validation and correlation tracking.
- **Privileged Execution Boundary:** Governed by ArmorIQ cryptographic delegation tokens. No agent may execute shell commands or write to disk without validated capability scopes.
- **Multi-Tenant Database Boundary:** SurrealDB queries strictly scoped with `WHERE project_id = $project_id AND team_id = $team_id`.

## 3. Agentic AI Threats & Safeguards
1. **Indirect Prompt Injection:** Untrusted documents and search results isolated in non-instruction frames.
2. **A2A Message Spoofing:** Ephemeral session tokens validated against `AgentRegistry`.
3. **Secrets Leakage:** Automated regex sanitization in logging middleware.
4. **Excessive Agency:** Static and dynamic least-privilege scoping via ArmorIQ.
