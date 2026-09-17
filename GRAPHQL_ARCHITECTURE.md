# ArmourFlow AI / WorkflowGuide AI: GraphQL Architectural Specification

## 1. Architectural Role & Boundary Principles

GraphQL serves as the **official Client and Application API Layer** for the ArmourFlow AI platform. It provides a strongly typed, introspectable, unified entry point for web consoles, desktop clients, mobile dashboards, IDE extensions, and automation scripts.

### 1.1 Strict Invariant Call Sequence
The platform strictly enforces the following unidirectional execution sequence:

`
+-------------------------------------------------------------+
| CLIENT / WEB CONSOLE / CLI / IDE EXTENSION                  |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| GRAPHQL API LAYER (Strawberry + FastAPI @ /graphql)         |
| - Authentication & Token Extraction                         |
| - AST Query Depth (<= 10) & Complexity Limiting             |
| - Context Propagation (GraphQLContext)                      |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| UNIFIED AGENT CONTROL FABRIC (AgentControlFabric)           |
| - Capability-Based Routing Engine                           |
| - Idempotency & Task Lifecycle State Machine                |
| - Tenant Isolation Boundary Checks                          |
| - Real-time Event Bus (FabricEventBus)                      |
+-------------------------------------------------------------+
                              |
         +--------------------+--------------------+
         |                                         |
         v                                         v
+------------------------+             +------------------------+
| ARMORIQ SECURITY CORE  |             | AUTHORITATIVE REGISTRY |
| - Scope Verification   |             | - 27 Domain Manifests  |
| - Permission Checks    |             | - Capability Index     |
| - Zero Secret Leaks    |             | - Importability Audits |
+------------------------+             +------------------------+
         |                                         |
         +--------------------+--------------------+
                              |
                              v
+-------------------------------------------------------------+
| EXECUTION RUNTIME & ADK LAYER                               |
| - Google Agent Development Kit (ADK) Runner                 |
| - A2A Inter-Agent Communication Bus                         |
| - Bindu Schema Contract Validation Engine                   |
+-------------------------------------------------------------+
                              |
         +--------------------+--------------------+
         |                                         |
         v                                         v
+------------------------+             +------------------------+
| SURREALDB CLIENT       |             | AMAZON BEDROCK RUNTIME |
| - Multi-model Graph    |             | - LLM Inferences       |
| - In-memory Fallback   |             | - Prompt Orchestration |
+------------------------+             +------------------------+
`

### 1.2 Anti-Patterns & Explicit Architecture Boundaries
To maintain decoupling and architectural integrity, the GraphQL API layer adheres to the following strict boundaries:
1. **No Direct Agent Execution**: Resolvers NEVER invoke gent.run(), import agent classes directly, or bypass the Control Fabric. All executions flow as asynchronous FabricTask submissions.
2. **No Direct Raw Database Mutation**: Resolvers do not write arbitrary records to SurrealDB; they interact exclusively via the PlatformDatabaseClient or delegated fabric tasks.
3. **No ArmorIQ Bypass**: Resolvers never skip tenant validation (project_id), role checks, or permission verification.
4. **No Secondary Event Bus**: Real-time subscriptions hook into the existing central FabricEventBus rather than spinning up isolated pub/sub mechanisms.
5. **Zero Fabrication Invariant**: Unverified facts or hallucinated metrics are strictly prohibited. Missing external connections fail gracefully into declared fallback modes.

---

## 2. Schema Architecture & Type System

The schema is built using **Strawberry GraphQL** with uto_camel_case=True, compiling clean, idiomatic GraphQL SDL with snake_case Python implementation.

### 2.1 Root Query Hierarchy
- systemHealth: Inspects application version, active environment, and all 13 diagnostic subsystems (including SurrealDB, Bedrock, ArmorIQ, ADK, A2A, Bindu, Harness, and GraphQL).
- gents: Enumerates the authoritative catalog of all 27 registered domain engineering agents.
- gent(id: String!): Retrieves complete manifest metadata, execution levels, dependencies, and permissions for a specific agent.
- gentHealth(id: String!): Performs live importability and entrypoint diagnostics on demand.
- capabilities: Lists all platform capabilities and maps each capability to providing agent IDs and names.
- 	ask(id: String!): Retrieves lifecycle state, execution progress, payload, and structured results for a specific task.
- 	asks(projectId: String, limit: Int): Queries tasks scoped to a project with hard limit protection (default 50, max 100).
- projects(limit: Int): Lists registered engineering projects.
- projectStatus(id: String!): Computes task metrics and release readiness verdict.
- ngineeringGraph(projectId: String!): Queries multi-model knowledge graph nodes and relational edges.
- valuationReport: Generates platform harness evaluation summaries across benchmarks.
- gentEvaluation(agentId: String!): Queries evaluation benchmark results for a single agent.

### 2.2 Root Mutation Hierarchy
- createTask(input: CreateTaskInput!): Submits a task to the Control Fabric by agent ID or dynamic capability.
- 
unCapabilityTask(input: RunCapabilityTaskInput!): High-level convenience mutation to run tasks based solely on capability name, eliminating client-to-agent tight coupling.
- cancelTask(taskId: String!): Requests graceful cancellation of queued or executing tasks.
- createProject(input: CreateProjectInput!): Initializes a new project record.
- createTechnicalDocument(input: CreateDocumentInput!): Submits a technical documentation generation job routed to Agent #27 (TechDocAgent).

### 2.3 Root Subscription Hierarchy
- 	askUpdated(taskId: String, projectId: String): An asynchronous event stream yielding FabricEventSubscriptionType notifications as tasks progress through PENDING -> QUEUED -> ROUTED -> AUTHORIZED -> EXECUTING -> COMPLETED / FAILED.

---

## 3. Security, Depth Limiting & Multitenancy

### 3.1 AST Query Depth & Complexity Limiting
To defend against nested Denial-of-Service (DoS) and cycle traversal attacks, Strawberry executes QueryDepthAndComplexityLimiter:
- **Max Query Depth**: 10 levels (configurable via GRAPHQL_MAX_QUERY_DEPTH). Queries exceeding this limit are rejected at parse time before execution begins.
- **Complexity Calculation**: Evaluates query fields, multipliers, and nested arguments.

### 3.2 Tenant Isolation
Every GraphQL query and mutation evaluates GraphQLContext extracted from request headers:
- x-project-id: Identifies tenant namespace.
- x-user-id: Authenticated actor.
- uthorization: Bearer token passed to ArmorIQ.
Cross-tenant task inspection or modification is blocked and raises AUTHORIZATION_ERROR.

### 3.3 Error Sanitization
Resolver errors are wrapped via create_graphql_error(message, code, details). Internal stack traces and database credentials are fully scrubbed from public error extensions.

---

## 4. CLI & Operational Commands

ArmourFlow CLI integrates first-class GraphQL operations:
- **Schema Export**:
  `ash
  armourflow graphql schema
  `
- **GraphQL HTTP Server**:
  `ash
  armourflow graphql serve --host 0.0.0.0 --port 10000
  `
