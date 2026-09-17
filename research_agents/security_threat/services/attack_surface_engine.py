"""
Attack Surface Discovery, Trust Boundary Mapping, and Data Flow Analysis (Agent #22).
"""

from typing import Any, Dict, List, Optional
from loguru import logger

from research_agents.security_threat.schemas import (
    AssetObject,
    AttackSurfaceEntry,
    SecurityDataFlow,
    TrustBoundary,
)


class AttackSurfaceEngine:
    """Discovers and catalogs assets, exposed entry points, trust boundaries, and cross-boundary data flows."""

    def discover_assets(
        self,
        project_id: str,
        architecture: Optional[Dict[str, Any]] = None,
        agents_topology: Optional[List[Dict[str, Any]]] = None,
        api_definitions: Optional[List[Dict[str, Any]]] = None,
    ) -> List[AssetObject]:
        assets = [
            AssetObject(
                asset_id=f"ASSET-GRAPH-DB-{project_id}",
                project_id=project_id,
                name="SurrealDB Knowledge Graph & Project Store",
                type="DATABASE",
                category="GRAPH_DATA",
                classification="CRITICAL",
                description="Stores multi-project engineering requirements, BOMs, FMEAs, and verification evidence.",
            ),
            AssetObject(
                asset_id=f"ASSET-ARMORIQ-TOKENS-{project_id}",
                project_id=project_id,
                name="ArmorIQ Execution Authorization & Delegation Tokens",
                type="CREDENTIAL",
                category="TOKENS",
                classification="CRITICAL",
                description="Cryptographic delegation tokens governing privileged agent operations.",
            ),
            AssetObject(
                asset_id=f"ASSET-API-KEYS-{project_id}",
                project_id=project_id,
                name="External Service Credentials (Bedrock / Tavily / Anakin)",
                type="CREDENTIAL",
                category="API_KEYS",
                classification="RESTRICTED",
                description="Cloud AI reasoning and web research API credentials.",
            ),
            AssetObject(
                asset_id=f"ASSET-BOM-DATA-{project_id}",
                project_id=project_id,
                name="Engineering Architecture & Component BOM",
                type="ARTIFACT",
                category="BOM",
                classification="CONFIDENTIAL",
                description="Proprietary hardware component selections, costs, and pin assignments.",
            ),
        ]
        return assets

    def map_trust_boundaries(self) -> List[TrustBoundary]:
        return [
            TrustBoundary(
                boundary_id="TB-PUBLIC-API",
                name="Public Internet to API Gateway",
                source_zone="PUBLIC",
                destination_zone="API",
                controls=["TLS 1.3 Termination", "JWT Authentication", "Rate Limiting Middleware"],
                data_types=["JSON API Requests", "Authentication Payloads"],
                description="External ingress boundary separating unauthenticated clients from FastAPI backend.",
            ),
            TrustBoundary(
                boundary_id="TB-API-FABRIC",
                name="API Layer to Agent Control Fabric",
                source_zone="API",
                destination_zone="CONTROL_FABRIC",
                controls=["RBAC / Team Permission Check", "Correlation ID Injection", "Schema Validation"],
                data_types=["Agent Invocation Tasks", "Project Context"],
                description="Boundary governing client requests transitioning into autonomous multi-agent execution.",
            ),
            TrustBoundary(
                boundary_id="TB-FABRIC-EXEC",
                name="Control Fabric to Privileged Execution Sandbox",
                source_zone="CONTROL_FABRIC",
                destination_zone="PRIVILEGED_EXECUTION",
                controls=["ArmorIQ Cryptographic Authorization", "Path Sandboxing", "Process Isolation"],
                data_types=["Shell Commands", "Filesystem Write Payloads", "Compiler Invocations"],
                description="Highest risk trust boundary governing execution of code and system tools (Agent #11).",
            ),
            TrustBoundary(
                boundary_id="TB-AGENT-EXTERNAL",
                name="Agent Runtime to External Third-Party APIs",
                source_zone="AGENT_RUNTIME",
                destination_zone="EXTERNAL_SERVICE",
                controls=["Egress Filter", "Secret Masking", "Output Sanitation"],
                data_types=["Bedrock LLM Prompts", "Tavily Search Queries", "Research Abstracts"],
                description="Egress boundary to third-party AI and search providers.",
            ),
        ]

    def map_attack_surface(
        self,
        api_definitions: Optional[List[Dict[str, Any]]] = None,
    ) -> List[AttackSurfaceEntry]:
        entries = [
            AttackSurfaceEntry(
                entry_id="ENTRY-AUTH-LOGIN",
                type="AUTH",
                exposure="PUBLIC",
                endpoint_path="/api/auth/login",
                authentication="None (Initial Credential Submission)",
                authorization="None",
                description="Public login endpoint vulnerable to credential stuffing, brute force, and token leakage.",
            ),
            AttackSurfaceEntry(
                entry_id="ENTRY-FILE-UPLOAD",
                type="FILE",
                exposure="PUBLIC",
                endpoint_path="/api/documents/upload",
                authentication="JWT Bearer Token",
                authorization="Team Member Role",
                description="Multipart document upload parser (PDF/DOCX/Markdown) processing untrusted user content.",
            ),
            AttackSurfaceEntry(
                entry_id="ENTRY-A2A-FABRIC",
                type="A2A",
                exposure="INTERNAL",
                endpoint_path="control_fabric.a2a_router",
                authentication="Agent Registry ID Token",
                authorization="Agent Capability Scopes",
                description="Inter-agent messaging bus vulnerable to message injection, spoofing, and privilege escalation.",
            ),
            AttackSurfaceEntry(
                entry_id="ENTRY-CLI-RUNNER",
                type="CLI",
                exposure="INTERNAL",
                endpoint_path="python -m *",
                authentication="Host OS User Identity",
                authorization="OS File Permissions",
                description="Direct command-line interface entrypoints across all 22 agents.",
            ),
            AttackSurfaceEntry(
                entry_id="ENTRY-EXTERNAL-WEB",
                type="EXTERNAL_SERVICE",
                exposure="RESTRICTED",
                endpoint_path="tavily.api.search",
                authentication="API Key",
                authorization="Outbound HTTPS",
                description="Outbound search results ingested directly into Agent #2 and #4 reasoning context.",
            ),
        ]
        return entries
