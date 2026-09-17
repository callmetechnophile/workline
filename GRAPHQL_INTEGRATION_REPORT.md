# ArmourFlow AI / WorkflowGuide AI: GraphQL Integration Report

## 1. Executive Summary
The GraphQL Client and Application API Layer has been fully designed, implemented, and verified for the ArmourFlow AI / WorkflowGuide AI platform. Operating as the official boundary between clients (web console, CLI, desktop tools, IDE plugins) and the platform core, the GraphQL layer exposes a strongly typed, declarative API while strictly preserving the integrity of the underlying architecture.

All operations flow strictly through the Unified Agent Control Fabric:
`CLIENT -> GraphQL -> Control Fabric -> ADK / Agents / SurrealDB / Bedrock / ArmorIQ`

Zero domain agents were modified, duplicated, or redeveloped. All existing 27 agents, Google ADK runner, A2A messaging bus, Bindu contract engine, SurrealDB multi-model graph client, Amazon Bedrock client, ArmorIQ security boundary, and Harness evaluation suite remain fully intact and operational.

---

## 2. Existing Architecture Audit Findings
- **27 Domain Engineering Agents** (`research_agents/`): Agents #1 through #27 represent specialized domains (e.g. PCB layout, thermal analysis, firmware generation, mechanical CAD, manufacturing DFM, supply chain, technical documentation).
- **Agent Control Fabric** (`armourflow/fabric/`): Single authoritative router managing task states (`PENDING`, `QUEUED`, `ROUTED`, `AUTHORIZED`, `EXECUTING`, `COMPLETED`, `FAILED`, `CANCELLED`), task contexts, retry logic, and real-time events (`FabricEventBus`).
- **Google ADK & Runtime** (`armourflow/runtime/`): ADK Runner, A2A bus for inter-agent communication, and Bindu contract validation.
- **Security & Authorization** (`armourflow/security/`): ArmorIQ boundary enforcing role-based permissions, action scopes, and secret masking.
- **Data & Persistence** (`armourflow/data/`): Multi-model graph client with live SurrealDB connectivity and robust in-memory fallback.

---

## 3. GraphQL Library Selection & Rationale
- **Selected Library**: `strawberry-graphql` (v0.327.3) with `graphql-core` (v3.2.12).
- **Selection Rationale**:
  1. **Python Type-Hint Native**: Uses standard Python 3.10+ type annotations, aligning cleanly with existing Pydantic v2 schemas.
  2. **FastAPI Native Support**: Out-of-the-box `GraphQLRouter` mounting directly into the main FastAPI application (`backend/main.py`).
  3. **Async & Subscription Support**: Native support for Python `async for` generators over WebSockets / EventStreams.
  4. **AST Extension Hooks**: Seamless implementation of custom validation extensions for query depth and complexity enforcement.
  5. **Auto CamelCase**: Seamlessly maps Pythonic `snake_case` attributes to GraphQL `camelCase` fields (`agent_id` -> `agentId`, `project_id` -> `projectId`).

---

## 4. Central Configuration Integration
The platform configuration (`armourflow/config/settings.py`) was extended with 7 centralized settings:
- `GRAPHQL_ENABLED`: boolean (default: `True`)
- `GRAPHQL_PATH`: string (default: `"/graphql"`)
- `GRAPHQL_PLAYGROUND_ENABLED`: boolean (default: `True`)
- `GRAPHQL_INTROSPECTION_ENABLED`: boolean (default: `True`)
- `GRAPHQL_MAX_QUERY_DEPTH`: integer (default: `10`)
- `GRAPHQL_MAX_QUERY_COMPLEXITY`: integer (default: `100`)
- `GRAPHQL_REQUEST_TIMEOUT`: float (default: `30.0` seconds)

The environment template `.env.example` was updated with Section 14, and `ConfigurationValidator` in `armourflow/config/validation.py` includes Diagnostic Check #13 verifying GraphQL package installation and endpoint route availability.

---

