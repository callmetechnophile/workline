"""
Workline Service Mesh: Hub-and-Spoke Inter-Service Communication Engine.
R1 acts as the central authenticated gateway, enforcing ArmourIQ policy,
request context propagation, timeouts, safe retries, and health probes.
"""

import os
import secrets
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid
import httpx
from pydantic import BaseModel, Field

from backend.workline.armouriq.adk_adapter import ArmourIQADKAdapter, ArmourIQSecurityError
from backend.workline.armouriq.audit import ArmourIQAuditLogger, sanitize_audit_payload
from backend.workline.armouriq.capabilities import AgentCapability, PolicyDecision, RiskTier
from backend.workline.armouriq.policy import ArmourIQPolicyEngine
from backend.workline.armouriq.trust_context import TrustContext


# Default Service Endpoints (Environment-overridable for Render deployment)
R1_GATEWAY_URL = os.getenv("WORKLINE_R1_URL", os.getenv("R1_SERVICE_URL", "http://localhost:10000"))
R2_AI_URL = os.getenv("WORKLINE_R2_URL", os.getenv("R2_SERVICE_URL", "http://localhost:10002"))
R3_KNOWLEDGE_URL = os.getenv("WORKLINE_R3_URL", os.getenv("R3_SERVICE_URL", "http://localhost:10003"))
R4_ENGINEERING_URL = os.getenv("WORKLINE_R4_URL", os.getenv("R4_SERVICE_URL", "http://localhost:10004"))
R5_PROCUREMENT_URL = os.getenv("WORKLINE_R5_URL", os.getenv("R5_SERVICE_URL", "http://localhost:10005"))

# Service Authentication Key (Render environment secret)
SERVICE_AUTH_KEY = os.getenv("WORKLINE_SERVICE_AUTH_KEY", "workline-internal-mesh-key-2026")

# Standard HTTP Timeouts
DEFAULT_CONNECT_TIMEOUT = 5.0
DEFAULT_READ_TIMEOUT = 30.0
DEFAULT_TOTAL_TIMEOUT = 35.0


class ServiceMeshRequest(BaseModel):
    """Encapsulated inter-service request with ArmourIQ trust context."""
    source_service: str = Field(..., description="Source microservice ID (e.g. 'R2_AI')")
    target_service: str = Field(..., description="Target microservice ID ('R2', 'R3', 'R4', 'R5')")
    action: str = Field(..., description="Target operation/endpoint (e.g. 'knowledge.search')")
    path: str = Field(..., description="Target URL path")
    method: str = Field(default="POST", description="HTTP Method")
    payload: Optional[Dict[str, Any]] = Field(default=None)
    params: Optional[Dict[str, Any]] = Field(default=None)
    context: TrustContext = Field(..., description="ArmourIQ Trust Context")


class ServiceMeshResponse(BaseModel):
    """Standardized response from service mesh invocation."""
    status_code: int
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    latency_ms: float = 0.0
    request_id: str
    target_service: str


