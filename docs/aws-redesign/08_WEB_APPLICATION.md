# Workline Web Application Architecture (Next.js 16)

**Document ID:** `WORKLINE-AWS-08`  
**Status:** CANONICAL FRONTEND SPECIFICATION  

---

## 1. Web-First Presentation Layer

The Workline Web Application (`frontend/`) is engineered as a responsive, modern engineering command center built on Next.js 16.2.9, React 19.2.4, Tailwind CSS v4, and Lucide icons.

### Core Architectural Rules:
1. **Zero Direct Database Access:**
   - The browser **MUST NEVER** connect directly to SurrealDB or Qdrant.
   - All interactions flow through the authenticated Workline API/BFF.
2. **Cognito Token Lifecycle:**
   - The web app manages Amazon Cognito user authentication via Amplify SDK / standard OAuth2 Authorization Code flow with PKCE.
   - Valid JWT tokens are attached as `Authorization: Bearer <token>` on all API requests.
3. **Real-time SSE Streaming:**
   - Long-running agent executions, thermal simulations, and multi-vendor procurement scans stream live logs and progress bars via Server-Sent Events (SSE) from `/api/v1/tasks/{task_id}/events`.
4. **Direct-to-S3 Presigned Asset Transfers:**
   - When uploading large CAD or Gerber archives, the web frontend requests a pre-signed S3 PUT URL from the API and uploads directly to S3.
   - Downloads of completed reports and 3D models use pre-signed GET URLs, avoiding API Gateway memory saturation.

---

## 2. Frontend Hosting Architecture on AWS

- **Static Asset Delivery:** Compiled Next.js client bundles (`_next/static/*`), icons, and images are hosted on Amazon S3 and distributed globally through **Amazon CloudFront**.
- **SSR / Dynamic Pages:** Next.js server-side rendering routes are containerized on ECS Fargate or hosted via AWS Amplify Hosting Gen 2.
- **Cache Invalidation:** Automated CI/CD invalidates CloudFront distribution paths on every production deployment.
