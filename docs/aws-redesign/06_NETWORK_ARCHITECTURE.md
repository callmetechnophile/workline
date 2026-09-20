# Workline Network & VPC Topology Architecture

**Document ID:** `WORKLINE-AWS-06`  
**Status:** CANONICAL NETWORK SPECIFICATION  

---

## 1. Multi-AZ VPC Architecture

Workline provisions a high-availability Virtual Private Cloud (VPC) spanning three Availability Zones (AZ-a, AZ-b, AZ-c) in the selected AWS region (e.g., `us-east-1` or `us-west-2`).

```
VPC: 10.0.0.0/16
├── Availability Zone A (us-east-1a)
│   ├── Public Subnet (10.0.1.0/24)        -> ALB-a, NAT Gateway A
│   ├── Private App Subnet (10.0.10.0/24)  -> ECS API Tasks, ECS Worker Tasks
│   └── Isolated Data Subnet (10.0.20.0/24)-> SurrealDB, Qdrant, ElastiCache
├── Availability Zone B (us-east-1b)
│   ├── Public Subnet (10.0.2.0/24)        -> ALB-b, NAT Gateway B
│   ├── Private App Subnet (10.0.11.0/24)  -> ECS API Tasks, ECS Worker Tasks
│   └── Isolated Data Subnet (10.0.21.0/24)-> SurrealDB Standby, ElastiCache
└── Availability Zone C (us-east-1c)
    ├── Public Subnet (10.0.3.0/24)        -> ALB-c
    ├── Private App Subnet (10.0.12.0/24)  -> ECS API Tasks, ECS Worker Tasks
    └── Isolated Data Subnet (10.0.22.0/24)-> Backup Storage, ElastiCache
```

---

## 2. Subnet Route Tables & Ingress Rules

| Subnet Tier | CIDR Blocks | Default Route (`0.0.0.0/0`) | Ingress Allowed | Egress Allowed |
| :--- | :--- | :--- | :--- | :--- |
| **Public Subnets** | `10.0.1.0/24`, `10.0.2.0/24`, `10.0.3.0/24` | Internet Gateway (`igw-...`) | HTTPS (443) from CloudFront (AWS IP ranges) | Anywhere via IGW |
| **Private App Subnets** | `10.0.10.0/24`, `10.0.11.0/24`, `10.0.12.0/24` | NAT Gateway (`nat-...`) | Port 8000 from ALB Security Group | Outbound internet via NAT for external vendor APIs |
| **Isolated Data Subnets**| `10.0.20.0/24`, `10.0.21.0/24`, `10.0.22.0/24`| **NONE (No Internet Route)** | Port 8000 (SurrealDB), 6333 (Qdrant), 6379 (Redis) from `sg-app` | Internal VPC only via AWS PrivateLink endpoints |

---

## 3. AWS PrivateLink VPC Endpoints

To ensure zero public internet transit for internal AWS API calls from private and isolated subnets, the following VPC Endpoints are provisioned:

1. `com.amazonaws.<region>.s3` (Gateway Endpoint) — For high-bandwidth, zero-cost S3 artifact uploads and database snapshots.
2. `com.amazonaws.<region>.bedrock-runtime` (Interface Endpoint) — Direct private access to Amazon Bedrock inference.
3. `com.amazonaws.<region>.sqs` (Interface Endpoint) — Private queueing for Control Fabric background tasks.
4. `com.amazonaws.<region>.secretsmanager` (Interface Endpoint) — Secure database credential retrieval.
5. `com.amazonaws.<region>.logs` & `monitoring` (Interface Endpoint) — CloudWatch telemetry streaming.
