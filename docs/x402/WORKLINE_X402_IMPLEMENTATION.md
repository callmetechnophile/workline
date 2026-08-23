# Workline AI — Production x402 Procurement Implementation

## 1. Architectural Overview

```
                         NETLIFY
                    WORKLINE FRONTEND
                           |
                           |
                     PERA WALLET (Client Signing Boundary)
                           |
                           v
                          R1
                    CORE / GATEWAY
                           |
                    INTERNAL URL
                    SERVICE TOKEN
                           |
                           v
                          R5
             PROCUREMENT / BOM / x402
                           |
                    CREATE QUOTE
                           |
                    USD → USDC (Exact 1:1 Parity)
                           |
                           v
                 HTTP 402 REQUIREMENT
                           |
                           v
                      PERA WALLET
                           |
                      USER SIGNS
                           |
                           v
                   PAYMENT PROOF
                           |
                           v
                   x402 VERIFICATION
                           |
                           v
                GOPLAUSIBLE FACILITATOR
                           |
                           v
                       ALGORAND
                           |
                     USDC SETTLEMENT
                           |
                           v
                       TX HASH
                           |
                    ┌──────┴──────┐
                    │             │
                    v             v
                CoinGecko       PDF
                USD → INR       Report
             (Informational) (ReportLab)
                    │             │
                    └──────┬──────┘
                           v
                          R3
                  PROJECT ARTIFACTS
```

---

## 2. Non-Negotiable Financial Invariants

1. **Authoritative BOM Pricing**:
   - The BOM engine calculates the authoritative total in USD using Python `Decimal` (`ROUND_HALF_UP`) to 2 decimal places.
   - Example: $\$127.43$ USD is converted to $127.43$ USDC ($127,430,000$ base units in Algorand standard 6 decimals).
   - Zero binary floating point distortion on financial totals.

2. **Strict 1:1 USD $\rightarrow$ USDC Parity**:
   - Every $\$1.00$ USD in BOM is charged as exactly $1.00$ USDC on Algorand.
   - No USD $\rightarrow$ INR $\rightarrow$ USDC conversion.

3. **Isolated CoinGecko INR Snapshot**:
   - CoinGecko is queried **ONLY** after payment is marked `SETTLED`.
   - Performed **ONCE** per report generation (never per BOM line item).
   - If CoinGecko times out, returns HTTP 500/429, or is unreachable: the report still completes with status `REPORT_READY_WITHOUT_INR` omitting INR.
   - INR is purely informational and never affects settlement amount.

---

## 3. Client Signing & Security Invariants

1. **Pera Wallet Client-Side Signing Boundary**:
   - Users connect their Pera Wallet on the frontend (`@perawallet/connect` / `algosdk`).
   - Transaction signature occurs directly in the user's Pera mobile app or browser extension.
   - **Zero Private Keys**: Neither frontend application nor backend R1/R5 ever receive private keys, seed phrases, or mnemonics.

2. **Independent Backend Verification**:
   - R5 never trusts client assertions or arbitrary transaction hashes.
   - Verification is submitted to the GoPlausible facilitator (`https://facilitator.goplausible.com/v1/verify`) or verified on the Algorand blockchain.
   - Replay protection guarantees that a transaction ID can only be redeemed once.

3. **Quote / Payment Binding**:
   - R5 enforces exact parity:
     - `submitted_amount == quote.amount_usdc`
     - `submitted_asset == quote.asset_id (31566704)`
     - `submitted_network == quote.network (algorand-mainnet)`
     - `submitted_recipient == quote.pay_to`

---

## 4. API Endpoints

### Quote Generation (R5 / Gateway)
- `POST /api/x402/bom/quote` (or `POST /api/procurement/quote`):
```json
{
  "project_id": "rover_arm_01",
  "bom": {
    "bom_id": "BOM_ROVER_01",
    "items": [
      {
        "part_number": "STM32F405RGT6",
        "description": "MCU ARM Cortex-M4 168MHz",
        "quantity": 2,
        "unit_price_usd": 12.50
      },
      {
        "part_number": "DRV8825PWP",
        "description": "Stepper Motor Controller IC",
        "quantity": 4,
        "unit_price_usd": 3.75
      }
    ]
  }
}
```

**Response (HTTP 200 / 402 Challenge)**:
```json
{
  "quote_id": "quote_4b89b0aa",
  "payment_request_id": "pay_req_7c12f45a",
  "bom_id": "BOM_ROVER_01",
  "project_id": "rover_arm_01",
  "amount_usd": 40.00,
  "amount_usdc": 40.00,
  "asset_id": "31566704",
  "asset": "USDC",
  "network": "algorand-mainnet",
  "pay_to": "WORKLINE24EUSDCALGORANDTREASURYRECIPIENT402XXXXXXXXXXXXXX",
  "expires_at": "2026-08-23T12:30:00Z",
  "status": "PAYMENT_REQUIRED"
}
```

### Payment Settlement Verification
- `POST /api/x402/bom/verify` (or `POST /api/procurement/{quote_id}/pay`):
```json
{
  "quote_id": "quote_4b89b0aa",
  "tx_hash": "TXALGO_8849204859302194857392019485720194857392",
  "payer": "PERA73910485720194857392019485739201948573920194857392",
  "signature": "base64_signed_proof_data"
}
```

### Report Generation
- `POST /api/x402/bom/report`:
```json
{
  "quote_id": "quote_4b89b0aa"
}
```

---

## 5. Algorand Network Configuration & Asset Matrix

| Environment | Algorand Network | USDC Asset ID | Explorer Base URL |
| :--- | :--- | :--- | :--- |
| **Production** | `algorand-mainnet` | `31566704` | `https://lora.algokit.io/mainnet/transaction` |
| **Testnet** | `algorand-testnet` | `10458941` | `https://lora.algokit.io/testnet/transaction` |
| **Development** | `local` | `31566704` | `https://lora.algokit.io/mainnet/transaction` |
