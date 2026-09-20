# Workline Data & Storage Architecture: SurrealDB, Qdrant & S3

**Document ID:** `WORKLINE-AWS-04`  
**Status:** CANONICAL DATA SPECIFICATION  

---

## 1. Non-Negotiable Database Responsibility Boundaries

Workline maintains a strict, unambiguous separation of data responsibilities:

```
                 WORKLINE DATA PLATFORM
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
          SURREALDB               QDRANT
       AUTHORITATIVE STATE      VECTOR SEARCH
              │                     │
              │                     │
       Graph / relational      Embeddings /
       engineering state       semantic retrieval
              │                     │
              └──────────┬──────────┘
                         ▼
                  CONTROL FABRIC
                         │
                         ▼
                    APPLICATION
```

- **SurrealDB:** Authoritative Workline engineering/application state and graph database.
- **Qdrant:** Authoritative vector search engine and semantic similarity retrieval.
- **Amazon S3:** Large binary/object artifacts (STEP CAD, Gerber, thermal logs, DB backups). **S3 MUST NOT replace SurrealDB as authoritative state, nor Qdrant as vector search.**
- **Amazon ElastiCache Redis:** Ephemeral caching and real-time SSE pub/sub only. **Redis MUST NOT store authoritative state.**

---

## 2. SurrealDB Deployment Evaluation on AWS

SurrealDB serves as the core multi-model graph and relational engine. We evaluate four deployment models:

| Evaluation Criteria | Option A: Surreal Cloud on AWS (VPC Peered) | Option B: Self-Hosted on AWS (ECS/EC2 + EBS gp3) | Option C: SurrealDB on Amazon EKS | Option D: Distributed SurrealDB + TiKV on AWS |
| :--- | :--- | :--- | :--- | :--- |
| **Workload Fit** | High (fully managed SurrealDB v2 instance in AWS region) | Very High (direct control over RocksDB engine, IOPS, and memory) | Medium (high infrastructure overhead for a single DB workload) | Low (excessive distributed complexity for current Workline scale) |
| **Persistence** | Managed by SurrealDB Cloud SLA | Persistent EBS gp3 volume formatted ext4, retained on task restart | Persistent Volume Claims (EBS CSI driver) | Distributed TiKV storage across multiple AZs |
| **Latency** | Low (2–4 ms via VPC Peering / PrivateLink) | Ultra-Low (< 1.5 ms intra-VPC private subnet) | Low (< 2 ms within EKS pod network) | Higher (multi-hop distributed consensus) |
| **Operational Complexity**| Very Low (automated patches and scaling) | Low-Medium (managed container definition, EBS snapshot automation) | Very High (Kubernetes cluster management, upgrades, ingress) | Very High (managing TiKV cluster, placement drivers, PD nodes) |
| **Monthly Cost** | ~$50–$150/mo managed tier | ~$35–$60/mo (t4g.xlarge / ECS Fargate + 100GB gp3) | ~$140+/mo ($73 for EKS control plane + EC2 worker nodes) | ~$300+/mo (minimum 3 TiKV nodes + 3 PD nodes + compute) |
| **Backup / Recovery** | Managed automated backups | Automated daily/hourly S3 export snapshots via cron/EventBridge | Velero or CSI Volume Snapshots | TiKV BR tool to S3 |
| **Security & Network** | PrivateLink endpoint in Workline VPC | Strictly isolated private subnet, zero public IP, TLS enabled | Private Kubernetes namespace and NetworkPolicies | Private VPC subnets |

### Architectural Selection & Blueprint:
Workline selects **Option B (Self-Hosted on AWS Infrastructure with ECS Fargate or dedicated EC2 + EBS gp3 storage)** as the primary deployment blueprint, with **Option A (Surreal Cloud with VPC Peering)** as an approved enterprise alternative.

#### Self-Hosted SurrealDB AWS Blueprint:
1. **Compute & Storage:**
   - Deployed on an ECS Fargate task (or EC2 instance) with an attached Amazon EBS gp3 volume mounted at `/var/lib/surrealdb/data`.
   - Command: `surreal start --bind 0.0.0.0:8000 --user $SURREAL_ROOT_USER --pass $SURREAL_ROOT_PASS file:/var/lib/surrealdb/data/workline.db`
2. **Network Isolation:**
   - Located exclusively in the **Isolated Data Subnet** (no internet route table, no public IP).
   - Internal DNS: `surrealdb.workline.internal:8000` via AWS Cloud Map / Route 53 Private Hosted Zone.
   - Security Group ingress restricted exclusively to the API and Worker Security Groups on port 8000.
3. **Backup & Disaster Recovery:**
   - Nightly automated cron/EventBridge Lambda triggers: `surreal export --conn http://surrealdb.workline.internal:8000 --ns workline --db workline s3://workline-backups-kms/surrealdb/backup-$(date +%Y%m%d%H%M).sql`.
   - Amazon EBS Lifecycle Manager (DLM) takes automated hourly EBS snapshots with 30-day retention.
4. **Monitoring & Health:**
   - Container health check: `GET http://localhost:8000/health` (HTTP 200).
   - CloudWatch Alarm on container CPU > 80% or memory > 80%.

---

