"""
System health and diagnostics GraphQL query resolvers.
"""

from typing import List
import strawberry
from strawberry.types import Info
from armourflow.config import ConfigurationValidator
from armourflow.graphql.types.system import SystemHealth, DiagnosticItem


@strawberry.type
class SystemQueries:
    @strawberry.field
    def system_health(self, info: Info) -> SystemHealth:
        """Inspect platform health across all central subsystems."""
        ctx = info.context
        validator = ConfigurationValidator(ctx.settings)
        checks = validator.run_diagnostics()

        items = [
            DiagnosticItem(
                name=c.name,
                status=c.status.value,
                details=c.details,
                required=c.required,
                secret=c.secret,
            )
            for c in checks
        ]

        all_ok = all(
            c.status.value in ("CONFIGURED", "HEALTHY", "DISABLED")
            for c in checks
            if c.required
        )

        return SystemHealth(
            app_name=ctx.settings.app_name,
            app_version=ctx.settings.app_version,
            app_env=ctx.settings.app_env.value,
            overall_status="HEALTHY" if all_ok else "DEGRADED",
            diagnostics=items,
        )
