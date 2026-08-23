import os
import sqlite3
from dotenv import load_dotenv
load_dotenv()
import json
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    DB_PATH = os.path.join(os.path.dirname(__file__), "..", "user_storage.db")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_cursor(conn):
    if hasattr(conn, "cursor_factory"):
        from psycopg2.extras import RealDictCursor
        return conn.cursor(cursor_factory=RealDictCursor)
    return conn.cursor()

def execute_query(conn, query: str, params=()):
    cursor = get_cursor(conn)
    if hasattr(conn, "cursor_factory"):
        query = query.replace("?", "%s")
    cursor.execute(query, params)
    return cursor

def init_db():
    conn = get_db_connection()
    is_postgres = hasattr(conn, "cursor_factory")
    cursor = conn.cursor()
    
    if is_postgres:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS packages (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                intent TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                risk_score INTEGER NOT NULL,
                optimization_score INTEGER NOT NULL,
                data TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                prompt TEXT NOT NULL,
                bom TEXT NOT NULL,
                power TEXT NOT NULL,
                dependencies TEXT NOT NULL,
                wiring TEXT NOT NULL,
                papers TEXT NOT NULL,
                gantt TEXT NOT NULL,
                code TEXT NOT NULL,
                exports TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id SERIAL PRIMARY KEY,
                team_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL,
                joined_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                permissions TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                project_id TEXT NOT NULL,
                section TEXT NOT NULL,
                author TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id SERIAL PRIMARY KEY,
                team_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_versions (
                id SERIAL PRIMARY KEY,
                project_id TEXT NOT NULL,
                version_num INTEGER NOT NULL,
                data TEXT NOT NULL,
                modified_by TEXT NOT NULL,
                change_summary TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                intent TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                risk_score INTEGER NOT NULL,
                optimization_score INTEGER NOT NULL,
                data TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                prompt TEXT NOT NULL,
                bom TEXT NOT NULL,
                power TEXT NOT NULL,
                dependencies TEXT NOT NULL,
                wiring TEXT NOT NULL,
                papers TEXT NOT NULL,
                gantt TEXT NOT NULL,
                code TEXT NOT NULL,
                exports TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL,
                joined_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                permissions TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                section TEXT NOT NULL,
                author TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                version_num INTEGER NOT NULL,
                data TEXT NOT NULL,
                modified_by TEXT NOT NULL,
                change_summary TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        # Insert default roles into roles table
        try:
            cursor.execute("INSERT OR IGNORE INTO roles (name, permissions) VALUES ('Owner', 'full')")
            cursor.execute("INSERT OR IGNORE INTO roles (name, permissions) VALUES ('Engineer', 'technical')")
            cursor.execute("INSERT OR IGNORE INTO roles (name, permissions) VALUES ('Reviewer', 'comment')")
            cursor.execute("INSERT OR IGNORE INTO roles (name, permissions) VALUES ('Viewer', 'read')")
        except Exception:
            pass

    # Dynamic Schema Upgrades (Projects, Packages, Teams UUID & Team Invitations)
    for table_name, columns in [
        ("packages", [
            ("project_name", "TEXT"),
            ("system_specification", "TEXT"),
            ("target_days", "INTEGER"),
            ("engineering_template", "TEXT"),
            ("team_id", "TEXT"),
            ("project_id", "TEXT"),
            ("status", "TEXT DEFAULT 'active'"),
        ]),
        ("projects", [
            ("project_name", "TEXT"),
            ("system_specification", "TEXT"),
            ("target_timeline_days", "INTEGER"),
            ("engineering_template", "TEXT"),
            ("team_id", "TEXT"),
            ("project_id", "TEXT"),
            ("status", "TEXT DEFAULT 'active'"),
        ]),
    ]:
        for col_name, col_type in columns:
            try:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
            except Exception:
                pass

    try:
        cursor.execute("ALTER TABLE teams ADD COLUMN uuid TEXT")
    except Exception:
        pass

    # Update existing teams with UUIDs if they are null/empty
    try:
        cursor.execute("SELECT id, uuid FROM teams")
        rows = cursor.fetchall()
        import uuid
        for row in rows:
            if not row or not row[1] if not is_postgres else not row["uuid"]:
                new_uuid = str(uuid.uuid4())
                if is_postgres:
                    cursor.execute("UPDATE teams SET uuid = %s WHERE id = %s", (new_uuid, row["id"]))
                else:
                    cursor.execute("UPDATE teams SET uuid = ? WHERE id = ?", (new_uuid, row["id"]))
    except Exception as e:
        print(f"[DB Schema Upgrade Warning] Could not update team UUIDs: {e}")

    # Create Team Invitations table
    if is_postgres:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_invitations (
                id SERIAL PRIMARY KEY,
                team_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                receipt_id TEXT
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                receipt_id TEXT
            )
        """)

    # Re-create Calendar Exports table with correct fields
    try:
        cursor.execute("DROP TABLE IF EXISTS calendar_exports")
    except Exception:
        pass

    if is_postgres:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calendar_exports (
                id SERIAL PRIMARY KEY,
                project_id TEXT NOT NULL,
                export_time TEXT NOT NULL,
                export_type TEXT NOT NULL,
                calendar_link TEXT,
                tasks_exported TEXT,
                status TEXT NOT NULL
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calendar_exports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                export_time TEXT NOT NULL,
                export_type TEXT NOT NULL,
                calendar_link TEXT,
                tasks_exported TEXT,
                status TEXT NOT NULL
            )
        """)

    conn.commit()
    conn.close()

def save_package(
    user_id: str,
    intent: str,
    readiness: int,
    risk: int,
    optimization: int,
    data: dict,
    project_name: str = None,
    system_specification: str = None,
    target_days: int = 30,
    engineering_template: str = None,
    team_id: str = None,
    project_id: str = None,
    status: str = "active",
):
    conn = get_db_connection()
    timestamp = datetime.utcnow().isoformat()
    data_str = json.dumps(data)
    
    spec = system_specification or intent
    p_name = (project_name or "").strip() or spec[:50].strip() or "Untitled Engineering Project"
    
    query = """
        INSERT INTO packages (
            user_id, intent, readiness_score, risk_score, optimization_score, data, timestamp,
            project_name, system_specification, target_days, engineering_template, team_id, project_id, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    execute_query(conn, query, (
        user_id, intent, readiness, risk, optimization, data_str, timestamp,
        p_name, spec, target_days, engineering_template or "", team_id or "", project_id or "", status
    ))
    conn.commit()
    conn.close()

def get_user_history(user_id: str):
    conn = get_db_connection()
    query = """
        SELECT id, intent, readiness_score, risk_score, optimization_score, data, timestamp,
               project_name, system_specification, target_days, engineering_template, team_id, project_id, status
        FROM packages 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    """
    try:
        cursor = execute_query(conn, query, (user_id,))
        rows = cursor.fetchall()
    except Exception:
        # Fallback for legacy tables if columns are missing
        query = """
            SELECT id, intent, readiness_score, risk_score, optimization_score, data, timestamp 
            FROM packages 
            WHERE user_id = ? 
            ORDER BY timestamp DESC
        """
        cursor = execute_query(conn, query, (user_id,))
        rows = cursor.fetchall()

    conn.close()
    
    history = []
    for row in rows:
        intent_val = row["intent"]
        p_name = None
        try:
            p_name = row["project_name"]
        except Exception:
            pass
        if not p_name or not str(p_name).strip():
            p_name = "Untitled Engineering Project"

        spec = None
        try:
            spec = row["system_specification"]
        except Exception:
            pass
        if not spec:
            spec = intent_val

        t_days = 30
        try:
            t_days = row["target_days"] or 30
        except Exception:
            pass

        t_id = None
        try:
            t_id = row["team_id"]
        except Exception:
            pass

        p_id = None
        try:
            p_id = row["project_id"]
        except Exception:
            pass

        template = None
        try:
            template = row["engineering_template"]
        except Exception:
            pass

        st = "active"
        try:
            st = row["status"] or "active"
        except Exception:
            pass

        history.append({
            "id": row["id"],
            "project_id": p_id or f"PROJ-{row['id']:04d}",
            "project_name": p_name,
            "system_specification": spec,
            "intent": intent_val,
            "target_days": t_days,
            "engineering_template": template,
            "team_id": t_id,
            "status": st,
            "readiness_score": row["readiness_score"],
            "risk_score": row["risk_score"],
            "optimization_score": row["optimization_score"],
            "data": json.loads(row["data"]),
            "timestamp": row["timestamp"]
        })
    return history