## 3. Qdrant Deployment Evaluation on AWS

Qdrant provides high-performance vector similarity search. We evaluate three deployment models:

| Evaluation Criteria | Option A: Qdrant Cloud on AWS (VPC Peered) | Option B: Self-Hosted on AWS (ECS/EC2 + EBS gp3) | Option C: Qdrant on Amazon EKS |
| :--- | :--- | :--- | :--- |
| **Workload Fit** | High (fully managed Qdrant cluster in AWS region) | Very High (optimized Rust runtime with dedicated RAM/EBS) | Medium (unnecessary K8s overhead for single cluster) |
| **Persistence** | Managed Qdrant Cloud disk storage | Persistent EBS gp3 volume mounted at `/qdrant/storage` | PVC via EBS CSI driver |
| **Latency** | Low (2–4 ms over VPC Peering) | Ultra-Low (< 1.5 ms intra-VPC) | Low (< 2 ms intra-cluster) |
| **Operational Overhead** | Minimal (fully managed) | Low (single container with persistent storage) | Very High (K8s operational burden) |
| **Monthly Cost** | ~$45–$90/mo | ~$35–$70/mo (t4g.large or ECS Fargate 4vCPU/16GB) | ~$150+/mo (EKS cluster cost + nodes) |
| **Backup / Recovery** | Qdrant Cloud automated snapshots | Qdrant Snapshot API (`POST /collections/{name}/snapshots`) to S3 | Snapshot volume backups |

### Architectural Selection & Blueprint:
Workline selects **Option B (Self-Hosted on AWS Infrastructure with ECS/EC2 + persistent EBS gp3 volume)** as the primary blueprint, with **Option A (Qdrant Cloud with VPC Peering)** as an approved enterprise alternative.

#### Self-Hosted Qdrant AWS Blueprint:
1. **Container & Volume:**
   - Container image: `qdrant/qdrant:v1.11.0` (official image).
   - Volume: Amazon EBS gp3 (3000 IOPS, 125 MB/s throughput) mounted at `/qdrant/storage`.
   - Environment variables: `QDRANT__SERVICE__HTTP_PORT=6333`, `QDRANT__SERVICE__API_KEY=$QDRANT_API_KEY`.
2. **Network Isolation:**
   - Deployed in the **Isolated Data Subnet**; zero public internet exposure.
   - Internal DNS: `qdrant.workline.internal:6333`.
   - Ingress restricted strictly to API and Worker security groups on port 6333 (HTTP) and 6334 (gRPC).
3. **Automated Snapshots:**
   - Daily Lambda calls `POST http://qdrant.workline.internal:6333/collections/{collection}/snapshots` and streams the resulting snapshot files directly to `s3://workline-backups-kms/qdrant/`.
4. **Health Probes:**
   - Health checks hit `GET /livez` and `GET /readyz`.

---

## 4. Preservation of Schemas & Zero Database Migration

**DATABASE MIGRATION RULE: ZERO DATABASE MIGRATION.**  
Workline does NOT migrate authoritative state to DynamoDB, Aurora, RDS, PostgreSQL, MySQL, OpenSearch, Neptune, or any other database.

All existing schemas, record identifiers, and collections are 100% preserved:

### Preserved SurrealDB Structures:
- Record ID Format: `project:<uuid>`, `task:<uuid>`, `workflow:<uuid>`, `user:<uuid>`, `bom_item:<uuid>`.
- Relational Fields: Foreign key references and embedded objects remain intact.
- Graph Topology: Edges (`has_optimization`, `evaluates_candidate`, `has_pareto_frontier`, `BLOCKS`, `DEPENDS_ON`, `PRODUCES`) preserved without modification.

### Preserved Qdrant Collections:
- `workline_documents` (vectors, chunk text, document metadata, source URLs).
- `workline_components` (vectors, MPN, manufacturer, specs, pinouts).
- `workline_projects` (domain summary vectors, project IDs).
- `workline_research` (trade-study embeddings, findings, evidence references).

---

## 5. Amazon S3 Artifact Storage Integration

Large binary files that exceed reasonable database record sizes are offloaded to Amazon S3:

- **Bucket Name:** `workline-artifacts-<account_id>-<region>`
- **Encryption:** Server-Side Encryption with AWS KMS (SSE-KMS, Customer-Managed Key).
- **Versioning:** Enabled to prevent accidental overwrites of engineering deliverables.
- **Path Hierarchy:**
  ```
  s3://workline-artifacts/
  ├── projects/{project_id}/
  │   ├── cad/
  │   │   ├── assembly.step
  │   │   └── enclosure.stl
  │   ├── pcb/
  │   │   ├── gerber_archive.zip
  │   │   └── schematic.kicad_sch
  │   ├── thermal/
  │   │   ├── simulation_field.npz
  │   │   └── heatmap_contour.png
  │   └── reports/
  │       └── compliance_audit.pdf
  └── backups/
      ├── surrealdb/
      └── qdrant/
  ```
- **Access Pattern:** The browser NEVER accesses S3 directly via raw credentials. The API/BFF generates time-bound (15-minute) pre-signed URLs (`GET` for downloading, `PUT` for uploading) after verifying user RBAC permissions.
