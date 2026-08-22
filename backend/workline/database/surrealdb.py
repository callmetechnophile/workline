"""SurrealDB asynchronous connection manager and lifespan handler for Workline."""

import asyncio
import os
import socket
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import httpx
from surrealdb import AsyncSurreal


def is_port_open(url: str, timeout: float = 0.1) -> bool:
    """Fast non-blocking TCP socket check to determine if database port is listening."""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or "127.0.0.1"
        if host == "localhost":
            host = "127.0.0.1"
        port = parsed.port or (8001 if "8001" in url else 8000)
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


class SurrealDBManager:
    """
    Manages connections and transactions with SurrealDB.
    Supports asynchronous client access and fallback REST querying.
    """

    def __init__(self):
        self.url = os.environ.get("WORKLINE_SURREALDB_URL", "http://127.0.0.1:8001")
        self.namespace = os.environ.get("WORKLINE_SURREALDB_NAMESPACE", "workline")
        self.database = os.environ.get("WORKLINE_SURREALDB_DATABASE", "engineering")
        self.user = os.environ.get("WORKLINE_SURREALDB_USER", "root")
        self.password = os.environ.get("WORKLINE_SURREALDB_PASSWORD", "root")

        self.client: Optional[AsyncSurreal] = None
        self._is_connected = False

    async def connect(self) -> bool:
        """Establish asynchronous connection and authenticate with SurrealDB."""
        # Ultra-fast socket pre-check (<1ms)
        if not is_port_open(self.url):
            self._is_connected = False
            return False

        try:
            conn_url = self.url
            if conn_url.startswith("http://"):
                conn_url = conn_url.replace("http://", "ws://") + "/rpc"
            elif conn_url.startswith("https://"):
                conn_url = conn_url.replace("https://", "wss://") + "/rpc"

            self.client = AsyncSurreal(conn_url)
            await asyncio.wait_for(self.client.connect(), timeout=1.0)
            await asyncio.wait_for(self.client.signin({"user": self.user, "pass": self.password}), timeout=1.0)
            await asyncio.wait_for(self.client.use(self.namespace, self.database), timeout=1.0)
            self._is_connected = True
            return True
        except Exception:
            self._is_connected = False
            return False

    async def close(self) -> None:
        """Close SurrealDB client connection."""
        if self.client:
            try:
                await self.client.close()
            except Exception:
                pass
        self._is_connected = False

    async def check_http_health(self) -> bool:
        """Verify SurrealDB availability."""
        if not is_port_open(self.url):
            return False
        try:
            http_url = self.url.rstrip("/")
            if http_url.startswith("ws://"):
                http_url = http_url.replace("ws://", "http://").replace("/rpc", "")
            elif http_url.startswith("wss://"):
                http_url = http_url.replace("wss://", "https://").replace("/rpc", "")

            async with httpx.AsyncClient(timeout=0.3) as client:
                res = await client.get(f"{http_url}/health")
                return res.status_code == 200
        except Exception:
            return False

    async def is_connected(self) -> bool:
        """Return connectivity status."""
        if self.client and self._is_connected:
            return True
        return await self.check_http_health()

    async def query(self, sql: str, vars: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a SurrealQL query."""
        if self.client and self._is_connected:
            try:
                return await self.client.query(sql, vars or {})
            except Exception:
                pass

        if not is_port_open(self.url):
            raise ConnectionError("SurrealDB service is offline.")

        http_url = self.url.rstrip("/")
        if http_url.startswith("ws://"):
            http_url = http_url.replace("ws://", "http://").replace("/rpc", "")

        headers = {
            "Accept": "application/json",
            "NS": self.namespace,
            "DB": self.database,
        }
        auth = (self.user, self.password)

        async with httpx.AsyncClient(timeout=3.0) as client:
            res = await client.post(f"{http_url}/sql", content=sql, headers=headers, auth=auth)
            if res.status_code in (200, 201):
                return res.json()
            raise RuntimeError(f"SurrealDB query failed with status {res.status_code}: {res.text}")


# Singleton instance
surreal_db = SurrealDBManager()
