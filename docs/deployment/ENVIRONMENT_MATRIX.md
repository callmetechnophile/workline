# Workline AI — Complete Environment Variable Matrix

This matrix serves as the authoritative specification for all environment variables across the Workline AI deployment topology:
- **Netlify**: Frontend Next.js client bundle (receives **ONLY** `NEXT_PUBLIC_*` variables)
- **R1**: Core Gateway / Control Plane (API Router, Session Auth, Mesh Dispatch)
- **R2**: AI / Google ADK / PaperBanana (Gemini Model Execution & Research)
- **R3**: Knowledge / Documents / Vector DB (Qdrant & SurrealDB)
- **R4**: Engineering / Simulation (Thermal PINN, SPICE, Multi-Physics)
- **R5**: Procurement / BOM / x402 (Algorand USDC Settlement, Supplier APIs)

---

## 1. Environment Variable Matrix

| Variable Name | R1 | R2 | R3 | R4 | R5 | Netlify | Classification | Requirement | Default / Purpose |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|---|---|
| `PORT` | ✓ | ✓ | ✓ | ✓ | ✓ | — | Deployment Config | Required | Dynamic port injected by Render (10000..10005) |
| `WORKLINE_ENV` | ✓ | ✓ | ✓ | ✓ | ✓ | — | Public Config | Required | `production`, `development`, or `test` |
| `WORKLINE_BASE_URL` | ✓ | — | — | — | — | — | Public Config | Required | Public URL of Workline API / app |
| `WORKLINE_CORS_ORIGINS` | ✓ | — | — | — | — | — | Public Config | Required | Allowed browser origins (`https://worklineai.netlify.app`) |
| `WORKLINE_SERVICE_AUTH_KEY` | ✓ | ✓ | ✓ | ✓ | ✓ | — | Service-to-Service Secret | Required | Shared mesh bearer token for internal auth |
| `WORKLINE_R1_URL` | ✓ | — | — | — | — | — | Deployment Config | Required | Gateway URL (`http://localhost:10000`) |
| `WORKLINE_R2_URL` | ✓ | — | — | — | — | — | Deployment Config | Required | Downstream R2 URL (`http://workline-ai-agents:10002`) |
| `WORKLINE_R3_URL` | ✓ | — | — | ✓ | ✓ | — | Deployment Config | Required | Downstream R3 URL (`http://workline-knowledge-documents:10003`) |
| `WORKLINE_R4_URL` | ✓ | — | — | — | ✓ | — | Deployment Config | Required | Downstream R4 URL (`http://workline-engineering-simulation:10004`) |
| `WORKLINE_R5_URL` | ✓ | — | — | — | — | — | Deployment Config | Required | Downstream R5 URL (`http://workline-procurement-service:10005`) |
| `R2_SERVICE_TOKEN` | ✓ | ✓ | — | — | — | — | Service-to-Service Secret | Optional | Granular token override for R2 |
| `R3_SERVICE_TOKEN` | ✓ | — | ✓ | ✓ | ✓ | — | Service-to-Service Secret | Optional | Granular token override for R3 |
| `R4_SERVICE_TOKEN` | ✓ | — | — | ✓ | ✓ | — | Service-to-Service Secret | Optional | Granular token override for R4 |
| `AWS_REGION` | — | ✓ | — | — | — | — | Public Config | Required (R2) | Amazon Bedrock AWS Region (`us-east-1`) |
| `AWS_ACCESS_KEY_ID` | — | ✓ | — | — | — | — | Backend Secret | Optional (IAM Role) | AWS IAM Access Key for Bedrock |
| `AWS_SECRET_ACCESS_KEY` | — | ✓ | — | — | — | — | Backend Secret | Optional (IAM Role) | AWS IAM Secret Key for Bedrock |
| `BEDROCK_RESEARCH_MODEL_ID` | — | ✓ | — | — | — | — | Public Config | Optional | Bedrock DeepSeek Model ID |
| `BEDROCK_FAST_CODE_MODEL_ID` | — | ✓ | — | — | — | — | Public Config | Optional | Bedrock Claude Haiku Model ID |
| `BEDROCK_REASONING_MODEL_ID` | — | ✓ | — | — | — | — | Public Config | Optional | Bedrock Claude Sonnet Model ID |
| `BEDROCK_REPORT_MODEL_ID` | — | ✓ | — | — | — | — | Public Config | Optional | Bedrock Claude Sonnet Report Model ID |
| `BEDROCK_IMAGE_MODEL_ID` | — | ✓ | — | — | — | — | Public Config | Optional | Bedrock Image Model ID (`amazon.nova-canvas-v1:0`) |
| `SARVAM_API_KEY` | — | ✓ | — | — | — | — | 3rd Party API Key | Optional | Indic vernacular speech-to-text / text-to-speech |
| `QDRANT_URL` | — | — | ✓ | — | — | — | Database Config | Required (R3) | Qdrant vector database endpoint |
| `QDRANT_API_KEY` | — | — | ✓ | — | — | — | Database Credential | Optional/Cloud | Qdrant Cloud cluster auth token |
| `SURREALDB_URL` | — | — | ✓ | — | — | — | Database Config | Required (R3) | SurrealDB endpoint (`ws://...:8000/rpc`) |
| `SURREALDB_USER` | — | — | ✓ | — | — | — | Database Credential | Required (R3) | SurrealDB username |
| `SURREALDB_PASSWORD` | — | — | ✓ | — | — | — | Database Credential | Required (R3) | SurrealDB password |
| `SURREALDB_NAMESPACE` | — | — | ✓ | — | — | — | Database Config | Required (R3) | SurrealDB namespace (`workline`) |
| `SURREALDB_DATABASE` | — | — | ✓ | — | — | — | Database Config | Required (R3) | SurrealDB database (`workline`) |
| `WORKLINE_EMBEDDING_PROVIDER` | — | — | ✓ | — | — | — | Public Config | Optional | `local`, `gemini`, `huggingface` |
| `WORKLINE_X402_ENABLED` | ✓ | — | — | — | ✓ | — | Public Config | Required | `true` or `false` |
| `WORKLINE_X402_NETWORK` | ✓ | — | — | — | ✓ | — | Public Config | Required | `algorand-mainnet` or `algorand-testnet` |
| `WORKLINE_X402_ASSET` | ✓ | — | — | — | ✓ | — | Public Config | Required | `USDC` |
| `WORKLINE_X402_ASSET_ID` | ✓ | — | — | — | ✓ | — | Public Config | Required | `31566704` (Mainnet) or `10458941` (Testnet) |
| `WORKLINE_X402_PAY_TO` | ✓ | — | — | — | ✓ | — | Blockchain Address | Required | Workline 58-char Algorand treasury address |
| `WORKLINE_X402_FACILITATOR_URL` | ✓ | — | — | — | ✓ | — | 3rd Party Config | Required | `https://facilitator.goplausible.com` |
| `WORKLINE_X402_TTL_MINUTES` | ✓ | — | — | — | ✓ | — | Public Config | Optional | Challenge TTL (default `30` mins) |
| `WORKLINE_X402_MODE` | ✓ | — | — | — | ✓ | — | Public Config | Required | `production`, `testnet`, `local` |
| `COINGECKO_API_URL` | ✓ | — | — | — | ✓ | — | 3rd Party Config | Optional | `https://api.coingecko.com/api/v3` |
| `WORKLINE_NEXAR_CLIENT_ID` | — | — | — | — | ✓ | — | 3rd Party API Key | Optional | Altium Nexar component API ID |
| `WORKLINE_NEXAR_CLIENT_SECRET`| — | — | — | — | ✓ | — | 3rd Party API Key | Optional | Altium Nexar component API secret |
| `WORKLINE_NEXAR_ENDPOINT` | — | — | — | — | ✓ | — | 3rd Party Config | Optional | `https://api.nexar.com/graphql` |
| `WORKLINE_NEXAR_ENABLED` | — | — | — | — | ✓ | — | Public Config | Optional | `false` |
| `WORKLINE_INVITATION_KEY_V1` | ✓ | — | — | — | — | — | Backend Secret | Required (R1) | 256-bit AES key for invitation tokens |
| `TEAM_JOIN_CODE_SECRET` | ✓ | — | — | — | — | — | Backend Secret | Required (R1) | HMAC-SHA-256 secret for team join codes |
| `TEAM_JOIN_CODE_TTL_SECONDS` | ✓ | — | — | — | — | — | Public Config | Optional | Join code TTL in seconds (default `86400`) |
| `TEAM_RSA_PUBLIC_KEY` | ✓ | — | — | — | — | — | Public Config | Optional | RSA-3072 public key in PEM format |
| `TEAM_RSA_PRIVATE_KEY` | ✓ | — | — | — | — | — | Backend Secret | Optional | RSA-3072 private key in PEM format |
| `CLERK_SECRET_KEY` | ✓ | — | — | — | — | — | Backend Secret | Required (R1) | Clerk server-side JWT verification key |
| `CLERK_JWKS_URL` | ✓ | — | — | — | — | — | Public Config | Optional | Custom Clerk JWKS validation URL |
| `NEXT_PUBLIC_API_URL` | — | — | — | — | — | ✓ | Public Config | Required (Netlify) | Backend Gateway URL for browser |
| `NEXT_PUBLIC_SITE_URL` | — | — | — | — | — | ✓ | Public Config | Required (Netlify) | Netlify site origin |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | — | — | — | — | — | ✓ | Public Config | Required (Netlify) | Clerk frontend widget key |
| `GITHUB_TOKEN` | — | — | — | — | — | — | 3rd Party API Key | Optional (CLI) | GitHub personal access token for CLI |
| `WORKLINE_API_URL` | — | — | — | — | — | — | Public Config | Optional (CLI) | Target API gateway URL for CLI |
| `WORKLINE_AUTH_TOKEN` | — | — | — | — | — | — | Backend Secret | Optional (CLI) | CLI authenticated bearer token |

---

## 2. Minimum Secret Distribution Rules

1. **Frontend / Netlify Isolation**:
   - The browser receives **ONLY** variables prefixed with `NEXT_PUBLIC_`.
   - **Zero** backend secrets (`GEMINI_API_KEY`, `SURREALDB_PASSWORD`, `WORKLINE_SERVICE_AUTH_KEY`, `CLERK_SECRET_KEY`, etc.) are ever provided to Netlify or frontend builds.

2. **R2 AI Isolation**:
   - `GEMINI_API_KEY` is provisioned exclusively on the R2 AI microservice.
   - R1, R3, R4, and R5 do not receive or require `GEMINI_API_KEY`.

3. **R3 Knowledge Isolation**:
   - SurrealDB and Qdrant database credentials are provisioned exclusively on R3.
   - Other microservices communicate with R3 over the authenticated service mesh.

4. **Service Mesh Mutual Authentication**:
   - `WORKLINE_SERVICE_AUTH_KEY` is shared only between internal backend containers on Render private networking.
