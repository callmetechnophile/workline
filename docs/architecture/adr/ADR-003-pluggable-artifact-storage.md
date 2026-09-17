# ADR-003: Pluggable Artifact Storage Abstraction

## Status
Accepted

## Context
Binary and file artifacts (Gerbers, schematics, simulation plots, procurement quote CSVs) were scattered across local temporary directories without a unified metadata indexing system or cloud storage compatibility.

## Decision
Introduce `backend/workline/artifacts/` with:
1. `ArtifactStore` abstract interface separating storage backends from business logic.
2. `FilesystemArtifactStore` for local development, tests, and CI/CD.
3. `S3ArtifactStore` with graceful local fallback if AWS credentials or S3 buckets are not configured.
4. Content hashing (SHA-256) and project-scoped storage organization.

## Consequences
- Single unified interface for saving and retrieving engineering artifacts.
- Zero local dependencies on external cloud providers during development and automated tests.
