# Workline AWS Platform Deployment & Hardening Plan

**Document ID:** `WORKLINE-AWS-10`  
**Status:** CANONICAL DEPLOYMENT ROADMAP  

---

## 1. Zero Database Migration Principle

**CRITICAL DIRECTIVE:** Workline does **NOT** migrate or replace SurrealDB or Qdrant. This roadmap focuses exclusively on platform deployment, AWS infrastructure provisioning, security hardening, and compute decoupling.

All existing SurrealDB tables, graph edges, and Qdrant vector collections are preserved in their native structures.

---

## 2. 10-Phase Platform Deployment Roadmap

### Phase 1: Canonical Architecture & Governance Baseline *(Completed)*
- Document complete AWS web-first rearchitecture in `docs/aws-redesign/`.
- Establish zero database migration invariants.
- Catalog all 27 agents and graph schemas.

### Phase 2: AWS Networking & Isolated Subnets Provisioning
- Deploy Terraform VPC module (3 AZs, public, private app, and isolated data subnets).
- Provision VPC Endpoints for S3, Bedrock, SQS, Secrets Manager, and CloudWatch.
- Configure security groups enforcing strict least-privilege traffic flow.

### Phase 3: SurrealDB on AWS Deployment & Automated Backup Setup
- Deploy self-hosted SurrealDB container on ECS Fargate / EC2 with attached Amazon EBS gp3 volume.
- Configure internal service discovery: `surrealdb.workline.internal:8000`.
- Implement automated nightly S3 export backup Lambda and hourly EBS snapshots.
- Verify health checks (`/health`) and query execution.

### Phase 4: Qdrant on AWS Deployment & Snapshot Automation
- Deploy self-hosted Qdrant container on ECS Fargate / EC2 with attached Amazon EBS gp3 volume.
- Configure internal service discovery: `qdrant.workline.internal:6333`.
- Verify standard collections: `workline_documents`, `workline_components`, `workline_projects`, `workline_research`.
- Set up automated daily snapshot sync to S3.

### Phase 5: Amazon S3 Pluggable Artifact Storage Subsystem
- Provision `workline-artifacts` S3 bucket with KMS encryption and versioning.
- Implement `backend/workline/artifacts/` store with pre-signed GET/PUT URL generation.
- Ensure only file metadata and S3 URIs are written to SurrealDB.

### Phase 6: Amazon Cognito Identity & RBAC Security Layer
- Provision Amazon Cognito User Pool with OAuth2/OIDC flows and custom RBAC claims.
- Implement `backend/app/auth/cognito.py` providing strict RS256 token verification.
- Eliminate insecure fallback in `backend/auth.py`.

### Phase 7: Central AWS Bedrock LLM Gateway
- Implement `backend/app/llm/bedrock_gateway.py` with Cross-Region Inference Profiles.
- Enforce Bedrock Guardrails for safety and PII masking.
- Configure text-only fallback to NVIDIA NIM.

### Phase 8: Authoritative Control Fabric & SQS Worker Decoupling
- Implement Amazon SQS task dispatching in `AgentControlFabric`.
- Deploy ECS Fargate Worker Pool consuming from SQS with automatic scaling.
- Correct Agent #23 manifest mapping to `HardwareThermalAgent`.

### Phase 9: Consolidated FastAPI API/BFF Deployment
- Consolidate all 50 endpoints from legacy Render microservices into a unified FastAPI API/BFF.
- Deploy API container on ECS Fargate behind Application Load Balancer.
- Implement Redis-backed Server-Sent Events (SSE) for real-time task progress.

### Phase 10: Next.js Frontend Deployment, CloudFront & Go-Live
- Compile Next.js 16 web application and upload static assets to S3.
- Configure CloudFront CDN distribution with AWS WAF rules and Route 53 DNS.
- Execute end-to-end integration validation from browser to agents.