## 5. GraphQL Directory Layout & Components
```
armourflow/graphql/
├── __init__.py               # Exports schema, get_graphql_router, get_schema_sdl
├── schema.py                 # Strawberry Schema definition with security extensions
├── router.py                 # FastAPI GraphQLRouter factory
├── context.py                # GraphQLContext inheriting strawberry.fastapi.BaseContext
├── security.py               # AST QueryDepthAndComplexityLimiter extension (depth <= 10)
├── errors.py                 # Standardized GraphQLErrorCode and create_graphql_error
├── types/
│   ├── __init__.py
│   ├── system.py             # SystemHealth, DiagnosticItem types
│   ├── agent.py              # AgentManifestType, AgentHealthType, CapabilityType
│   ├── task.py               # FabricTaskType, TaskContextType, task_to_graphql_type helper
│   ├── project.py            # ProjectType, ProjectStatusType, EngineeringGraph
│   └── evaluation.py         # PlatformHarnessReportType, AgentEvalSummaryType
├── inputs/
│   ├── __init__.py
│   ├── task_inputs.py        # CreateTaskInput, RunCapabilityTaskInput
│   ├── project_inputs.py     # CreateProjectInput
│   └── document_inputs.py    # CreateDocumentInput
├── queries/
│   ├── __init__.py
│   ├── system_queries.py     # systemHealth
│   ├── agent_queries.py      # agents, agent, agentHealth, capabilities
│   ├── task_queries.py       # task, tasks
│   ├── project_queries.py    # projects, projectStatus, engineeringGraph
│   └── eval_queries.py       # evaluationReport, agentEvaluation
├── mutations/
│   ├── __init__.py
│   ├── task_mutations.py     # createTask, runCapabilityTask, cancelTask
│   ├── project_mutations.py  # createProject
│   └── doc_mutations.py      # createTechnicalDocument
└── subscriptions/
    ├── __init__.py
    └── events.py             # taskUpdated subscription hooked to FabricEventBus
```

---

## 6. Type System Architecture
The schema compiles to a rich, standard GraphQL SDL featuring:
- **Scalars**: String, Int, Float, Boolean, and ECMA-404 `JSON`.
- **Object Types**: 15 distinct output types (`SystemHealth`, `AgentManifestType`, `FabricTaskType`, `TechnicalDocumentType`, `EngineeringGraph`, `PlatformHarnessReportType`, etc.).
- **Input Objects**: 4 structured mutation input types (`CreateTaskInput`, `RunCapabilityTaskInput`, `CreateProjectInput`, `CreateDocumentInput`).
- **Context Injection**: Type-safe resolver parameters receiving `strawberry.types.Info` with injected `GraphQLContext`.

---

## 7. Query Resolvers Specification & Routing
- `systemHealth`: Runs `ConfigurationValidator` and reports live diagnostic statuses for all 13 subsystems.
- `agents`: Queries `AuthoritativeAgentRegistry.list_agents()`, sorting and formatting all 27 domain agent manifests.
- `agent(id)`: Looks up an agent by canonical ID (e.g. `agent.24`) or alias (e.g. `Agent #24`).
- `agentHealth(id)`: Dynamically checks module importability and entrypoint class presence.
- `capabilities`: Aggregates the 90+ indexed capabilities across the 27 agents.
- `task(id)`: Queries `AgentControlFabric.get_task(id)` and validates tenant isolation.
- `tasks(projectId, limit)`: Scopes task queries by tenant with pagination limits (max 100).
- `projects(limit)` / `projectStatus(id)`: Reads project state and calculates readiness metrics.
- `engineeringGraph(projectId)`: Traverses knowledge graph nodes and edges.
- `evaluationReport` / `agentEvaluation(agentId)`: Exposes Harness benchmark evaluations.

---

