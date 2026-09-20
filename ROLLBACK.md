# Rollback Strategy & Disaster Recovery: WorkflowGuide AI / ArmourFlow AI

## Overview
This document specifies the rollback procedures, fallback mechanisms, and zero-downtime recovery strategy for the AWS-native migration of WorkflowGuide AI / ArmourFlow AI.

---

## 1. Zero-Disruption Dual-Run Architecture

During the migration window, both hosting environments remain operational:
- **Legacy Environment:** Render (Backend) + Vercel (Frontend).
- **Target AWS Environment:** AWS API Gateway / Lambda + S3 / CloudFront.

Traffic shifting is governed via Route 53 weighted DNS records:
- **Phase 1 (Canary):** 90% Render / 10% AWS API Gateway.
- **Phase 2 (Fifty-Fifty):** 50% Render / 50% AWS API Gateway.
- **Phase 3 (Cutover):** 100% AWS API Gateway.

---

## 2. Immediate Rollback Triggers

Initiate immediate rollback if any of the following occur during deployment or verification:
1. API Gateway 5xx error rate exceeds **1.0%** over a 5-minute window.
2. Step Functions multi-agent execution failure rate exceeds **2.0%**.
3. P95 latency on `/api/projects/*` exceeds **2500ms**.
4. ArmorIQ policy verification fails or reports signature verification discrepancies.
5. SurrealDB graph query timeouts exceed **500ms**.

---

## 3. Step-by-Step Rollback Execution

### Step 1: Instant DNS Weight Shift (60-second recovery)
Revert Route 53 DNS weighting back to legacy Render/Vercel endpoints:
```bash
aws route53 change-resource-record-sets \
  --hosted-zone-id <HOSTED_ZONE_ID> \
  --change-batch file://infra/aws/rollback-dns.json
```

### Step 2: CloudFront Origin Failover
If CloudFront is already the primary edge distributor, point the origin from API Gateway back to the fallback Render R1 gateway origin in the CloudFront distribution settings.

### Step 3: SAM / CloudFormation Rollback
To roll back an infrastructure update to the previous stable CloudFormation changeset:
```bash
sam deploy --config-file infra/aws/samconfig.toml --config-env <ENV> --no-execute-changeset
# Or via AWS CloudFormation CLI:
aws cloudformation rollback-stack --stack-name workline-platform-<ENV>
```

### Step 4: SQS Drain & Re-queue
If tasks failed during the transition:
1. Examine the Dead Letter Queue (`workline-jobs-dlq-<ENV>`).
2. Run the dead-letter redrive tool to reprocess failed jobs once stable:
   ```bash
   aws sqs start-message-move-task \
     --source-arn <DLQ_ARN> \
     --destination-arn <QUEUE_ARN>
   ```

---

## 4. Data Consistency & State Protection

- **SurrealDB:** Because SurrealDB remains the authoritative graph database throughout migration, no database restore or rollback is needed. Graph writes remain valid across both old and new backend instances.
- **Qdrant:** Vector indexes remain synchronized and unaffected by compute rollbacks.
- **DynamoDB:** Idempotency locks automatically expire via TTL (300 seconds), preventing locked requests during a failover.
- **S3:** All S3 objects are versioned with SSE-KMS encryption; accidental deletes can be reverted by removing delete markers.
