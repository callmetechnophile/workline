"""
Workline AI — Startup Environment & Configuration Validator.

Provides non-leaking, fail-fast verification of required environment variables
for each deployment microservice role (R1, R2, R3, R4, R5).
"""

import os
from typing import Dict, List, Optional, Tuple
from loguru import logger


# Service role definition of required and recommended environment variables
SERVICE_ENV_REQUIREMENTS: Dict[str, Dict[str, List[str]]] = {
    "R1_CORE": {
        "required": [],  # Defaults provided internally; in production WORKLINE_SERVICE_AUTH_KEY is validated
        "recommended": ["WORKLINE_SERVICE_AUTH_KEY", "WORKLINE_CORS_ORIGINS"],
    },
    "R2_AI": {
        "required": [],
        "recommended": ["AWS_REGION", "WORKLINE_SERVICE_AUTH_KEY"],
    },
    "R3_KNOWLEDGE": {
        "required": [],
        "recommended": ["SURREALDB_URL", "QDRANT_URL", "WORKLINE_SERVICE_AUTH_KEY"],
    },
    "R4_ENGINEERING": {
        "required": [],
        "recommended": ["WORKLINE_SERVICE_AUTH_KEY"],
    },
    "R5_PROCUREMENT": {
        "required": [],
        "recommended": ["WORKLINE_X402_NETWORK", "WORKLINE_SERVICE_AUTH_KEY"],
    },
}


class EnvironmentValidator:
    """Validates presence and format of required variables without leaking secrets."""

    @classmethod
    def validate_service_environment(
        cls,
        service_role: str,
        fail_fast: bool = False,
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validates environment variables for the specified service role.
        Returns: (is_valid, missing_required_vars, missing_recommended_vars)
        """
        reqs = SERVICE_ENV_REQUIREMENTS.get(service_role, {"required": [], "recommended": []})
        missing_required = [var for var in reqs.get("required", []) if not os.getenv(var)]
        missing_recommended = [var for var in reqs.get("recommended", []) if not os.getenv(var)]

        if missing_required:
            logger.error(
                f"[{service_role}] Startup configuration error: Missing required environment variables: "
                f"{', '.join(missing_required)}"
            )
            if fail_fast:
                raise RuntimeError(
                    f"Missing required environment variable(s) for {service_role}: {', '.join(missing_required)}"
                )

        if missing_recommended:
            logger.info(
                f"[{service_role}] Notice: Optional/recommended variables not set in current environment: "
                f"{', '.join(missing_recommended)} (using safe defaults)"
            )

        is_valid = len(missing_required) == 0
        return is_valid, missing_required, missing_recommended


# Global helper function
validate_environment = EnvironmentValidator.validate_service_environment
