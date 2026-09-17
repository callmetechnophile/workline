"""
Configuration management and versioned operational baselines engine.
"""

import datetime
from typing import List, Optional
from research_agents.deployment_operations.schemas import (
    ConfigurationItem,
    OperationalBaseline,
    OperationalMode,
)


class ConfigurationEngine:
    """Manages configuration items, environment overrides, and operational baselines."""

    def create_operational_baseline(
        self,
        project_id: str,
        system_id: str,
        configurations: Optional[List[ConfigurationItem]] = None,
    ) -> OperationalBaseline:
        default_configs = configurations or [
            ConfigurationItem(item_id="CFG-01", key="MAX_OPERATING_TEMP_C", value="65.0", version="1.0.0"),
            ConfigurationItem(item_id="CFG-02", key="CONTROL_FABRIC_HEARTBEAT_SEC", value="5.0", version="1.0.0"),
            ConfigurationItem(item_id="CFG-03", key="LOG_LEVEL", value="INFO", version="1.0.0"),
            ConfigurationItem(item_id="CFG-04", key="AUTO_FAILOVER_ENABLED", value="true", version="1.0.0"),
        ]

        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return OperationalBaseline(
            baseline_id=f"BASE-{system_id}-V1",
            project_id=project_id,
            system_id=system_id,
            version="1.0.0",
            timestamp=now_str,
            configurations=default_configs,
            approved_operating_modes=[
                OperationalMode.NORMAL,
                OperationalMode.STARTUP,
                OperationalMode.SHUTDOWN,
                OperationalMode.MAINTENANCE,
                OperationalMode.DEGRADED,
            ],
            is_active=True,
        )
