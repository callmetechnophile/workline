# ADR-004: Centralized LLM Gateway & Offline Mock Provider

## Status
Accepted

## Context
Multiple modules attempted direct LLM invocation, leading to fragmented error handling and failures in CI/CD environments where AWS Bedrock credentials were not configured.

## Decision
Implement `backend/workline/llm/`:
1. `LLMGateway` providing unified completion interface with token usage and cost estimation.
2. `BedrockProvider` adapter for AWS Bedrock.
3. `LocalMockProvider` providing deterministic synthetic responses offline.
4. Automatic graceful fallback to `LocalMockProvider` when Bedrock credentials or network connections are unavailable.

## Consequences
- Tests and local development run reliably 100% offline.
- Token consumption and latency metrics are centralized.
