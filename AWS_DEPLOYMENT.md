# AWS Deployment Guide: WorkflowGuide AI / ArmourFlow AI

## Overview
This document guides the deployment of the WorkflowGuide AI / ArmourFlow AI platform to AWS using AWS SAM, CloudFront, API Gateway, Lambda, Step Functions, SQS, SNS, EventBridge, S3, DynamoDB, Cognito, and CloudWatch.

---

## Prerequisites
1. **AWS CLI** configured (`aws configure`) with administrative permissions.
2. **AWS SAM CLI** installed (`sam --version` >= 1.100.0).
3. **Docker** installed and running (for building Lambda container artifacts or LocalStack).
4. **Node.js 20+** and **Python 3.11+**.

---

## 1. Local Emulation with LocalStack
For rapid local verification without provisioning cloud resources:

```bash
# Start LocalStack, SurrealDB, and Qdrant
docker-compose -f docker-compose.localstack.yml up -d

# Verify LocalStack health
curl http://localhost:4566/_localstack/health
```

---

## 2. Deploying AWS Infrastructure via AWS SAM

### Step 1: Validate SAM Template
```bash
sam validate -t infra/aws/template.yaml
```

### Step 2: Build Application
```bash
sam build -t infra/aws/template.yaml --use-container
```

### Step 3: Deploy to Environment

#### Development Deployment:
```bash
sam deploy --config-file infra/aws/samconfig.toml --config-env default
```

#### Staging Deployment:
```bash
sam deploy --config-file infra/aws/samconfig.toml --config-env staging
```

#### Production Deployment:
```bash
sam deploy --config-file infra/aws/samconfig.toml --config-env production
```

SAM will output:
- `ApiEndpoint`: The live API Gateway base URL.
- `JobQueueUrl`: SQS Queue URL for asynchronous workloads.
- `ArtifactsBucketName`: S3 Bucket name for file storage.
- `StepFunctionsStateMachineArn`: State Machine ARN for multi-agent workflows.

---

## 3. Frontend Deployment & CloudFront Integration

### Step 1: Set Frontend Environment Variables
In `frontend/.env.production`:
```ini
NEXT_PUBLIC_API_URL=https://<api-id>.execute-api.us-east-1.amazonaws.com/prod
```

### Step 2: Build Frontend
```bash
cd frontend
npm install
npm run build
```

### Step 3: Hosting via AWS Amplify or S3 + CloudFront
1. Connect repository to **AWS Amplify Hosting** or sync `out/` directory to S3:
   ```bash
   aws s3 sync ./out s3://workline-frontend-prod/ --delete
   ```
2. Invalidate CloudFront cache:
   ```bash
   aws cloudfront create-invalidation --distribution-id <DISTRIBUTION_ID> --paths "/*"
   ```

---

## 4. Post-Deployment Verification Checklist

1. **Health Check:**
   ```bash
   curl -i https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/health
   ```
   *Expected Response:* `HTTP 200 OK {"status": "healthy"}`

2. **Step Functions Execution:**
   Trigger test execution from AWS Console or CLI:
   ```bash
   aws stepfunctions start-execution \
     --state-machine-arn <STATE_MACHINE_ARN> \
     --input '{"project_id": "test-proj", "user_intent": "Build an IoT environmental monitor"}'
   ```

3. **CloudWatch Metrics Dashboard:**
   Navigate to CloudWatch Console -> Dashboards -> `Workline-Platform-prod` to monitor latency, invocations, and ArmorIQ security violations.
