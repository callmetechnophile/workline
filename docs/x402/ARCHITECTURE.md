# Workline AI — Algorand x402 Service Monetization Architecture

## 1. Executive Overview

Workline AI is an engineering lifecycle platform that synthesizes hardware requirements, queries domain literature, optimizes Bill of Materials (BOMs), verifies physical PCB constraints, and solves multi-physics neural surrogate PINN models.

This document defines the **x402 Service Monetization Architecture**, establishing how external AI agents, developers, and enterprises pay Workline for computational and engineering intelligence services using **USDC on the Algorand blockchain** coordinated via the **GoPlausible Facilitator**.

---

## 2. Core Architectural Separation

A fundamental requirement of this architecture is the **strict separation** between:
1. **Workline Service Revenue (x402)**: Micro-payments made to Workline for API and service execution.
2. **Physical Component Procurement**: Purchase orders and checkout submitted to third-party component distributors (DigiKey, Mouser, Robu) via their native commerce rails.

```
+-------------------------------------------------------------------------------+
|                                WORKLINE AI                                    |
|                                                                               |
|   +-----------------------------------------------------------------------+   |
|   |                       WORKLINE x402 GATEWAY                           |   |
|   |  • Issues HTTP 402 Challenges with Algorand USDC terms                |   |
|   |  • Verifies GoPlausible facilitator settlement proofs                 |   |
|   |  • Credits WORKLINE SERVICE REVENUE to Workline Pay-To Wallet         |   |
|   +-----------------------------------------------------------------------+   |
|                                       | (Payment Verified)                    |
|                                       v                                       |
|   +-----------------------------------------------------------------------+   |
|   |                     ENGINEERING AI SERVICES (R1-R5)                   |   |
|   |  [bom.optimize]          [component.analyze]  [research.engineering]  |   |
|   |  [simulation.thermal]    [procurement.quote]                          |   |
|   +-----------------------------------------------------------------------+   |
|                                       |                                       |
|                                       | (Outputs BOM / Quote / Plan)          |
|                                       v                                       |
|   +-----------------------------------------------------------------------+   |
|   |                     PHYSICAL PROCUREMENT ENGINE                       |   |
|   |  • Consolidates vendor availability & pricing                         |   |
|   |  • Generates itemized Purchase Orders                                 |   |
|   |  • Submits orders via DigiKey / Mouser / Robu B2B APIs                |   |
|   |  • Paid via DISTRIBUTOR PAYMENT RAILS (Invoicing / Credit Card / ACH)  |   |
|   +-----------------------------------------------------------------------+   |
+-------------------------------------------------------------------------------+
```

> [!IMPORTANT]
> **No Fake Crypto Checkout**: Workline does NOT implement a fake "USDC-to-DigiKey" payment bridge. The x402 payment received by Workline is solely for Workline's engineering computations and AI services.

---

## 3. Algorand + USDC + GoPlausible Standard

### 3.1 Network Parameters
- **Blockchain**: Algorand (Fast finality ~3.3s, low transaction costs <0.001 ALGO).
- **Payment Asset**: USDC (Algorand Standard Asset / ASA).
- **Mainnet USDC Asset ID**: `31566704` (6 decimals).
- **Testnet USDC Asset ID**: `10458941` (6 decimals).
- **Facilitator**: GoPlausible (`https://facilitator.goplausible.com` or custom configured node).
- **Standard Protocol**: x402 HTTP Payment Required standard.

### 3.2 Key Configuration Variables
| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `WORKLINE_X402_NETWORK` | Target Algorand network | `algorand-mainnet` / `algorand-testnet` |
| `WORKLINE_X402_ASSET` | Symbol of settlement asset | `USDC` |
| `WORKLINE_X402_ASSET_ID` | Algorand ASA ID | `31566704` (Mainnet) / `10458941` (Testnet) |
| `WORKLINE_X402_PAY_TO` | Workline Treasury Algorand Address | `WORKLINE24...` (58-char Algorand address) |
| `WORKLINE_X402_FACILITATOR_URL` | GoPlausible Facilitator API | `https://facilitator.goplausible.com` |
| `WORKLINE_X402_ENABLED` | Feature gate for 402 monetization | `true` |

---

## 4. End-to-End 402 Handshake Lifecycle

```
CLIENT / AGENT                      WORKLINE GATEWAY                     GOPLAUSIBLE / ALGORAND
      |                                    |                                       |
      | 1. POST /api/x402/bom/optimize     |                                       |
      |    (No payment proof)              |                                       |
      |----------------------------------->|                                       |
      |                                    |                                       |
      | 2. HTTP 402 Payment Required       |                                       |
      |    Header: X-Payment-Required      |                                       |
      |    Body: { price: 0.50,            |                                       |
      |            asset_id: 31566704,     |                                       |
      |            pay_to: "...", ... }    |                                       |
      |<-----------------------------------|                                       |
      |                                                                            |
      | 3. Signs Algorand ASA transfer transaction                                 |
      |--------------------------------------------------------------------------->|
      |                                                                            |
      | 4. Confirms on-chain & generates GoPlausible proof                         |
      |<---------------------------------------------------------------------------|
      |                                    |                                       |
      | 5. POST /api/x402/bom/optimize     |                                       |
      |    Header: X-PAYMENT: <proof>      |                                       |
      |----------------------------------->|                                       |
      |                                    | 6. Verifies proof with GoPlausible    |
      |                                    |-------------------------------------->|
      |                                    | 7. Settlement Verified (USDC in PayTo)|
      |                                    |<--------------------------------------|
      |                                    |                                       |
      |                                    | 8. Executes BOM Optimization Engine   |
      |                                    |    (Knowledge + Sourcing + Pin checks)|
      |                                    |                                       |
      | 9. HTTP 200 OK + Service Result    |                                       |
      |    { status: "SUCCESS", ... }      |                                       |
      |<-----------------------------------|                                       |
```

---

## 5. Service Catalog & Authoritative Pricing

| Service ID | Service Name | Endpoint | Price (USDC) | Description |
| :--- | :--- | :--- | :--- | :--- |
| `bom.optimize` | BOM Sourcing Optimizer | `POST /api/x402/bom/optimize` | **$0.50** | Multi-vendor consolidation, stock verification & lifecycle checks |
| `component.analyze` | Component & Datasheet AI | `POST /api/x402/component/analyze` | **$0.25** | Automated datasheet parameter extraction & pin compatibility |
| `research.engineering` | Hardware Research Synthesis | `POST /api/x402/research/engineering` | **$1.00** | Literature vector search, topology ranking & contradiction check |
| `simulation.thermal` | Multi-Physics Thermal PINN | `POST /api/x402/simulation/thermal` | **$0.75** | Physics-Informed Neural Network 2D/3D thermal loss solver |
| `procurement.quote` | Multi-Vendor RFQ Consolidation | `POST /api/x402/procurement/quote` | **$0.25** | Real-time distributor price aggregation & MOQ optimization |

---

## 6. Idempotency & Replay Protection

1. **Transaction Hash Deduping**: Each Algorand transaction hash (`tx_hash`) can settle at most one unique service execution request.
2. **Idempotency Keys**: Clients may provide an `X-Idempotency-Key` or `idempotency_key` in the request body. If the same key is submitted again for a settled request, Workline returns the cached result without re-executing or double-charging.
3. **Expiry Checks**: 402 payment challenges expire after 30 minutes. Proofs submitted against expired challenges are rejected.
4. **Project Isolation**: Service execution checks that the authenticated user owns or has access to the target `project_id`. Payment alone does NOT grant access to another tenant's project files.
