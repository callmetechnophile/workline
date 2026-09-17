"""
System and health check GraphQL types.
"""

from typing import List, Optional
import strawberry


@strawberry.type
class DiagnosticItem:
    name: str
    status: str
    details: str
    required: bool
    secret: bool


@strawberry.type
class SystemHealth:
    app_name: str
    app_version: str
    app_env: str
    overall_status: str
    diagnostics: List[DiagnosticItem]
