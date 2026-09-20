# Workline Security, Identity & Threat Mitigation Architecture

**Document ID:** `WORKLINE-AWS-05`  
**Status:** CANONICAL SECURITY SPECIFICATION  

---

## 1. Zero-Trust Security Principles

1. **Strict Private Database Isolation:**
   - Neither **SurrealDB** nor **Qdrant** is EVER exposed to the public internet.
   - The browser **MUST NEVER** connect directly to SurrealDB or Qdrant.
   - All database queries are authenticated and mediated by the Workline API or Control Fabric over private VPC subnets.
2. **Zero Hardcoded Credentials:**
   - Static IAM access keys (`AKIA...`) are strictly prohibited in code, Git repositories, Docker images, and container environment variables.
   - All AWS permissions are obtained dynamically via ECS Task IAM Roles.
   - Database passwords, API keys, and third-party tokens are stored in AWS Secrets Manager and resolved at runtime.
3. **Strict Cryptographic Authentication:**
   - Deprecate the insecure fallback in `backend/auth.py`.
   - All incoming API requests must present a valid RS256 JWT issued by **Amazon Cognito User Pools**.
   - Tokens are validated against Cognito JWKS public keys with strict audience, issuer, and expiration verification.

---

## 2. Identity & Access Management (IAM & Cognito)

```
                    ┌─────────────────────────┐
                    │       User Browser      │
                    └────────────┬────────────┘
                                 │ 1. OAuth2 Login
                                 ▼
                    ┌─────────────────────────┐
                    │ Amazon Cognito User Pool│
                    └────────────┬────────────┘
                                 │ 2. Issues RS256 JWT (ID + Access Token)
                                 ▼
                    ┌─────────────────────────┐
                    │   Workline Web Portal   │
                    └────────────┬────────────┘
                                 │ 3. HTTPS + Bearer <JWT>
                                 ▼
                    ┌─────────────────────────┐
                    │  FastAPI API / BFF GW   │
                    │  - Validates RS256 JWKS │
                    │  - Extracts User & Roles│
                    └────────────┬────────────┘
                                 │ 4. Authorized Query / Task
                                 ▼
                    ┌─────────────────────────┐
                    │     Control Fabric      │
                    └─────────────────────────┘
```

### Role-Based Access Control (RBAC) Matrix:
- `system:admin`: Full administrative access to system health, all projects, agent configurations, and audit trails.
- `project:lead`: Can create projects, approve BOM transitions, trigger simulations, and sign off on design decisions.
- `engineer:write`: Can submit tasks, edit requirements, upload CAD/PCB files, and run trade studies.
- `viewer:read`: Read-only access to project dashboards, reports, and generated artifacts.

---

## 3. Network Security & Subnet Protection

- **Public Subnet:** Application Load Balancer and NAT Gateways only.
- **Private Application Subnet:** ECS Fargate API containers and ECS Fargate Worker containers. Ingress allowed only from ALB (port 8000).
- **Isolated Data Subnet:** SurrealDB, Qdrant, and ElastiCache Redis. **Zero internet routes.** Ingress allowed strictly from API and Worker security groups on specific ports:
  - SurrealDB: Port 8000 (TCP) from `sg-api` and `sg-workers`.
  - Qdrant: Port 6333 (HTTP) and 6334 (gRPC) from `sg-api` and `sg-workers`.
  - Redis: Port 6379 from `sg-api` and `sg-workers`.

---

## 4. Encryption Standards

- **In-Transit:** TLS 1.3 enforced at CloudFront, ALB, and internal service communication.
- **At-Rest:**
  - Amazon S3: SSE-KMS with Customer Managed Key (CMK) and automatic key rotation.
  - Amazon EBS gp3 (SurrealDB & Qdrant persistent disks): KMS encrypted.
  - AWS Secrets Manager: KMS encrypted.
  - Amazon CloudWatch Logs: KMS encrypted.

---

## 5. Centralized LLM Gateway & Bedrock Guardrails

All model interactions flow through the central LLM Gateway:
- **Bedrock Guardrails:** Configured to sanitize prompts, detect jailbreak attempts, mask sensitive PII (emails, SSNs, financial info), and block harmful content.
- **Capability Isolation:** Image and CAD generation requests are strictly bound to Bedrock Titan Image or specialized agents; they are **NEVER** routed to text-only fallbacks such as NVIDIA NIM.
