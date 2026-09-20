# Workline Production Threat Model & STRIDE Analysis

**Document ID:** `WORKLINE-THREAT-MODEL`  
**Status:** APPROVED SECURITY SPECIFICATION  

---

## 1. System Scope & Assets Under Protection

This threat model protects the Workline AWS Web Platform, including:
1. **Authoritative Engineering State:** Hardware designs, BOMs, trade studies, and requirements in **SurrealDB**.
2. **Proprietary Vector Embeddings:** Engineering datasheets and component indexes in **Qdrant**.
3. **Engineering Artifacts:** High-value CAD STEP models, Gerber files, and simulation datasets in **Amazon S3**.
4. **Inference & AI Integrity:** Bedrock LLM gateway prompts, agent tools, and decision synthesis.
5. **Customer Identities & Sessions:** Cognito user credentials, JWT tokens, and RBAC boundaries.

---

## 2. STRIDE Threat Analysis & Concrete Mitigations

| Threat Category | Potential Attack Vector | Impact | Workline Production Mitigation |
| :--- | :--- | :---: | :--- |
| **Spoofing** | Forged or expired JWT presented to API endpoints. | Critical | Strict RS256 signature verification against Cognito JWKS. Signature validation failures immediately return HTTP 401. Zero unverified fallbacks. |
| **Tampering** | Parameter tampering or SurrealQL injection in API payloads. | High | Pydantic model validation on all inputs. Strictly parameterized SurrealQL queries via SDK (`vars={"project_id": ...}`). |
| **Repudiation** | An engineer denies approving a critical BOM change or thermal override. | High | Immutable append-only audit events logged to SurrealDB `audit_event` table and mirrored to CloudWatch Logs with SHA-256 hashes. |
| **Information Disclosure** | Direct public internet access to SurrealDB or Qdrant. | Critical | **Databases deployed strictly in Isolated Data Subnets with NO internet gateway routing.** Browser never connects to databases. Security groups block all external IPs. |
| **Information Disclosure** | Unauthorized download of proprietary CAD or Gerber files. | Critical | S3 buckets block all public access. Downloads require short-lived (15-min) pre-signed URLs issued only after RBAC check. |
| **Denial of Service** | Volumetric HTTP flooding or malformed requests aimed at API or workers. | High | AWS WAF rate-limiting rules at CloudFront edge. SQS queue buffers heavy compute workloads, preventing API starvation. |
| **Elevation of Privilege**| Low-privileged viewer attempts to trigger hardware fabrication or agent workflows. | High | RBAC middleware enforces explicit role scopes (`project:lead`, `system:admin`) before dispatching Control Fabric tasks. |
| **Prompt Injection** | Adversarial prompt embedded in uploaded datasheet to hijack agent reasoning. | High | AWS Bedrock Guardrails scan incoming texts. Agents validate tool outputs against strict Pydantic schemas before writing to SurrealDB. |

---

## 3. Database-Specific Threat Defenses

### SurrealDB Security Controls:
- Authentication required on every connection via root/namespace credentials.
- Passwords dynamically injected from AWS Secrets Manager via ECS task secrets.
- Subnet isolation: Only ECS API and Worker security groups can access port 8000.
- Daily cryptographic S3 backup exports with KMS SSE.

### Qdrant Security Controls:
- API key authentication enforced on HTTP (6333) and gRPC (6334) ports.
- Subnet isolation: Zero public internet access.
- Ingestion validation: Vector dimensions strictly validated against collection schema before upsert.