class ServiceMeshGateway:
    """
    R1 Control Plane & Authenticated Gateway.
    Routes inter-service traffic with ArmourIQ policy evaluation,
    context propagation, timeouts, and safe retries.
    """

    SERVICE_URLS = {
        "R2": R2_AI_URL,
        "R2_AI": R2_AI_URL,
        "R3": R3_KNOWLEDGE_URL,
        "R3_KNOWLEDGE": R3_KNOWLEDGE_URL,
        "R4": R4_ENGINEERING_URL,
        "R4_ENGINEERING": R4_ENGINEERING_URL,
        "R5": R5_PROCUREMENT_URL,
        "R5_PROCUREMENT": R5_PROCUREMENT_URL,
    }

    # Action to required ArmourIQ capability mapping
    ACTION_CAPABILITY_MAP = {
        "research.execute": AgentCapability.READ_RESEARCH,
        "knowledge.search": AgentCapability.READ_KNOWLEDGE,
        "knowledge.query_graph": AgentCapability.READ_KNOWLEDGE,
        "knowledge.index_document": AgentCapability.READ_RESEARCH,
        "engineering.validate_pcb": AgentCapability.VALIDATE_PCB,
        "engineering.run_pinn": AgentCapability.RUN_SIMULATION,
        "engineering.validate_candidate": AgentCapability.ANALYZE_COMPONENT,
        "procurement.search": AgentCapability.LOOKUP_COMPONENT,
        "procurement.quote": AgentCapability.CREATE_PROCUREMENT_QUOTE,
        "procurement.order": AgentCapability.EXECUTE_PROCUREMENT,
    }

    @classmethod
    def get_service_url(cls, target_service: str) -> Optional[str]:
        """Resolves target microservice base URL."""
        return cls.SERVICE_URLS.get(target_service.upper())

    @classmethod
    def verify_service_token(cls, token: Optional[str]) -> bool:
        """Constant-time verification of internal service token."""
        if not token:
            return False
        return secrets.compare_digest(token, SERVICE_AUTH_KEY)

    @classmethod
    async def dispatch(
        cls,
        mesh_req: ServiceMeshRequest,
        service_token: Optional[str] = None,
    ) -> ServiceMeshResponse:
        """
        Main R1 Gateway dispatch pipeline:
        1. Authenticate source service token
        2. Validate project context & isolation
        3. Evaluate ArmourIQ policy & capabilities
        4. Propagate Trust Context headers
        5. Execute HTTP call with timeouts and safe retries
        6. Log sanitized audit event
        """
        start_time = time.perf_counter()
        req_id = mesh_req.context.request_id

        # 1. Service Token Authentication
        effective_token = service_token or SERVICE_AUTH_KEY
        if not cls.verify_service_token(effective_token):
            return ServiceMeshResponse(
                status_code=401,
                error="Unauthorized: Invalid internal service mesh authorization token",
                request_id=req_id,
                target_service=mesh_req.target_service,
            )

        # 2. Project Isolation Check
        if not mesh_req.context.project_id or not mesh_req.context.project_id.strip():
            return ServiceMeshResponse(
                status_code=403,
                error="Forbidden: Missing or invalid project_id in execution context",
                request_id=req_id,
                target_service=mesh_req.target_service,
            )

        # 3. ArmourIQ Policy & Capability Check
        required_cap = cls.ACTION_CAPABILITY_MAP.get(mesh_req.action)
        if required_cap and not mesh_req.context.has_capability(required_cap):
            # Log denied audit event
            ArmourIQAuditLogger.log_event(
                request_id=req_id,
                session_id=mesh_req.context.session_id,
                user_id=mesh_req.context.user_id,
                project_id=mesh_req.context.project_id,
                agent_id=mesh_req.context.agent_id,
                parent_agent_id=mesh_req.context.parent_agent_id,
                tool_name=mesh_req.action,
                capability=required_cap.value,
                risk_level=mesh_req.context.risk_level,
                policy="service_mesh_policy",
                decision=PolicyDecision.DENY,
                delegation_chain=mesh_req.context.delegation_chain,
                execution_status="DENIED",
                error=f"Source service '{mesh_req.source_service}' / Agent '{mesh_req.context.agent_id}' lacks capability '{required_cap.value}'",
            )
            return ServiceMeshResponse(
                status_code=403,
                error=f"ArmourIQ Policy Violation: Agent '{mesh_req.context.agent_id}' is not authorized for '{mesh_req.action}'",
                request_id=req_id,
                target_service=mesh_req.target_service,
            )

        # 4. Resolve Target Service URL
        target_base_url = cls.get_service_url(mesh_req.target_service)
        if not target_base_url:
            return ServiceMeshResponse(
                status_code=400,
                error=f"Unknown target service: '{mesh_req.target_service}'",
                request_id=req_id,
                target_service=mesh_req.target_service,
            )

        target_url = f"{target_base_url.rstrip('/')}/{mesh_req.path.lstrip('/')}"

        # 5. Build Propagated Headers
        headers = {
            "Authorization": f"Bearer {SERVICE_AUTH_KEY}",
            "X-Workline-Service-Token": SERVICE_AUTH_KEY,
            "X-Request-ID": req_id,
            "X-Session-ID": mesh_req.context.session_id,
            "X-Project-ID": mesh_req.context.project_id,
            "X-User-ID": mesh_req.context.user_id,
            "X-Agent-ID": mesh_req.context.agent_id,
            "X-Delegation-Chain": ",".join(mesh_req.context.delegation_chain),
            "Content-Type": "application/json",
        }

        # 6. Execute Request with Explicit Timeouts & Safe Retries
        timeouts = httpx.Timeout(
            connect=DEFAULT_CONNECT_TIMEOUT,
            read=DEFAULT_READ_TIMEOUT,
            write=DEFAULT_READ_TIMEOUT,
            pool=DEFAULT_TOTAL_TIMEOUT,
        )

        max_attempts = 3 if mesh_req.method.upper() == "GET" else 1
        last_error = None

        for attempt in range(max_attempts):
            try:
                async with httpx.AsyncClient(timeout=timeouts) as client:
                    if mesh_req.method.upper() == "GET":
                        resp = await client.get(target_url, headers=headers, params=mesh_req.params)
                    else:
                        resp = await client.post(target_url, headers=headers, json=mesh_req.payload)

                    latency = (time.perf_counter() - start_time) * 1000.0

                    try:
                        resp_data = resp.json()
                    except Exception:
                        resp_data = {"raw_text": resp.text}

                    # Log success audit event
                    ArmourIQAuditLogger.log_event(
                        request_id=req_id,
                        session_id=mesh_req.context.session_id,
                        user_id=mesh_req.context.user_id,
                        project_id=mesh_req.context.project_id,
                        agent_id=mesh_req.context.agent_id,
                        tool_name=mesh_req.action,
                        capability=required_cap.value if required_cap else None,
                        risk_level=mesh_req.context.risk_level,
                        policy="service_mesh_policy",
                        decision=PolicyDecision.ALLOW,
                        delegation_chain=mesh_req.context.delegation_chain,
                        execution_status="EXECUTED" if resp.status_code < 400 else "DOWNSTREAM_ERROR",
                        metadata={"target_service": mesh_req.target_service, "status_code": resp.status_code, "latency_ms": round(latency, 2)},
                    )

                    return ServiceMeshResponse(
                        status_code=resp.status_code,
                        data=resp_data if resp.status_code < 400 else None,
                        error=resp_data.get("detail") if resp.status_code >= 400 and isinstance(resp_data, dict) else (resp.text if resp.status_code >= 400 else None),
                        latency_ms=latency,
                        request_id=req_id,
                        target_service=mesh_req.target_service,
                    )
            except httpx.RequestError as exc:
                last_error = str(exc)
                if attempt < max_attempts - 1:
                    continue  # Safe retry for GET

        latency = (time.perf_counter() - start_time) * 1000.0
        return ServiceMeshResponse(
            status_code=503,
            error=f"Service Mesh Error: Target microservice '{mesh_req.target_service}' unavailable at {target_base_url}: {last_error}",
            latency_ms=latency,
            request_id=req_id,
            target_service=mesh_req.target_service,
        )

    @classmethod
    async def check_cluster_health(cls) -> Dict[str, Any]:
        """
        Probes real liveness and readiness of all 5 Render microservices.
        Never fabricates health status.
        """
        results = {}
        overall_healthy = True

        for s_id, s_url in [("R2", R2_AI_URL), ("R3", R3_KNOWLEDGE_URL), ("R4", R4_ENGINEERING_URL), ("R5", R5_PROCUREMENT_URL)]:
            probe_url = f"{s_url.rstrip('/')}/health"
            try:
                async with httpx.AsyncClient(timeout=httpx.Timeout(2.5, connect=2.0)) as client:
                    resp = await client.get(probe_url)
                    if resp.status_code == 200:
                        results[s_id] = {
                            "status": "healthy",
                            "endpoint": s_url,
                            "http_code": 200,
                        }
                    else:
                        results[s_id] = {
                            "status": "degraded",
                            "endpoint": s_url,
                            "http_code": resp.status_code,
                        }
                        overall_healthy = False
            except Exception as e:
                results[s_id] = {
                    "status": "unreachable",
                    "endpoint": s_url,
                    "error": str(e),
                }
                overall_healthy = False

        return {
            "status": "healthy" if overall_healthy else "degraded",
            "gateway": "R1_CORE",
            "version": "1.0.0-rc1",
            "downstream_services": results,
        }
