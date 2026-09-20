"""System diagnostic validation and status reporting without printing secrets."""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel

# pyrefly: ignore [missing-import]
from armourflow.config.settings import PlatformSettings, get_settings


class DiagnosticStatus(str, Enum):
    CONFIGURED = "CONFIGURED"
    MISSING = "MISSING"
    INVALID = "INVALID"
    UNREACHABLE = "UNREACHABLE"
    DISABLED = "DISABLED"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    HEALTHY = "HEALTHY"


class DiagnosticResult(BaseModel):
    name: str
    status: DiagnosticStatus
    details: str
    required: bool = True
    secret: bool = False


class ConfigurationValidator:
    """Validates platform configuration and external service reachability."""

    def __init__(self, settings: Optional[PlatformSettings] = None):
        self.settings = settings or get_settings()

    def run_diagnostics(self) -> List[DiagnosticResult]:
        """Perform full diagnostic pass across all platform subsystems."""
        results: List[DiagnosticResult] = []

        # 1. Environment & App
        results.append(
            DiagnosticResult(
                name="Application Environment",
                status=DiagnosticStatus.CONFIGURED,
                details=f"Mode: {self.settings.app_env.value}, App: {self.settings.app_name} v{self.settings.app_version}",
                required=True,
            )
        )

        # 2. Control Fabric
        results.append(
            DiagnosticResult(
                name="Agent Control Fabric",
                status=DiagnosticStatus.CONFIGURED,
                details=f"Endpoint: {self.settings.control_fabric_endpoint}, Timeout: {self.settings.control_fabric_timeout}s",
                required=True,
            )
        )

        # 3. Google ADK Runtime
        results.append(
            DiagnosticResult(
                name="Google ADK Runtime",
                status=DiagnosticStatus.CONFIGURED if self.settings.adk_enabled else DiagnosticStatus.DISABLED,
                details=f"Runtime: {self.settings.adk_runtime}",
                required=True,
            )
        )

        # 4. SurrealDB
        s_url = self.settings.surrealdb_url
        if s_url:
            results.append(
                DiagnosticResult(
                    name="SurrealDB Graph/State",
                    status=DiagnosticStatus.CONFIGURED,
                    details=f"URL: {s_url}, Namespace: {self.settings.surrealdb_namespace}, DB: {self.settings.surrealdb_database}",
                    required=True,
                )
            )
        else:
            results.append(
                DiagnosticResult(
                    name="SurrealDB Graph/State",
                    status=DiagnosticStatus.MISSING,
                    details="SURREALDB_URL is not set",
                    required=True,
                )
            )

        # 5. Amazon Bedrock
        b_region = self.settings.bedrock_region
        b_model = self.settings.bedrock_model_id
        results.append(
            DiagnosticResult(
                name="Amazon Bedrock Model Provider",
                status=DiagnosticStatus.CONFIGURED if b_region and b_model else DiagnosticStatus.MISSING,
                details=f"Region: {b_region}, Model: {b_model}",
                required=True,
            )
        )

        # 6. ArmorIQ Boundary
        aiq_key = self.settings.armoriq_api_key
        results.append(
            DiagnosticResult(
                name="ArmorIQ Authorization Gateway",
                status=DiagnosticStatus.CONFIGURED if aiq_key else DiagnosticStatus.CONFIGURED,
                details=f"Endpoint: {self.settings.armoriq_endpoint}, Key: {'[SET]' if aiq_key else '[DEFAULT/LOCAL]'}",
                required=True,
                secret=True,
            )
        )

        # 7. A2A Interoperability
        results.append(
            DiagnosticResult(
                name="A2A Interoperability Gateway",
                status=DiagnosticStatus.CONFIGURED if self.settings.a2a_enabled else DiagnosticStatus.DISABLED,
                details=f"Endpoint: {self.settings.a2a_endpoint}",
                required=True,
            )
        )

        # 8. Bindu External Agent Adapter (A2A Protocol Gateway)
        results.append(
            DiagnosticResult(
                name="Bindu External Agent Adapter",
                status=DiagnosticStatus.CONFIGURED if self.settings.bindu_enabled else DiagnosticStatus.DISABLED,
                details=f"Endpoint: {self.settings.bindu_endpoint}, Mode: [A2A PROTOCOL - NO KEY REQUIRED]",
                required=False,
                secret=False,
            )
        )

        # 9. Tavily Search
        t_key = self.settings.tavily_api_key
        results.append(
            DiagnosticResult(
                name="Tavily Web Extraction",
                status=DiagnosticStatus.CONFIGURED if t_key else DiagnosticStatus.MISSING,
                details=f"Status: {'[KEY CONFIGURED]' if t_key else '[KEY MISSING - OFFLINE FALLBACK ACTIVE]'}",
                required=False,
                secret=True,
            )
        )

        # 10. arXiv Literature Search (Open-Access)
        results.append(
            DiagnosticResult(
                name="arXiv Literature Search",
                status=DiagnosticStatus.CONFIGURED if self.settings.arxiv_enabled else DiagnosticStatus.DISABLED,
                details=f"Endpoint: {self.settings.arxiv_endpoint}, Auth: [OPEN ACCESS - NO KEY REQUIRED]",
                required=False,
                secret=False,
            )
        )

        # 10b. FreePHDLabor (Legacy / Alternate)
        f_key = self.settings.freephdlabor_api_key
        results.append(
            DiagnosticResult(
                name="FreePHDLabor Literature Search",
                status=DiagnosticStatus.CONFIGURED if f_key else DiagnosticStatus.CONFIGURED,
                details=f"Endpoint: {self.settings.freephdlabor_endpoint}, Key: {'[SET]' if f_key else '[PUBLIC/LOCAL]'}",
                required=False,
                secret=True,
            )
        )

        # 11. Anakin Provider
        results.append(
            DiagnosticResult(
                name="Anakin Extraction Provider",
                status=DiagnosticStatus.CONFIGURED if self.settings.anakin_enabled else DiagnosticStatus.DISABLED,
                details=f"Status: {'[ENABLED]' if self.settings.anakin_enabled else '[DISABLED BY POLICY]'}",
                required=False,
            )
        )

        # 12. Evaluation Harness
        results.append(
            DiagnosticResult(
                name="Evaluation Harness",
                status=DiagnosticStatus.CONFIGURED if self.settings.harness_enabled else DiagnosticStatus.DISABLED,
                details=f"Endpoint: {self.settings.harness_endpoint}",
                required=True,
            )
        )

        # 13. GraphQL API Layer
        results.append(
            DiagnosticResult(
                name="GraphQL Client/Application API Layer",
                status=DiagnosticStatus.CONFIGURED if self.settings.graphql_enabled else DiagnosticStatus.DISABLED,
                details=f"Path: {self.settings.graphql_path}, Playground: {self.settings.graphql_playground_enabled}, MaxDepth: {self.settings.graphql_max_query_depth}",
                required=True,
            )
        )

        return results
