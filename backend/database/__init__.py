import os
import sqlite3
import json
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db_connection():
    DB_PATH = os.path.join(os.path.dirname(__file__), "..", "user_storage.db")
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
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
    
    if not is_postgres:
        try:
            cursor.execute("PRAGMA journal_mode=WAL;")
        except Exception:
            pass
    
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                status TEXT NOT NULL,
                current_stage TEXT,
                requirements_revision INTEGER DEFAULT 0,
                research_revision INTEGER DEFAULT 0,
                architecture_revision INTEGER DEFAULT 0,
                bom_revision INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                error TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_stage_runs (
                id SERIAL PRIMARY KEY,
                run_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                stage TEXT NOT NULL,
                status TEXT NOT NULL,
                input_revision_ids TEXT,
                output_revision_id INTEGER,
                stage_data TEXT,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                error TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pcb_visualizations (

                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                image_url TEXT,
                image_data TEXT,
                storage_key TEXT,
                generation_prompt_hash TEXT,
                model TEXT NOT NULL,
                status TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pcb_visualizations (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                image_url TEXT,
                image_data TEXT,
                storage_key TEXT,
                generation_prompt_hash TEXT,
                model TEXT NOT NULL,
                status TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                status TEXT NOT NULL,
                current_stage TEXT,
                requirements_revision INTEGER DEFAULT 0,
                research_revision INTEGER DEFAULT 0,
                architecture_revision INTEGER DEFAULT 0,
                bom_revision INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                error TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_stage_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                stage TEXT NOT NULL,
                status TEXT NOT NULL,
                input_revision_ids TEXT,
                output_revision_id INTEGER,
                stage_data TEXT,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                error TEXT
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


def save_pipeline_run(
    run_id: str,
    project_id: str,
    status: str = "RUNNING",
    current_stage: str = "R2_REQUIREMENTS",
    requirements_rev: int = 0,
    research_rev: int = 0,
    architecture_rev: int = 0,
    bom_rev: int = 0,
):
    conn = get_db_connection()
    is_postgres = hasattr(conn, "cursor_factory")
    created_at = datetime.utcnow().isoformat()
    if is_postgres:
        execute_query(conn, "DELETE FROM pipeline_stage_runs WHERE run_id = %s", (run_id,))
        query = """
            INSERT INTO pipeline_runs (
                run_id, project_id, status, current_stage,
                requirements_revision, research_revision, architecture_revision, bom_revision,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (run_id) DO UPDATE SET
                status = EXCLUDED.status,
                current_stage = EXCLUDED.current_stage,
                requirements_revision = EXCLUDED.requirements_revision,
                research_revision = EXCLUDED.research_revision,
                architecture_revision = EXCLUDED.architecture_revision,
                bom_revision = EXCLUDED.bom_revision
        """
    else:
        execute_query(conn, "DELETE FROM pipeline_stage_runs WHERE run_id = ?", (run_id,))
        query = """
            INSERT OR REPLACE INTO pipeline_runs (
                run_id, project_id, status, current_stage,
                requirements_revision, research_revision, architecture_revision, bom_revision,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    execute_query(conn, query, (
        run_id, project_id, status, current_stage,
        requirements_rev, research_rev, architecture_rev, bom_rev,
        created_at
    ))
    conn.commit()
    conn.close()


def update_pipeline_run(
    run_id: str,
    status: str,
    current_stage: str = None,
    requirements_rev: int = None,
    research_rev: int = None,
    architecture_rev: int = None,
    bom_rev: int = None,
    error: str = None,
):
    conn = get_db_connection()
    completed_at = datetime.utcnow().isoformat() if status in ["COMPLETED", "FAILED"] else None
    
    updates = ["status = ?"]
    params = [status]
    
    if current_stage is not None:
        updates.append("current_stage = ?")
        params.append(current_stage)
    if requirements_rev is not None:
        updates.append("requirements_revision = ?")
        params.append(requirements_rev)
    if research_rev is not None:
        updates.append("research_revision = ?")
        params.append(research_rev)
    if architecture_rev is not None:
        updates.append("architecture_revision = ?")
        params.append(architecture_rev)
    if bom_rev is not None:
        updates.append("bom_revision = ?")
        params.append(bom_rev)
    if completed_at is not None:
        updates.append("completed_at = ?")
        params.append(completed_at)
    if error is not None:
        updates.append("error = ?")
        params.append(error)
        
    params.append(run_id)
    query = f"UPDATE pipeline_runs SET {', '.join(updates)} WHERE run_id = ?"
    execute_query(conn, query, tuple(params))
    conn.commit()
    conn.close()


def get_pipeline_run(run_id: str):
    conn = get_db_connection()
    query = "SELECT * FROM pipeline_runs WHERE run_id = ?"
    cursor = execute_query(conn, query, (run_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_pipeline_runs_for_project(project_id: str):
    conn = get_db_connection()
    query = "SELECT * FROM pipeline_runs WHERE project_id = ? ORDER BY created_at DESC"
    cursor = execute_query(conn, query, (project_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_pipeline_stage_run(
    run_id: str,
    project_id: str,
    stage: str,
    status: str,
    input_revision_ids: dict = None,
    output_revision_id: int = None,
    stage_data: dict = None,
    error: str = None,
):
    conn = get_db_connection()
    now_iso = datetime.utcnow().isoformat()
    # Check if stage already exists for this run
    check_query = "SELECT id FROM pipeline_stage_runs WHERE run_id = ? AND stage = ?"
    cursor = execute_query(conn, check_query, (run_id, stage))
    existing = cursor.fetchone()

    if existing:
        update_query = """
            UPDATE pipeline_stage_runs SET
                status = ?,
                input_revision_ids = COALESCE(?, input_revision_ids),
                output_revision_id = COALESCE(?, output_revision_id),
                stage_data = COALESCE(?, stage_data),
                completed_at = ?,
                error = ?
            WHERE run_id = ? AND stage = ?
        """
        input_revs_json = json.dumps(input_revision_ids) if input_revision_ids is not None else None
        stage_data_json = json.dumps(stage_data) if stage_data is not None else None
        completed_at = now_iso if status in ["COMPLETED", "FAILED"] else None
        execute_query(conn, update_query, (
            status, input_revs_json, output_revision_id, stage_data_json, completed_at, error, run_id, stage
        ))
    else:
        insert_query = """
            INSERT INTO pipeline_stage_runs (
                run_id, project_id, stage, status,
                input_revision_ids, output_revision_id, stage_data,
                started_at, completed_at, error
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        execute_query(conn, insert_query, (
            run_id, project_id, stage, status,
            json.dumps(input_revision_ids or {}), output_revision_id,
            json.dumps(stage_data or {}), now_iso, now_iso if status in ["COMPLETED", "FAILED"] else None, error
        ))
    conn.commit()
    conn.close()


def get_pipeline_stages_for_run(run_id: str):
    conn = get_db_connection()
    query = "SELECT * FROM pipeline_stage_runs WHERE run_id = ? ORDER BY id ASC"
    cursor = execute_query(conn, query, (run_id,))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        try:
            d["input_revision_ids"] = json.loads(d["input_revision_ids"])
        except Exception:
            pass
        try:
            d["stage_data"] = json.loads(d["stage_data"])
        except Exception:
            pass
        results.append(d)
    return results


def save_pcb_visualization(
    project_id: str,
    image_url: Optional[str] = None,
    image_data: Optional[str] = None,
    storage_key: Optional[str] = None,
    generation_prompt_hash: Optional[str] = None,
    model: str = "PaperBanana",
    status: str = "COMPLETED",
    metadata: Optional[Dict[str, Any]] = None,
    visualization_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Persists a generated PCB visualization scoped strictly by project_id."""
    conn = get_db_connection()
    now_iso = datetime.utcnow().isoformat()
    vis_id = visualization_id or f"pcb_vis_{uuid.uuid4().hex[:10]}"
    
    # Check if project already has a visualization
    cursor = execute_query(conn, "SELECT id FROM pcb_visualizations WHERE project_id = ?", (project_id,))
    existing = cursor.fetchone()
    
    meta_json = json.dumps(metadata or {})
    
    if existing:
        update_query = """
            UPDATE pcb_visualizations SET
                image_url = COALESCE(?, image_url),
                image_data = COALESCE(?, image_data),
                storage_key = COALESCE(?, storage_key),
                generation_prompt_hash = COALESCE(?, generation_prompt_hash),
                model = ?,
                status = ?,
                metadata = ?,
                updated_at = ?
            WHERE project_id = ?
        """
        execute_query(conn, update_query, (
            image_url, image_data, storage_key, generation_prompt_hash,
            model, status, meta_json, now_iso, project_id
        ))
        vis_id = existing["id"] if isinstance(existing, sqlite3.Row) or isinstance(existing, dict) else existing[0]
    else:
        insert_query = """
            INSERT INTO pcb_visualizations (
                id, project_id, image_url, image_data, storage_key,
                generation_prompt_hash, model, status, metadata,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        execute_query(conn, insert_query, (
            vis_id, project_id, image_url, image_data, storage_key,
            generation_prompt_hash, model, status, meta_json,
            now_iso, now_iso
        ))
        
    conn.commit()
    conn.close()
    
    return {
        "id": vis_id,
        "project_id": project_id,
        "image_url": image_url,
        "image_data": image_data,
        "storage_key": storage_key,
        "generation_prompt_hash": generation_prompt_hash,
        "model": model,
        "status": status,
        "metadata": metadata or {},
        "created_at": now_iso,
        "updated_at": now_iso,
    }


def get_pcb_visualization(project_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = execute_query(conn, "SELECT * FROM pcb_visualizations WHERE project_id = ?", (project_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    try:
        d["metadata"] = json.loads(d["metadata"])
    except Exception:
        d["metadata"] = {}
    return d


