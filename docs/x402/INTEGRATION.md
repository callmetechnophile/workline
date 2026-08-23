# Workline AI — x402 Developer Integration Guide

This guide explains how autonomous AI agents, external microservices, and client applications consume Workline engineering services via the **x402 protocol** on **Algorand**.

---

## 1. Overview of x402 Endpoints

All services are accessible under `/api/x402/`.

### Discovering Available Services
```bash
GET /api/x402/services
```
**Response (200 OK):**
```json
{
  "network": "algorand-mainnet",
  "asset": "USDC",
  "asset_id": 31566704,
  "pay_to": "WORKLINE24EUSDCALGORANDTREASURYRECIPIENT402XXXXXXXXXXXXXX",
  "services": [
    {
      "id": "bom.optimize",
      "name": "BOM Sourcing Optimizer",
      "price_usdc": 0.50,
      "endpoint": "/api/x402/bom/optimize",
      "enabled": true
    },
    {
      "id": "component.analyze",
      "name": "Component & Datasheet AI",
      "price_usdc": 0.25,
      "endpoint": "/api/x402/component/analyze",
      "enabled": true
    },
    {
      "id": "research.engineering",
      "name": "Hardware Research Synthesis",
      "price_usdc": 1.00,
      "endpoint": "/api/x402/research/engineering",
      "enabled": true
    },
    {
      "id": "simulation.thermal",
      "name": "Multi-Physics Thermal PINN",
      "price_usdc": 0.75,
      "endpoint": "/api/x402/simulation/thermal",
      "enabled": true
    },
    {
      "id": "procurement.quote",
      "name": "Multi-Vendor RFQ Consolidation",
      "price_usdc": 0.25,
      "endpoint": "/api/x402/procurement/quote",
      "enabled": true
    }
  ]
}
```

---

## 2. Making a Service Call (402 Handshake Flow)

### Step 1: Initial Request (Unpaid)
An external client or AI agent sends an engineering payload to the service endpoint:

```bash
POST /api/x402/bom/optimize
Content-Type: application/json

{
  "project_id": "rover_power_board",
  "bom_items": [
    { "ref": "U1", "part_number": "TPS62130RGTR", "quantity": 1 }
  ]
}
```

### Step 2: Receive 402 Payment Required
Workline returns an HTTP 402 with structured payment challenge details:

```http
HTTP/1.1 402 Payment Required
Content-Type: application/json
X-Payment-Required: x402 network=algorand-mainnet asset=USDC asset_id=31566704 amount=0.50 pay_to=WORKLINE24...

{
  "error": "Payment Required",
  "status_code": 402,
  "service_id": "bom.optimize",
  "challenge": {
    "scheme": "x402",
    "network": "algorand-mainnet",
    "asset": "USDC",
    "asset_id": 31566704,
    "amount": 0.50,
    "pay_to": "WORKLINE24EUSDCALGORANDTREASURYRECIPIENT402XXXXXXXXXXXXXX",
    "nonce": "c98df2410a7b45828f731238914bca81",
    "payment_request_id": "pay_req_9f3b128ac812",
    "expires_at": "2026-08-23T08:35:00Z",
    "facilitator": "https://facilitator.goplausible.com"
  }
}
```

### Step 3: Sign & Settle on Algorand
The client or agent wallet constructs an Algorand Asset Transfer Transaction (`axfer`) sending `0.50 USDC` (`500,000` base units given 6 decimals) to the specified `pay_to` address, including the `nonce` in the transaction note.

### Step 4: Retry with Payment Proof
The client re-submits the request with the transaction proof:

```bash
POST /api/x402/bom/optimize
Content-Type: application/json
X-PAYMENT: { "payment_request_id": "pay_req_9f3b128ac812", "tx_hash": "ALGO_TX_HASH_402_PROOF_998124" }

{
  "project_id": "rover_power_board",
  "bom_items": [
    { "ref": "U1", "part_number": "TPS62130RGTR", "quantity": 1 }
  ]
}
```

### Step 5: Service Execution & Result
Workline validates the settlement through GoPlausible, runs the optimization engine, and responds with HTTP 200:

```json
{
  "status": "SUCCESS",
  "service_id": "bom.optimize",
  "payment": {
    "payment_id": "pay_req_9f3b128ac812",
    "status": "SETTLED",
    "amount_usdc": 0.50,
    "network": "algorand-mainnet",
    "tx_hash": "ALGO_TX_HASH_402_PROOF_998124"
  },
  "result": {
    "bom_count": 1,
    "resolved_items": [
      {
        "ref": "U1",
        "part_number": "TPS62130RGTR",
        "supplier": "DigiKey",
        "unit_price_usd": 2.10,
        "availability": "IN_STOCK",
        "status": "OPTIMIZED"
      }
    ],
    "savings_summary": {
      "original_cost_usd": 2.65,
      "optimized_cost_usd": 2.10,
      "percentage_savings": 20.7
    }
  }
}
```

---

## 3. Python SDK Example (Agent Integration)

```python
import httpx
import json

BASE_URL = "https://workline-core-gateway.onrender.com"

def run_paid_bom_optimization(bom_data: dict, algorand_signer) -> dict:
    with httpx.Client(base_url=BASE_URL) as client:
        # 1. First attempt -> triggers 402
        res = client.post("/api/x402/bom/optimize", json=bom_data)
        
        if res.status_code == 402:
            challenge = res.json()["challenge"]
            print(f"402 Received: Pay {challenge['amount']} USDC to {challenge['pay_to']}")
            
            # 2. Sign and submit Algorand USDC transaction
            tx_hash = algorand_signer.transfer_usdc(
                pay_to=challenge["pay_to"],
                amount_usdc=challenge["amount"],
                asset_id=challenge["asset_id"],
                note=challenge["nonce"]
            )
            
            # 3. Retry with proof
            proof_headers = {
                "X-PAYMENT": json.dumps({
                    "payment_request_id": challenge["payment_request_id"],
                    "tx_hash": tx_hash
                })
            }
            res_paid = client.post("/api/x402/bom/optimize", json=bom_data, headers=proof_headers)
            res_paid.raise_for_status()
            return res_paid.json()
            
    return res.json()
```
