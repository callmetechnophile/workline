# Workline AI — Algorand x402 Hackathon Demonstration

This document outlines the step-by-step demonstration flow of the **Algorand x402 Service Monetization** feature.

---

## Scenario: Autonomous Agent BOM Optimization

An external autonomous hardware agent wants Workline AI to optimize a Bill of Materials for a robotics power distribution board.

### Step 1: Discover Services
The agent queries the public catalog:
```bash
curl https://workline-core-gateway.onrender.com/api/x402/services
```
Returns 5 services with pricing in USDC on Algorand.

### Step 2: Invoke BOM Optimizer (Unpaid)
```bash
curl -X POST https://workline-core-gateway.onrender.com/api/x402/bom/optimize \
  -H "Content-Type: application/json" \
  -d '{"project_id": "rover_pwr_01", "bom_items": [{"ref": "U1", "part_number": "TPS62130RGTR", "quantity": 1}]}'
```
**Result**: HTTP `402 Payment Required` with challenge terms (0.50 USDC to Workline Pay-To address on Algorand).

### Step 3: Settle Payment on Algorand
The agent signs and broadcasts an Algorand transaction transferring 0.50 USDC to the Workline Treasury wallet.

### Step 4: Retry with Payment Proof
```bash
curl -X POST https://workline-core-gateway.onrender.com/api/x402/bom/optimize \
  -H "Content-Type: application/json" \
  -H 'X-PAYMENT: {"payment_request_id": "<PAY_REQ_ID>", "tx_hash": "<ALGORAND_TX_HASH>"}' \
  -d '{"project_id": "rover_pwr_01", "bom_items": [{"ref": "U1", "part_number": "TPS62130RGTR", "quantity": 1}]}'
```
**Result**: HTTP `200 OK` with complete BOM optimization output and settlement receipt.

### Step 5: Procurement Handoff (Separate Flow)
If the engineer approves the optimized BOM for physical ordering:
- The Procurement Engine generates standard distributor purchase orders (PO).
- Physical parts are ordered through DigiKey / Mouser API with commercial invoice billing.
- **x402 remains Workline service revenue.**
