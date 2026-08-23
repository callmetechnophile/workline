"""
Service Mesh Client: Standardized client library for R2, R3, R4, and R5 microservices
to execute cross-service operations exclusively through R1 Gateway.
"""

from typing import Any, Dict, List, Optional
from backend.workline.armouriq.trust_context import TrustContext
from backend.workline.mesh.gateway import ServiceMeshGateway, ServiceMeshRequest, ServiceMeshResponse


class ServiceMeshClient:
    """Client for microservices to route dependencies through R1 Gateway."""

    def __init__(self, source_service_id: str):
        self.source_service_id = source_service_id

    async def call_service(
        self,
        target_service: str,
        action: str,
        path: str,
        context: TrustContext,
        method: str = "POST",
        payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> ServiceMeshResponse:
        """Dispatches an inter-service request through R1 Gateway."""
        mesh_req = ServiceMeshRequest(
            source_service=self.source_service_id,
            target_service=target_service,
            action=action,
            path=path,
            method=method,
            payload=payload,
            params=params,
            context=context,
        )
        return await ServiceMeshGateway.dispatch(mesh_req)

    # ==================== R2 SPECIFIC DEPENDENCIES ====================

    async def r2_query_r3_knowledge(self, context: TrustContext, query: str, limit: int = 5) -> ServiceMeshResponse:
        """R2 -> R1 -> R3: Semantic knowledge search."""
        return await self.call_service(
            target_service="R3",
            action="knowledge.search",
            path="/api/knowledge/search",
            context=context,
            payload={"query": query, "limit": limit},
        )

    async def r2_request_r4_simulation(self, context: TrustContext, pcb_id: str) -> ServiceMeshResponse:
        """R2 -> R1 -> R4: PCB DRC and PINN physics validation."""
        return await self.call_service(
            target_service="R4",
            action="engineering.validate_pcb",
            path="/api/pcb/validate",
            context=context,
            payload={"pcb_id": pcb_id},
        )

    async def r2_query_r5_procurement(self, context: TrustContext, query: str) -> ServiceMeshResponse:
        """R2 -> R1 -> R5: Component sourcing search."""
        return await self.call_service(
            target_service="R5",
            action="procurement.search",
            path="/api/procurement/search",
            context=context,
            payload={"query": query},
        )

    # ==================== R4 & R5 SPECIFIC DEPENDENCIES ====================

    async def r4_query_r3_datasheet(self, context: TrustContext, doc_id: str) -> ServiceMeshResponse:
        """R4 -> R1 -> R3: Datasheet and material parameters."""
        return await self.call_service(
            target_service="R3",
            action="knowledge.search",
            path="/api/documents/search",
            context=context,
            payload={"query": doc_id},
        )

    async def r5_query_r3_graph(self, context: TrustContext, component_id: str) -> ServiceMeshResponse:
        """R5 -> R1 -> R3: Component knowledge graph topology."""
        return await self.call_service(
            target_service="R3",
            action="knowledge.query_graph",
            path=f"/api/graph/entities/{component_id}",
            context=context,
            method="GET",
        )
