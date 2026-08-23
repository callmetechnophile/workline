# Workline AI — Central AI Architecture: Amazon Bedrock Standardization

## 1. Architectural Overview

Amazon Bedrock is the **primary, centralized, and authoritative AI model provider** for the Workline AI hardware engineering platform.

Direct external API dependencies (OpenAI, direct Anthropic, direct DeepSeek, direct Google Gemini, direct Google Imagen) have been completely removed and standardized through Amazon Bedrock.

```
                         WORKLINE
                            |
                            v
                           R2
                    AI / ADK Runtime
                            |
                     MODEL ROUTER
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
        DeepSeek V3    Claude Haiku   Claude Sonnet
             |              |              |
             +--------------+--------------+
                            |
                            v
                    AMAZON BEDROCK
                            |
                            v
                  AI MODEL EXECUTION
```

---

## 2. Model Roles & Configuration

All model IDs are configuration-driven via environment variables, allowing seamless regional deployment and version switching:

| Role | Environment Variable | Default Bedrock Model ID | Provider Family | Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **Research & Reasoning** | `BEDROCK_RESEARCH_MODEL_ID` | `deepseek.r1-v1:0` / `deepseek.v3` | DeepSeek | Academic synthesis, contradiction discovery |
| **Fast Code & Tools** | `BEDROCK_FAST_CODE_MODEL_ID` | `anthropic.claude-3-5-haiku-20241022-v1:0` | Anthropic | Fast coding, syntax verification, lightweight transforms |
| **Complex Reasoning** | `BEDROCK_REASONING_MODEL_ID` | `anthropic.claude-3-5-sonnet-20241022-v2:0` | Anthropic | Multi-physics, PINN validation, architecture design |
| **Report Generation** | `BEDROCK_REPORT_MODEL_ID` | `anthropic.claude-3-5-sonnet-20241022-v2:0` | Anthropic | Executive summaries, audit log analysis |
| **Engineering Visuals** | `BEDROCK_IMAGE_MODEL_ID` | `amazon.nova-canvas-v1:0` | Amazon | Block diagrams, architecture charts, PCB visuals |

---

## 3. Subsystem Architecture

### `backend/workline/ai/bedrock/`
1. **`client.py` (`BedrockClient`)**:
   - Central thread-safe boto3 client wrapping `bedrock-runtime`.
   - Exponential backoff with jitter on `ThrottlingException`, `ModelTimeoutException`, and transient 5xx errors.
   - Configured connection and read timeouts.
   - Converts raw AWS ClientErrors into normalized domain exceptions.

2. **`router.py` (`BedrockModelRouter`)**:
   - High-level interface called across all Workline agents and services:
     - `model_router.research(prompt)`
     - `model_router.fast_code(prompt)`
     - `model_router.reasoning(prompt)`
     - `model_router.report_generation(prompt)`
     - `model_router.image_generation(prompt)`

3. **Adapters**:
   - `adapters/anthropic.py`: Claude Messages API schema translation (`anthropic_version: "bedrock-2023-05-31"`).
   - `adapters/deepseek.py`: DeepSeek prompt and reasoning token parser.
   - `adapters/image.py`: Amazon Nova Canvas / Titan Image Generator text-to-image adapter.

4. **`schemas.py` (`AIResponse`)**:
   - Normalized response container: `text`, `model_id`, `provider`, `request_id`, `usage` (`prompt_tokens`, `completion_tokens`, `total_tokens`), `latency_ms`, `finish_reason`.

---

## 4. Google ADK & PaperBanana Integration

- **Google ADK**: Used purely as an agent orchestration, tool-calling, and lifecycle runtime framework. Google ADK agents invoke tools that delegate all generative reasoning to `BedrockModelRouter`.
- **PaperBanana**: Visual diagram renderer powered by Amazon Bedrock (`amazon.nova-canvas-v1:0` or Bedrock Claude SVG generation). Direct Gemini/Imagen APIs are completely removed.

---

## 5. Security & Credential Isolation

- **Backend-Only**: AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) and Bedrock access are restricted exclusively to the R2 AI microservice.
- **Zero Frontend Leaks**: No AWS keys, Gemini keys, or model API keys are included in the Netlify frontend bundle or exposed to browser clients.
