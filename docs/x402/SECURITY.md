# Workline AI — x402 Security Specification

## 1. Threat Model & Safeguards

| Threat | Attack Vector | Workline Mitigation |
| :--- | :--- | :--- |
| **Replay Attacks** | Reusing a valid `tx_hash` across multiple service requests | Database constraints enforce one unique service execution per on-chain `tx_hash`. Second attempts are rejected with `400 Bad Request: Transaction hash already redeemed`. |
| **Client-Side Spoofing** | Sending `payment=true` or fake proof objects in headers | Workline backend verifies proofs against GoPlausible facilitator or Algorand indexer/node. Client boolean assertions are ignored. |
| **Double Charging** | Network timeouts causing client retries of the same paid action | Idempotency keys (`X-Idempotency-Key`) return the previously executed result without issuing new charges or double-settling. |
| **Challenge Tampering** | Changing the challenge amount or asset ID | Payment verification matches on-chain receiver (`pay_to`), asset ID (`31566704`), and minimum amount against server-side session records. |
| **Expired Challenges** | Submitting transactions against hours-old challenges | Challenges enforce a strict 30-minute time-to-live (`expires_at`). Expired challenges transition to `EXPIRED`. |
| **Unauthorized Project Access** | Using payment to access another user's private project data | Verification requires user authentication & project authorization before executing project-scoped workloads. |
| **Secret Leakage** | Exposing private keys or facilitator API secrets in logs/frontend | Zero blockchain private keys are stored on the server (Workline acts as payee with public address only). Facilitator secrets are environment-scoped. |

---

## 2. Redaction & Audit Logging

Workline emits structured logs during all 402 lifecycle events:
- `402_CHALLENGE_ISSUED`: Service ID, amount, nonce, client IP.
- `PAYMENT_PROOF_RECEIVED`: Payment request ID, transaction hash (truncated).
- `PAYMENT_SETTLED`: Facilitator confirmation, block round, timestamp.
- `SERVICE_EXECUTED`: Execution duration, status, result summary.

**Strict Prohibition**: No mnemonics, private keys, or client credentials are ever logged.
