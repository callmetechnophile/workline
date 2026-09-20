# Security & Compliance Model: WorkflowGuide AI / ArmourFlow AI

## Overview
This document outlines the security controls, authentication safeguards, cryptographic delegation invariants, and data protection architecture of the WorkflowGuide AI / ArmourFlow AI platform.

---

## 1. Authentication & RBAC (Amazon Cognito)
- **Token Verification:** RS256 JWT tokens issued by Amazon Cognito are strictly verified against the Cognito JWKS endpoint (`COGNITO_JWKS_URL`) with key ID (`kid`) validation and automated 1-hour TTL cache refresh.
- **Production Guardrail:** Unverified token fallbacks are disabled in production environments (`WORKLINE_ALLOW_DEV_AUTH=false`). Any expired, forged, or unauthenticated request returns HTTP 401 Unauthorized.
- **RBAC Roles:** Built-in roles include `engineer`, `reviewer`, `admin`, and `system:admin`. Role claims are verified per endpoint via FastAPI dependencies.

---

## 2. Agent Governance & Delegation (ArmorIQ SDK)
- **Zero-Trust Agent Interactions:** No agent can invoke tools without an HMAC-signed cryptographic receipt traceable back to an authorized user intent.
- **Scope Isolation:** Sub-agents operate strictly within delegated tool subsets. Scope escalations are trapped immediately as `ScopeViolationError`.
- **Auditability:** Every delegation and execution attempt generates an audit record dispatched to AWS CloudWatch Metrics (`ArmorIQPolicyViolations`) and Amazon EventBridge (`PolicyViolation` / `AgentDelegated`).

---

## 3. Data Protection & Encryption
- **Data at Rest:**
  - Amazon S3: Server-side encryption via AWS Key Management Service (`SSE-KMS`).
  - Amazon DynamoDB: Encrypted at rest using AWS owned keys.
  - SurrealDB & Qdrant: TLS encryption on all intra-VPC connections; encrypted storage volumes.
- **Data in Transit:**
  - HTTPS / TLS 1.3 enforced across Amazon CloudFront, API Gateway, and backend services.
  - Presigned URLs for S3 downloads/uploads expire within 900 seconds (15 minutes).

---

## 4. Secret & Credential Safety
- API keys, database passwords, and private tokens are strictly injected via environment variables and AWS Secrets Manager / Parameter Store.
- Hardcoded keys are prohibited. `.env.example` provides redacted templates for deployment.
