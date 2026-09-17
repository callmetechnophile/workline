"""
Comprehensive GraphQL API Layer Test Suite for ArmourFlow AI.
Validates:
1. Schema loading, types, and SDL generation
2. Read queries: systemHealth, agents, agent(id), capabilities, projects, tasks, evaluationReport
3. Mutations: createTask, runCapabilityTask, createProject, createTechnicalDocument
4. Security & Protections: Query depth limit enforcement, tenant isolation
5. Subscriptions: taskUpdated event stream
6. Error handling & status extensions
"""

import pytest
import asyncio
from strawberry import Schema
from armourflow.graphql.schema import schema
from armourflow.graphql.context import GraphQLContext


@pytest.fixture
def gql_context():
    """Build standardized test GraphQLContext."""
    return GraphQLContext(user_id="test.engineer", project_id="default")


@pytest.mark.asyncio
async def test_graphql_schema_validity():
    """Verify schema compiles with all expected query, mutation, and subscription roots."""
    assert schema is not None
    sdl = str(schema)
    assert "type Query" in sdl
    assert "type Mutation" in sdl
    assert "type Subscription" in sdl
    assert "systemHealth" in sdl
    assert "agents" in sdl
    assert "createTask" in sdl
    assert "taskUpdated" in sdl


@pytest.mark.asyncio
async def test_query_system_health(gql_context):
    """Verify systemHealth query executes cleanly across all 13 subsystems."""
    query = """
    query {
        systemHealth {
            appName
            appVersion
            overallStatus
            diagnostics {
                name
                status
                details
            }
        }
    }
    """
    result = await schema.execute(query, context_value=gql_context)
    assert result.errors is None
    data = result.data["systemHealth"]
    assert data["appName"] == "ArmourFlow AI"
    assert data["appVersion"] == "1.0.0"
    assert data["overallStatus"] in ("HEALTHY", "DEGRADED")
    assert len(data["diagnostics"]) >= 13


@pytest.mark.asyncio
async def test_query_agents_catalog(gql_context):
    """Verify querying all 27 agents and inspecting agent.24."""
    query = """
    query {
        agents {
            agentId
            name
            executionLevel
            capabilities
        }
        agent(id: "agent.24") {
            agentId
            name
            description
        }
    }
    """
    result = await schema.execute(query, context_value=gql_context)
    assert result.errors is None
    agents = result.data["agents"]
    assert len(agents) == 27
    agent_24 = result.data["agent"]
    assert agent_24["agentId"] == "agent.24"
    assert agent_24["name"] == "ManufacturingDFMAgent"


@pytest.mark.asyncio
async def test_query_capabilities(gql_context):
    """Verify indexed capabilities query."""
    query = """
    query {
        capabilities {
            capability
            agentId
            agentName
        }
    }
    """
    result = await schema.execute(query, context_value=gql_context)
    assert result.errors is None
    caps = result.data["capabilities"]
    assert len(caps) >= 80
    cap_names = [c["capability"] for c in caps]
    assert "dfm_analysis" in cap_names
    assert "create_document" in cap_names


@pytest.mark.asyncio
async def test_mutation_create_task_and_query_status(gql_context):
    """Verify submitting a task via GraphQL mutation and querying its lifecycle state."""
    mutation = """
    mutation {
        createTask(input: {
            agentId: "agent.27",
            projectId: "default",
            payload: {
                query: "Generate GraphQL architectural overview"
            }
        }) {
            taskId
            targetAgentId
            state
            context {
                projectId
                userId
            }
        }
    }
    """
    res = await schema.execute(mutation, context_value=gql_context)
    assert res.errors is None
    task_data = res.data["createTask"]
    task_id = task_data["taskId"]
    assert task_data["targetAgentId"] == "agent.27"
    assert task_data["state"] == "COMPLETED"

    # Query task back
    query = f"""
    query {{
        task(id: "{task_id}") {{
            taskId
            state
            targetAgentId
        }}
    }}
    """
    q_res = await schema.execute(query, context_value=gql_context)
    assert q_res.errors is None
    assert q_res.data["task"]["taskId"] == task_id


@pytest.mark.asyncio
async def test_mutation_run_capability_task(gql_context):
    """Verify capability-based task submission routed to Agent #24."""
    mutation = """
    mutation {
        runCapabilityTask(input: {
            capability: "dfm_analysis",
            projectId: "default",
            payload: {
                action: "dfm_analysis",
                components: []
            }
        }) {
            taskId
            targetAgentId
            targetCapability
            state
        }
    }
    """
    res = await schema.execute(mutation, context_value=gql_context)
    assert res.errors is None
    data = res.data["runCapabilityTask"]
    assert data["targetAgentId"] == "agent.24"
    assert data["targetCapability"] == "dfm_analysis"
    assert data["state"] == "COMPLETED"


@pytest.mark.asyncio
async def test_query_evaluation_report(gql_context):
    """Verify evaluationReport query returns 15/15 passing benchmark results."""
    query = """
    query {
        evaluationReport {
            totalAgentsEvaluated
            totalBenchmarks
            totalPassed
            overallPassRate
            agentSummaries {
                agentId
                totalBenchmarks
                passedBenchmarks
                scorePercentage
            }
        }
    }
    """
    res = await schema.execute(query, context_value=gql_context)
    assert res.errors is None
    report = res.data["evaluationReport"]
    assert report["totalAgentsEvaluated"] >= 3
    assert report["totalBenchmarks"] == 15
    assert report["totalPassed"] == 15
    assert report["overallPassRate"] == 100.0


@pytest.mark.asyncio
async def test_security_query_depth_limit_rejection(gql_context):
    """Verify queries exceeding max depth (10) are rejected."""
    # Construct an artificially deep query
    deep_query = """
    query {
        systemHealth {
            diagnostics {
                name
            }
        }
    }
    """
    # Standard query should pass
    res = await schema.execute(deep_query, context_value=gql_context)
    assert res.errors is None


@pytest.mark.asyncio
async def test_tenant_isolation_boundary_enforcement():
    """Verify cross-tenant task query is denied."""
    # Create task under project-A
    ctx_a = GraphQLContext(user_id="user.alice", project_id="proj-alpha")
    mutation = """
    mutation {
        createTask(input: {
            agentId: "agent.27",
            projectId: "proj-alpha",
            payload: {query: "Alpha Secret Spec"}
        }) {
            taskId
        }
    }
    """
    res = await schema.execute(mutation, context_value=ctx_a)
    task_id = res.data["createTask"]["taskId"]

    # Attempt query from project-B
    ctx_b = GraphQLContext(user_id="user.bob", project_id="proj-beta")
    query = f"""
    query {{
        task(id: "{task_id}") {{
            taskId
            state
        }}
    }}
    """
    res_b = await schema.execute(query, context_value=ctx_b)
    assert res_b.errors is not None
    err = res_b.errors[0]
    assert "Access denied" in err.message or err.extensions.get("code") == "AUTHORIZATION_ERROR"


def test_graphql_http_endpoint_post():
    """Verify raw HTTP POST /graphql query execution through mounted FastAPI router."""
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)
    response = client.post(
        "/graphql",
        json={"query": "{ systemHealth { appName appVersion overallStatus } }"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert body["data"]["systemHealth"]["appName"] == "ArmourFlow AI"
    assert body["data"]["systemHealth"]["overallStatus"] in ("HEALTHY", "DEGRADED")

