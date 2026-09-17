"""
Agent manifest, capability, and health GraphQL query resolvers.
"""

from typing import List, Optional
import strawberry
from strawberry.types import Info
from armourflow.registry import get_agent_registry
from armourflow.graphql.types.agent import AgentManifestType, AgentHealthType, CapabilityType
from armourflow.graphql.errors import create_graphql_error, GraphQLErrorCode


@strawberry.type
class AgentQueries:
    @strawberry.field
    def agents(self, info: Info) -> List[AgentManifestType]:
        """List all 27 registered agents and their capabilities."""
        reg = get_agent_registry()
        agents = reg.list_agents()
        return [
            AgentManifestType(
                agent_id=a.agent_id,
                name=a.name,
                version=a.version,
                execution_level=a.execution_level,
                entrypoint=a.entrypoint,
                description=a.description,
                capabilities=a.capabilities,
                dependencies=a.dependencies,
                permissions=a.permissions,
            )
            for a in sorted(agents, key=lambda x: x.agent_id)
        ]

    @strawberry.field
    def agent(self, info: Info, id: str) -> Optional[AgentManifestType]:
        """Look up a specific agent manifest by agent ID."""
        reg = get_agent_registry()
        a = reg.get_agent(id)
        if not a:
            raise create_graphql_error(
                f"Agent '{id}' not found in Authoritative Registry.",
                code=GraphQLErrorCode.NOT_FOUND,
                details={"agent_id": id},
            )
        return AgentManifestType(
            agent_id=a.agent_id,
            name=a.name,
            version=a.version,
            execution_level=a.execution_level,
            entrypoint=a.entrypoint,
            description=a.description,
            capabilities=a.capabilities,
            dependencies=a.dependencies,
            permissions=a.permissions,
        )

    @strawberry.field
    def agent_health(self, info: Info, id: str) -> AgentHealthType:
        """Check live importability and runtime health of an agent."""
        reg = get_agent_registry()
        h = reg.check_health(id)
        return AgentHealthType(
            agent_id=id,
            status=h["status"],
            importable=h["importable"],
            error=h.get("error"),
        )

    @strawberry.field
    def capabilities(self, info: Info) -> List[CapabilityType]:
        """List all indexed capabilities and their providing agents."""
        reg = get_agent_registry()
        caps = reg.get_all_capabilities()
        res = []
        for c in sorted(caps):
            agents = reg.find_by_capability(c)
            for a in agents:
                res.append(
                    CapabilityType(
                        capability=c,
                        agent_id=a.agent_id,
                        agent_name=a.name,
                    )
                )
        return res
