"""
Workline Service Mesh Package: R1 Hub-and-Spoke Gateway, Authenticated Routing & Inter-Service Client.
"""

from backend.workline.mesh.client import ServiceMeshClient
from backend.workline.mesh.gateway import (
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_READ_TIMEOUT,
    DEFAULT_TOTAL_TIMEOUT,
    R1_GATEWAY_URL,
    R2_AI_URL,
    R3_KNOWLEDGE_URL,
    R4_ENGINEERING_URL,
    R5_PROCUREMENT_URL,
    SERVICE_AUTH_KEY,
    ServiceMeshGateway,
    ServiceMeshRequest,
    ServiceMeshResponse,
)

__all__ = [
    "ServiceMeshGateway",
    "ServiceMeshClient",
    "ServiceMeshRequest",
    "ServiceMeshResponse",
    "R1_GATEWAY_URL",
    "R2_AI_URL",
    "R3_KNOWLEDGE_URL",
    "R4_ENGINEERING_URL",
    "R5_PROCUREMENT_URL",
    "SERVICE_AUTH_KEY",
    "DEFAULT_CONNECT_TIMEOUT",
    "DEFAULT_READ_TIMEOUT",
    "DEFAULT_TOTAL_TIMEOUT",
]
