"""Environment mode resolution and checking."""

import os
from enum import Enum


class EnvironmentMode(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "test"
    PRODUCTION = "production"


def get_environment() -> EnvironmentMode:
    """Resolve current environment from APP_ENV or WORKLINE_ENV."""
    raw = os.getenv("APP_ENV") or os.getenv("WORKLINE_ENV") or "development"
    raw_lower = raw.strip().lower()
    if raw_lower in ("prod", "production"):
        return EnvironmentMode.PRODUCTION
    elif raw_lower in ("test", "testing"):
        return EnvironmentMode.TESTING
    return EnvironmentMode.DEVELOPMENT
