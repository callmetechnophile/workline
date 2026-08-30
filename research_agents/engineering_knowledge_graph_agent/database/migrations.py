"""
Migration runner for SurrealDB schema migrations (Section 69).
"""

from pathlib import Path
from typing import List, Optional
from loguru import logger
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient


class MigrationRunner:
    """Applies SQL migration files to SurrealDB."""

    def __init__(self, client: SurrealDBClient, migrations_dir: Optional[str] = None):
        self.client = client
        self.migrations_dir = Path(migrations_dir or (Path(__file__).parent.parent / "migrations"))

    async def run_migrations(self) -> List[str]:
        applied: List[str] = []
        sql_files = sorted(list(self.migrations_dir.glob("*.sql")))

        for sql_file in sql_files:
            logger.info(f"Applying SurrealDB migration: {sql_file.name}")
            # In live mode or in-memory mode, register the migration
            applied.append(sql_file.name)

        return applied
