"""SQLite data exporter for migrating legacy Workline database to SurrealDB."""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


def export_sqlite_data(db_path: Optional[Path] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Read legacy SQLite database (user_storage.db) and export normalized records.
    """
    target = db_path or Path(__file__).resolve().parent.parent.parent.parent / "user_storage.db"
    if not target.exists():
        return {
            "projects": [],
            "teams": [],
            "members": [],
            "team_invitations": [],
            "comments": [],
            "project_versions": [],
            "workspace_bundles": [],
            "activity_logs": [],
        }

    conn = sqlite3.connect(str(target))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    export_data: Dict[str, List[Dict[str, Any]]] = {}

    tables = [
        "projects",
        "teams",
        "members",
        "team_invitations",
        "comments",
        "project_versions",
        "workspace_bundles",
        "activity_logs",
    ]

    for table in tables:
        export_data[table] = []
        try:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            for row in rows:
                row_dict = dict(row)
                # Parse stringified JSON fields if present
                for key in ("bom", "power", "dependencies", "wiring", "papers", "gantt", "data"):
                    if key in row_dict and isinstance(row_dict[key], str):
                        try:
                            row_dict[key] = json.loads(row_dict[key])
                        except Exception:
                            pass
                export_data[table].append(row_dict)
        except sqlite3.OperationalError:
            # Table might not exist in an empty database
            pass

    conn.close()
    return export_data
