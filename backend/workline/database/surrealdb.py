"""SurrealDB asynchronous connection manager and lifespan handler for Workline."""

import asyncio
import os
import socket
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from dotenv import load_dotenv
import httpx
from surrealdb import AsyncSurreal

load_dotenv()


def is_port_open(url: str, timeout: float = 0.4) -> bool:
    """Fast non-blocking TCP socket check to determine if database port is listening."""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or "127.0.0.1"
        if host == "localhost":
            host = "127.0.0.1"
        if parsed.port:
            port = parsed.port
        elif parsed.scheme in ("wss", "https"):
            port = 443
        elif "8001" in url:
            port = 8001
        elif "8000" in url:
            port = 8000
        else:
            port = 80
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
        self.url = os.environ.get("SURREALDB_URL", os.environ.get("WORKLINE_SURREALDB_URL", "http://127.0.0.1:8001"))
        self.namespace = os.environ.get("SURREALDB_NAMESPACE", os.environ.get("WORKLINE_SURREALDB_NAMESPACE", "main"))
        self.database = os.environ.get("SURREALDB_DATABASE", os.environ.get("WORKLINE_SURREALDB_DATABASE", "main"))
        self.user = os.environ.get("SURREALDB_USER", os.environ.get("WORKLINE_SURREALDB_USER", "root"))
        self.password = os.environ.get("SURREALDB_PASSWORD", os.environ.get("WORKLINE_SURREALDB_PASSWORD", "root"))

        self.client: Optional[AsyncSurreal] = None
        self._is_connected = False

    async def connect(self) -> bool:
        """Establish asynchronous connection and authenticate with SurrealDB."""
        # Socket pre-check with 2.5s timeout for cloud endpoints
        if not is_port_open(self.url, timeout=2.5):
            self._is_connected = False
            return False

        try:
            conn_url = self.url.rstrip("/")
            if conn_url.startswith("http://"):
                conn_url = conn_url.replace("http://", "ws://")
            elif conn_url.startswith("https://"):
                conn_url = conn_url.replace("https://", "wss://")
            if not conn_url.endswith("/rpc"):
                conn_url += "/rpc"

            self.client = AsyncSurreal(conn_url)
            await asyncio.wait_for(self.client.connect(), timeout=5.0)
            try:
                await asyncio.wait_for(self.client.signin({"username": self.user, "password": self.password}), timeout=5.0)
            except Exception:
                await asyncio.wait_for(self.client.signin({"user": self.user, "pass": self.password}), timeout=5.0)

            await asyncio.wait_for(self.client.use(self.namespace, self.database), timeout=5.0)
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
        """Return connectivity status with fast cached TTL."""
        if self.client and self._is_connected:
            return True
        now = time.time()
        if hasattr(self, "_last_conn_check") and (now - self._last_conn_check < 30.0):
            return getattr(self, "_last_conn_result", False)
        self._last_conn_check = now
        res = await self.check_http_health()
        self._last_conn_result = res
        return res

    async def query(self, sql: str, vars: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a SurrealQL query."""
        if self.client and self._is_connected:
            try:
                return await self.client.query(sql, vars or {})
            except Exception:
                pass

        if not is_port_open(self.url, timeout=2.5):
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

    async def select(self, thing: str) -> Any:
        """Select records from a table or by ID."""
        if not self._is_connected:
            await self.connect()
        if self.client and self._is_connected:
            try:
                return await self.client.select(thing)
            except Exception:
                pass
        return await self.query(f"SELECT * FROM {thing};")

    async def create(self, thing: str, data: Dict[str, Any]) -> Any:
        """Create a new record in SurrealDB."""
        if not self._is_connected:
            await self.connect()
        if self.client and self._is_connected:
            try:
                return await self.client.create(thing, data)
            except Exception:
                pass
        return await self.query(f"CREATE {thing} CONTENT $data;", {"data": data})

    async def upsert(self, thing: str, data: Dict[str, Any]) -> Any:
        """Upsert a record in SurrealDB."""
        if not self._is_connected:
            await self.connect()
        if self.client and self._is_connected:
            try:
                return await self.client.upsert(thing, data)
            except Exception:
                pass
        return await self.query(f"UPSERT {thing} CONTENT $data;", {"data": data})

    async def delete(self, thing: str) -> Any:
        """Delete records from a table or by ID."""
        if not self._is_connected:
            await self.connect()
        if self.client and self._is_connected:
            try:
                return await self.client.delete(thing)
            except Exception:
                pass
        return await self.query(f"DELETE {thing};")


# Singleton instance
surreal_db = SurrealDBManager()
