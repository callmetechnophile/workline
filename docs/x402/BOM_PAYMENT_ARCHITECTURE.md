# Workline x402 BOM Payment, Algorand Settlement, and Informational Report Architecture

## 1. Architectural Overview

Workline AI uses a non-custodial, high-precision payment and reporting pipeline for hardware Bill of Materials (BOM) procurement and engineering services:

```
[BOM Engine] (Authoritative USD Total via Decimal arithmetic)
      ↓
[x402 Service] (Issues HTTP 402 Challenge: Exact 1:1 USDC Amount)
      ↓
[Algorand Network] (Settles USDC on Mainnet / Testnet)
      ↓
[GoPlausible Facilitator] (Verifies settlement proof & prevents replay)
      ↓
[Payment Settled] (Authoritative payment ledger record created)
      ↓
┌──────────────────────────────────────────────┐
│ Post-Settlement Report Compilation           │
│                                              │
│ [CoinGecko] (USD Coin -> INR Rate fetched    │
│              EXACTLY ONCE per report)        │
│                                              │
│ [ReportLab Engine] (Compiles immutable PDF   │
│                     with itemized BOM, USDC, │
│                     Lora Explorer URL, & INR)│
└──────────────────────────────────────────────┘
```

---

## 2. Core Financial Principle

$$\text{Authoritative BOM Total (USD)} = \text{x402 Payment Amount (USDC)} = \text{Settlement Amount (USDC)}$$

- **Strictly No Currency Distortion**: There is **no** `USD → INR → USDC` conversion in determining the payment obligation. USDC is already USD-denominated.
- **CoinGecko Role**: CoinGecko exists **ONLY** to annotate the final post-settlement report with an approximate local currency reference.
- **CoinGecko Isolation**: CoinGecko is **NOT** used to determine the payment amount and is **NOT** in the payment authorization path.

---

## 3. Decimal Money Handling (Zero Floating-Point Drift)

All financial totals are calculated using Python's `Decimal` with standard `ROUND_HALF_UP` quantization:
- Line item total: $\text{line\_total} = \text{quantity} \times \text{unit\_price\_usd}$
- BOM Total: $\text{bom\_total\_usd} = \sum \text{line\_total}$
- Floating-point addition bugs (e.g. `0.1 + 0.2 = 0.30000000000000004`) are strictly prevented in financial logic.

---

## 4. x402 Payment State Machine

| State | Description |
|---|---|
| `BOM_CREATED` | BOM line items defined and validated. |
| `PAYMENT_REQUIRED` | Frozen `PaymentQuote` issued with unique `quote_id` and expiry. |
| `PAYMENT_SUBMITTED` | Client submits Algorand transaction hash / proof. |
| `PAYMENT_VERIFYING` | Proof being verified against Algorand / GoPlausible Facilitator. |
| `PAYMENT_SETTLED` | Payment confirmed on-chain for exact required USDC amount. |
| `REPORT_GENERATING` | Initiating post-settlement PDF report compilation. |
| `REPORT_READY` | Auditable PDF report generated with CoinGecko INR annotation. |
| `REPORT_READY_WITHOUT_INR` | PDF generated with INR marked "Unavailable" due to CoinGecko timeout/error. |
| `PAYMENT_FAILED` | Verification failed (amount mismatch, invalid signature, replay). |
| `PAYMENT_EXPIRED` | Payment challenge TTL elapsed before settlement. |
| `REPORT_FAILED` | PDF rendering engine failure. |

---

## 5. Algorand & GoPlausible Settlement Verification

- **Settlement Network**: Algorand Mainnet (`asset_id: 31566704`) or Algorand Testnet (`asset_id: 10458941`).
- **Replay Protection**: Every transaction hash is checked against the persistent ledger; duplicate redemption attempts are rejected.
- **Amount Verification**: Exact equality between the required quote amount and the settled on-chain USDC amount is strictly enforced.

---

## 6. CoinGecko Resilience Guarantee

When generating the PDF report:
1. `GET /simple/price?ids=usd-coin&vs_currencies=inr` is queried **once**.
2. If CoinGecko responds successfully: Rate is recorded, and `≈ ₹X,XXX.XX INR` is stamped with timestamp and source.
3. If CoinGecko times out, returns HTTP 5xx, or responds with malformed data:
   - The PDF generation **proceeds without error**.
   - The INR field is stamped as `<font color='#b91c1c'>Unavailable</font>`.
   - The report retains all itemized BOM details, USD total, USDC settled amount, transaction ID, and explorer verification link.

---

## 7. ArmourIQ Governance

Procurement and payment actions are protected by ArmourIQ:
- **Capability**: `AgentCapability.EXECUTE_PROCUREMENT` (or `FINANCIAL_TRANSACTION`)
- **Risk Tier**: `RiskTier.CRITICAL`
- Payment authorization and capability authorization remain separate controls: payment does not bypass ArmourIQ policy, and ArmourIQ does not waive payment obligations.
