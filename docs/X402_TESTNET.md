# Workline AI — Algorand Testnet x402 Payment & Verification Guide

This guide documents the end-to-end configuration and execution of real micro-payments on **Algorand Testnet** using the **x402 protocol**, **Pera Wallet**, and the **GoPlausible Facilitator**.

---

## 1. Algorand Testnet Architecture Overview

```
Client (Browser / Pera Wallet)
        │
        ▼ 1. Call GET /api/x402/demo
Server (Workline x402 Engine)
        │
        ▼ 2. Return HTTP 402 + X402Challenge (0.01 USDC, asset_id=10458941)
Client (Pera Wallet UI)
        │
        ▼ 3. Prompt user for signature (0.01 USDC Asset Transfer)
Client (Auto-Retry)
        │
        ▼ 4. Retry with X-PAYMENT: {"tx_hash": "...", "signature": "..."}
Facilitator (GoPlausible / Testnet Indexer)
        │
        ▼ 5. Cryptographic verification & on-chain replay check
Server ──► Return HTTP 200 + REAL Transaction ID + Attestation Proof
```

---

## 2. Environment Configuration

Set the following environment variables in your backend `.env` (or cloud runtime configuration):

```bash
# Network Mode
X402_NETWORK=algorand-testnet
X402_MODE=testnet

# Testnet USDC ASA ID (Circle Official Algorand Testnet USDC)
X402_ASSET=USDC
X402_ASSET_ID=10458941

# GoPlausible Facilitator API URL
X402_FACILITATOR_URL=https://facilitator.goplausible.xyz

# Workline Testnet Receiving Treasury (58-character public address)
X402_PAY_TO=WORKLINE24EUSDCALGORANDTREASURYRECIPIENT402TESTNETADDRXXXX

# Demo Service Price
X402_PRICE_USDC=0.01

# Algorand Testnet Public Nodes
ALGORAND_NODE_URL=https://testnet-api.algonode.cloud
ALGORAND_INDEXER_URL=https://testnet-idx.algonode.cloud
```

> **SECURITY NOTE:** Never commit private keys, mnemonics, or seed phrases to the repository. The receiving address `X402_PAY_TO` is a public address only.

---

## 3. Obtaining Testnet Funds

1. **Testnet ALGO (for transaction fees):**
   - Use the [Algorand Testnet Dispenser](https://bank.testnet.algorand.network/) or [Algodex Faucet](https://dispenser.testnet.aws.algodev.network/).
   - Fund your Pera Testnet wallet with at least 1–2 Testnet ALGO.

2. **Testnet USDC (Asset ID: `10458941`):**
   - In Pera Wallet (switched to Testnet mode in Settings -> Developer Settings -> Node Settings -> Testnet), opt-in to Asset ID `10458941`.
   - Request Testnet USDC from the Circle/Algorand faucet or dispense bot.

---

## 4. End-to-End Test Procedure via UI

1. **Start Backend & Frontend:**
   ```bash
   # Terminal 1 (Backend)
   uvicorn backend.main:app --reload --port 8000

   # Terminal 2 (Frontend)
   cd frontend && npm run dev
   ```

2. **Open Workline Workbench:**
   - Navigate to `http://localhost:3000`.
   - Sign in with Clerk.

3. **Open Wallet Page:**
   - Click the **Wallet** icon in the top navigation bar, or navigate directly to `http://localhost:3000/wallet`.

4. **Connect Pera Wallet:**
   - Click **Connect Pera Wallet**.
   - Scan the QR code with Pera Mobile on Testnet or connect via Pera Web.
   - The UI will display your connected Testnet address: `ABCD...WXYZ` with a green `CONNECTED` badge.

5. **Execute x402 Payment Test:**
   - Under **x402 Payment Test (Workline Verified Engineering Service - 0.01 USDC)**, click **Pay 0.01 USDC via x402**.
   - The client fetches `GET /api/x402/demo` and receives a real `HTTP 402 Payment Required` challenge.
   - Pera Wallet opens a signature modal requesting approval to transfer `0.01 USDC` to the Workline treasury.
   - Approve the transaction in Pera Wallet.
   - The client automatically retries `GET /api/x402/demo` with the `X-PAYMENT` header attached.
   - GoPlausible verifies the settlement and the backend transitions the payment status to `SETTLED`.

6. **Inspect Verified Transaction:**
   - The UI updates to show:
     - `✓ PAYMENT SETTLED`
     - Service: `Workline Verified Engineering Service`
     - Real Algorand Transaction ID (e.g. `TXALGO...`)
     - Click **View on Algorand Explorer** to inspect the live transaction on [Lora Algokit Explorer](https://lora.algokit.io/testnet).

---

## 5. API Direct Testing via cURL

### Step 1: Request Challenge (Unpaid)
```bash
curl -i -X GET http://localhost:8000/api/x402/demo
```
**Expected Output:**
```http
HTTP/1.1 402 Payment Required
X-Payment-Required: x402 network=algorand-testnet asset=USDC asset_id=10458941 amount=0.01 pay_to=WORKLINE... payment_request_id=pay_req_...

{
  "error": "Payment Required",
  "status_code": 402,
  "service_id": "workline.test.verified",
  "challenge": {
    "scheme": "x402",
    "network": "algorand-testnet",
    "asset": "USDC",
    "asset_id": 10458941,
    "amount": 0.01,
    "pay_to": "WORKLINE24EUSDCALGORANDTREASURYRECIPIENT402TESTNETADDRXXXX",
    "payment_request_id": "pay_req_a1b2c3d4e5f6",
    "nonce": "...",
    "facilitator": "https://facilitator.goplausible.xyz"
  }
}
```

### Step 2: Retry with Signed Payment Proof
```bash
curl -i -X GET http://localhost:8000/api/x402/demo \
  -H 'X-PAYMENT: {"payment_request_id":"pay_req_a1b2c3d4e5f6","tx_hash":"TXALGOTESTNETEXAMPLEHASH52CHARSXXXXXXXXXXXXXXXXXXX","signature":"sig","payer_address":"PERAWALLETADDRESS..."}'
```
**Expected Output:**
```http
HTTP/1.1 200 OK

{
  "status": "SUCCESS",
  "service_id": "workline.test.verified",
  "payment": {
    "payment_id": "pay_req_a1b2c3d4e5f6",
    "status": "EXECUTED",
    "amount_usdc": 0.01,
    "asset": "USDC",
    "network": "algorand-testnet",
    "tx_hash": "TXALGOTESTNETEXAMPLEHASH52CHARSXXXXXXXXXXXXXXXXXXX",
    "settled_at": "2026-08-23T10:25:00Z"
  },
  "result": {
    "status": "VERIFIED",
    "service_id": "workline.test.verified",
    "service_name": "Workline Verified Engineering Service",
    "price_usdc": 0.01,
    "engineering_attestation": "Autonomous hardware lifecycle attestation unlocked via verified Algorand Testnet x402 settlement."
  }
}
```

---

## 6. Replay & Tamper Resistance

- **Replay Protection:** Submitting the same `tx_hash` against a second `payment_request_id` is rejected with `HTTP 400 Replay rejected`.
- **Amount Tampering:** The 0.01 USDC price is calculated server-side; client attempts to alter the charge are rejected.
- **Challenge Expiration:** Every challenge has a 30-minute TTL; expired challenges are rejected.