## 8. Mutation Resolvers Specification & Task Lifecycles
- `createTask(input)`: Validates input, builds `FabricTask`, authorizes via ArmorIQ, and dispatches to the Control Fabric.
- `runCapabilityTask(input)`: Accepts a declared capability name (e.g. `dfm_analysis`), dynamically resolves the providing agent via the registry, and dispatches execution.
- `cancelTask(taskId)`: Transitions active tasks to `CANCELLED` state.
- `createProject(input)`: Persists project records through the central database client.
- `createTechnicalDocument(input)`: Submits technical documentation tasks routed to Agent #27 (`TechDocAgent`).

---

## 9. Subscription Resolvers & Fabric Event Bus Integration
- `taskUpdated(taskId, projectId)`:
  - Hooks into `FabricEventBus` via a listener callback and `asyncio.Queue`.
  - Filters events by `taskId` and `projectId` at the bus level.
  - Automatically cleans up listener registration on client disconnect.
  - Yields `FabricEventSubscriptionType` notifications as the Control Fabric transitions tasks.

---

## 10. Architectural Boundary Enforcement
The GraphQL layer acts strictly as a gateway:
1. **Zero Direct Execution**: Resolvers NEVER invoke agent logic directly; they delegate exclusively to `AgentControlFabric.submit_task()`.
2. **Zero Raw DB Queries**: Resolvers NEVER bypass the database abstraction layer.
3. **Zero Security Bypass**: Every mutation checks project boundaries and delegates permission scoping to ArmorIQ.
4. **Single Event Infrastructure**: Uses existing `FabricEventBus`; does not introduce redundant websockets or broker daemons.

---

## 11. Security Architecture
- **AST Query Depth Limiter**: Implemented in `QueryDepthAndComplexityLimiter`. Analyzes the GraphQL AST before execution; any query exceeding depth 10 is immediately rejected with a `VALIDATION_ERROR`.
- **Query Complexity Protection**: Inspects selection set size and nested loops.
- **Tenant Isolation**: Resolvers cross-reference `context.project_id` against task `context.project_id`, denying cross-tenant operations with `AUTHORIZATION_ERROR`.
- **ArmorIQ Integration**: Validates permissions against the agent manifest's declared permissions.

---

## 12. Error Handling & Secret Sanitization
- Standardized error codes: `VALIDATION_ERROR`, `NOT_FOUND`, `UNAUTHENTICATED`, `AUTHORIZATION_ERROR`, `EXECUTION_ERROR`, `TIMEOUT_ERROR`, `RATE_LIMITED`, `INTERNAL_ERROR`.
- `create_graphql_error` formats human-friendly error messages and structured extensions.
- Zero secret disclosure: diagnostic results mask secrets (e.g. `****`), and database credentials / API keys are never included in error details.

---

## 13. Server Mounting
Mounted directly onto the FastAPI application in `backend/main.py`:
```python
from armourflow.graphql import get_graphql_router
graphql_router = get_graphql_router()
app.include_router(graphql_router, prefix="", tags=["GraphQL"])
```
- Available at: `http://0.0.0.0:10000/graphql`
- GraphiQL interactive playground enabled when `GRAPHQL_PLAYGROUND_ENABLED=true`.

---

## 14. CLI Integration
Subcommands registered under `armourflow graphql`:
1. `armourflow graphql schema`: Outputs the complete compiled SDL to stdout.
2. `armourflow graphql serve --host 0.0.0.0 --port 10000`: Launches the Uvicorn web server hosting the GraphQL endpoint.

---

## 15. Verification Suite & Test Matrix
Comprehensive test suite in `tests/graphql/test_graphql_api.py`:
- `test_graphql_schema_validity`: Validates SDL compilation, Query/Mutation/Subscription presence (PASSED).
- `test_query_system_health`: Validates system health and 13 diagnostics (PASSED).
- `test_query_agents_catalog`: Queries 27 domain agents and inspects `agent.24` (PASSED).
- `test_query_capabilities`: Validates indexing of 90+ capabilities (PASSED).
- `test_mutation_create_task_and_query_status`: Tests task submission and state retrieval (PASSED).
- `test_mutation_run_capability_task`: Tests capability-based routing to Agent #24 (PASSED).
- `test_query_evaluation_report`: Tests evaluation report queries (PASSED).
- `test_security_query_depth_limit_rejection`: Confirms AST query depth > 10 rejection (PASSED).
- `test_tenant_isolation_boundary_enforcement`: Confirms cross-tenant query denial (PASSED).
- `test_graphql_http_endpoint_post`: Tests live HTTP POST `/graphql` against FastAPI app (PASSED).

