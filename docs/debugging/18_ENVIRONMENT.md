# Workline Environment Configuration Audit

**Document ID:** `WORKLINE-DEBUG-18`  
**Execution Timestamp:** 2026-09-18T01:14:00+05:30  
**File:** `.env`  

---

## 1. Environment Variable Audit

A total of **16 environment variables** were detected in `.env`:

| Key Name | Category | Status | Operational Impact |
| :--- | :--- | :---: | :--- |
| `AWS_ACCESS_KEY_ID` | AI Provider | Present | Bedrock runtime; token currently invalid (`UnrecognizedClientException`) |
| `AWS_SECRET_ACCESS_KEY` | AI Provider | Present | Bedrock runtime |
| `AWS_REGION` | AI Provider | Present (`us-east-1`) | Valid region configuration |
| `SURREALDB_URL` | Graph Database | Present | Cloud instance suspended/unreachable (HTTP 403) |
| `SURREALDB_USER` / `PASS` | Graph Database | Present | Credentials configured |
| `QDRANT_URL` | Vector Database | Present | Cloud instance suspended/unreachable |
| `QDRANT_API_KEY` | Vector Database | Present | Credentials configured |
| `ALGORAND_NETWORK` | x402 Micropayments | Present (`testnet`) | Operates in testnet mode |
| `ALGORAND_ALGOD_SERVER` | x402 Micropayments | Present | Node API endpoint configured |
| `CLERK_SECRET_KEY` | Authentication | Present | Clerk user validation |
| `CLERK_JWKS_URL` | Authentication | Present | Public key URL for token decoding |
| `NVIDIA_API_KEY` | Fallback AI | Missing | Gateway correctly skips to LocalMockProvider |
