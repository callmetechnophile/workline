"""Centralized platform data layer."""

from armourflow.data.client import PlatformDatabaseClient, get_database_client

__all__ = ["PlatformDatabaseClient", "get_database_client"]