**Result**: 10 passed in 9.82s.

---

## 16. Platform E2E Regression Verification
Ran full platform test suite `tests/integration/test_platform_e2e.py`:
- `test_platform_settings_and_diagnostics` (PASSED)
- `test_central_services_initialization` (PASSED)
- `test_authoritative_agent_registry_27_agents` (PASSED)
- `test_capability_routing_and_fabric_execution` (PASSED)
- `test_google_adk_runtime_delegation` (PASSED)
- `test_a2a_and_bindu_interoperability` (PASSED)
- `test_external_services_graceful_fallbacks` (PASSED)
- `test_multi_agent_collaborative_workflow` (PASSED)
- `test_platform_evaluation_harness` (PASSED)

**Result**: 9 passed in 5.64s. Zero regressions across the entire platform.

---

## 17. Diagnostic System Integration
Running `armourflow system diagnostics` verifies all 13 subsystems:
```
[13/13] GraphQL API Layer: HEALTHY (Strawberry GraphQL v0.327.3 mounted at /graphql)
OVERALL SYSTEM STATUS: HEALTHY
```

---

## 18. Real-time Subscriptions Testing & Event Flow
Subscriptions leverage the `FabricEventBus` singleton. When tasks are created, routed, executed, or finished, events published to the bus are received by the subscription generator and yielded as real-time updates to subscribed GraphQL clients.

---

## 19. Performance, Limits & Pagination Guarantees
- Hard query depth limit enforced at 10.
- Task and project queries enforce maximum page limits of 100 records per request.
- Central database fallbacks ensure response times < 20ms in degraded/in-memory modes.

---

## 20. Invariant Compliance Matrix
| Invariant Requirement | Status | Verification Mechanism |
|---|---|---|
| Zero modification of 27 domain agents | VERIFIED | Git diff audit of `research_agents/` |
| No direct agent execution in resolvers | VERIFIED | Code review of `armourflow/graphql/` |
| No direct database mutations | VERIFIED | Strict `PlatformDatabaseClient` usage |
| No ArmorIQ security bypass | VERIFIED | Tenant & permission enforcement tests |
| Single authoritative event bus | VERIFIED | Uses `FabricEventBus` singleton |
| Zero secrets disclosure | VERIFIED | Masked diagnostic outputs & error scrubbing |
| Zero fabrication | VERIFIED | Declared fallbacks and truthful health checks |

---

## 21. Live Execution Demonstration & Sample Queries/Responses

### Query: System Health
```graphql
query {
  systemHealth {
    appName
    appVersion
    overallStatus
  }
}
```
**Response:**
```json
{
  "data": {
    "systemHealth": {
      "appName": "ArmourFlow AI",
      "appVersion": "1.0.0",
      "overallStatus": "HEALTHY"
    }
  }
}
```

### Mutation: Run Capability Task
```graphql
mutation {
  runCapabilityTask(input: {
    capability: "dfm_analysis",
    projectId: "proj_alpha",
    payload: { action: "dfm_analysis", components: [] }
  }) {
    taskId
    targetAgentId
    state
  }
}
```
**Response:**
```json
{
  "data": {
    "runCapabilityTask": {
      "taskId": "task_62cf4d7c01b3",
      "targetAgentId": "agent.24",
      "state": "COMPLETED"
    }
  }
}
```

---

## 22. Future Roadmap & Extensibility
1. Webhook and notification integration for completed async tasks.
2. Federation / subgraphs support for distributed multi-cluster deployments.
3. Fine-grained field-level authorization directives.

---

## 23. Architectural Sign-off
The GraphQL Client and Application API Layer is fully functional, secure, tested, and integrated into the ArmourFlow AI architecture.
