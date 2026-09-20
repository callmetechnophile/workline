# Workline Security & Vulnerability Assessment

**Document ID:** `WORKLINE-DEBUG-17`  
**Execution Timestamp:** 2026-09-18T01:14:00+05:30  
**Scope:** Authentication, Secrets, CORS, Input Validation  

---

## 1. Vulnerability Findings

### SEC-01: Unverified JWT Signature Fallback (Severity: HIGH)
- **Location:** `backend/auth.py:45-50`
- **Details:** When JWKS verification fails or is unreachable, the auth handler catches the exception and falls back to accepting `sub` claim from unverified token.
- **Reproduction:** Base64 header + payload with `"sub": "attacker"` and dummy signature returned HTTP 200 / user context.
- **Status:** **CONFIRMED VULNERABILITY**. Requires immediate patch to reject unverified tokens in non-local environments.

### SEC-02: Overly Permissive CORS Policy (Severity: MEDIUM)
- **Location:** `backend/main.py:94-100`
- **Details:** `allow_origins=["*"]` configured with `allow_credentials=True`.
- **Remediation:** Restrict allowed origins to specific trusted domains (e.g. `https://workline.ai`, `http://localhost:3000`).

### SEC-03: Secret Exposure Hygiene (Severity: PASS)
- **Details:** Verified that error handlers, logs, and public endpoints do not dump raw AWS Bedrock credentials, SurrealDB passwords, or Algorand private keys.
