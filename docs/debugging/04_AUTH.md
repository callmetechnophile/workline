# Workline Authentication & Security Audit

**Document ID:** `WORKLINE-DEBUG-04`  
**Execution Timestamp:** 2026-09-18T01:14:00+05:30  
**Module:** `backend/auth.py` & Clerk Gateway  

---

## 1. Authentication Flow Analysis

Workline uses Clerk for identity and token management. In `backend/auth.py`, incoming requests are processed via HTTP Bearer tokens.

## 2. Empirical Test Results

| Test Scenario | Input Token | Expected Behavior | Observed Behavior | Verdict |
| :--- | :--- | :--- | :--- | :---: |
| **Malformed Token** | `invalid-token` | 401 Unauthorized | REJECTED_EXPECTED (401: Invalid authorization token: 401: Invalid token format) | **REAL_PASS** |
| **Unsigned / Forged Token** | Base64 header + payload with `sub`, dummy signature | 401 Signature Verification Failure | VULNERABLE_ACCEPTED (Accepted sub: `user_forged_123`) | **SECURITY_VULNERABILITY** |

## 3. Vulnerability Diagnosis: Unverified JWT Fallback

In `backend/auth.py`:
```python
try:
    if JWKS_CACHE:
        jwt.decode(token, JWKS_CACHE, algorithms=["RS256"])
except Exception as e:
    # Gracefully log verification failures and use claims for local dev resilience
    print(f"[Clerk Auth] Signature verification skipped/failed: {e}. Falling back to claims sub.")

user_id = payload.get("sub")
```

### Risk Severity: HIGH (CVSS 7.5)
- **Impact:** Any client can forge an arbitrary JWT with `sub: "admin"` or `sub: "target_user"` and bypass authentication when Clerk JWKS is unreachable or signature verification fails.
- **Remediation:** Enforce strict verification rejection in production environments; fallback must only be enabled under explicit `ALLOW_INSECURE_DEV_AUTH=true`.
