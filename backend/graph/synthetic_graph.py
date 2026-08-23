"""
synthetic_graph.py
------------------
Builds a live Knowledge Graph from Qdrant/SQLite pipeline data.

Produces the same {nodes, edges} shape that format_for_react_flow expects.
"""
import json
import logging

logger = logging.getLogger("SyntheticGraph")


def _slugify(text: str) -> str:
    return text.strip().lower().replace(" ", "_").replace("/", "_")[:40]


def build_synthetic_graph(project_name: str) -> dict:
    """
    Query SQLite for the most recent pipeline package that matches project_name.
    Parse BOM, papers, dependency edges, agents, and build a graph.
    """
    try:
        from backend.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Try matching by intent (project description stored as intent)
        cursor.execute(
            "SELECT data FROM packages WHERE intent LIKE ? ORDER BY id DESC LIMIT 1",
            (f"%{project_name.replace('_', ' ')}%",)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return _empty_graph(project_name)

        data = json.loads(row[0] if isinstance(row, (list, tuple)) else row["data"])
        return _build_from_data(project_name, data)

    except Exception as e:
        logger.error(f"[SyntheticGraph] Failed to build graph for '{project_name}': {e}")
        return _empty_graph(project_name)


def _build_from_data(project_name: str, data: dict) -> dict:
    nodes = []
    edges = []
    seen_ids = set()

    def add_node(node_id, label, node_type, properties=None):
        if node_id in seen_ids:
            return
        seen_ids.add(node_id)
        nodes.append({
            "id": node_id,
            "label": label,
            "type": node_type,
            "properties": properties or {}
        })

    def add_edge(source, target, rel_type):
        if source in seen_ids and target in seen_ids:
            edges.append({"source": source, "target": target, "type": rel_type})

    # ── Project root node ──────────────────────────────────────────────────────
    proj_id = f"project_{_slugify(project_name)}"
    add_node(proj_id, project_name.replace("_", " ").title(), "Project",
             {"description": data.get("intent", "")})

    # ── Components (BOM) ──────────────────────────────────────────────────────
    components = data.get("components", [])
    for comp in components[:25]:
        name  = comp.get("name") or comp.get("component") or "Unknown"
        cid   = f"comp_{_slugify(name)}"
        props = {
            "category": comp.get("category", ""),
            "cost":     comp.get("unit_price") or comp.get("cost") or 0.0,
            "quantity": comp.get("quantity", 1),
            "vendor":   comp.get("vendor", ""),
        }
        add_node(cid, name, "Component", props)
        add_edge(proj_id, cid, "USES")

        # Vendor node
        vendor = comp.get("vendor", "").strip()
        if vendor:
            vid = f"vendor_{_slugify(vendor)}"
            add_node(vid, vendor, "Vendor", {"name": vendor})
            add_edge(cid, vid, "SOURCED_FROM")

    # ── Research Papers ───────────────────────────────────────────────────────
    papers = data.get("research_papers", [])
    for paper in papers[:10]:
        title = paper.get("title", "Research Paper")
        pid   = f"paper_{_slugify(title)}"
        add_node(pid, title[:40], "ResearchPaper", {
            "authors": ", ".join(paper.get("authors", [])),
            "year":    paper.get("year", ""),
            "doi":     paper.get("doi", ""),
        })
        add_edge(proj_id, pid, "SUPPORTED_BY")

    # ── Dependency edges ─────────────────────────────────────────────────────
    deps = data.get("dependencies", [])
    for dep in deps[:30]:
        src  = dep.get("from") or dep.get("source") or ""
        tgt  = dep.get("to")   or dep.get("target") or ""
        rel  = dep.get("type", "CONNECTED_TO")
        if src and tgt:
            src_id = f"comp_{_slugify(src)}"
            tgt_id = f"comp_{_slugify(tgt)}"
            # Ensure orphan nodes still appear
            if src_id not in seen_ids:
                add_node(src_id, src, "Component")
                add_edge(proj_id, src_id, "USES")
            if tgt_id not in seen_ids:
                add_node(tgt_id, tgt, "Component")
                add_edge(proj_id, tgt_id, "USES")
            add_edge(src_id, tgt_id, rel)

    # ── AI Agents ─────────────────────────────────────────────────────────────
    AGENTS = [
        ("ExtractionAgent",  "Extraction Agent",  "Parses raw query into structured BOM"),
        ("PlannerAgent",     "Planner Agent",     "Generates roadmap & Gantt timeline"),
        ("ResearchAgent",    "Research Agent",    "Retrieves relevant research papers"),
        ("ValidationAgent",  "Validation Agent",  "Validates electrical and power rules"),
        ("OptimizationAgent","Optimization Agent","Suggests cost/weight optimizations"),
    ]
    for agent_id, agent_label, desc in AGENTS:
        aid = f"agent_{agent_id.lower()}"
        add_node(aid, agent_label, "Agent", {"description": desc})
        add_edge(proj_id, aid, "DELEGATES_TO")

    # ── Power / protocol nodes from power analysis ────────────────────────────
    power = data.get("power_analysis", {})
    rails = power.get("power_rails", []) if isinstance(power, dict) else []
    for rail in rails[:6]:
        label  = rail.get("name") or rail.get("rail") or str(rail)
        rid    = f"rail_{_slugify(str(label))}"
        add_node(rid, str(label), "Battery", {"voltage": rail.get("voltage", ""), "current": rail.get("current", "")})
        add_edge(proj_id, rid, "POWERED_BY")

    # ── Contradictions / failure modes ────────────────────────────────────────
    contradictions = data.get("contradictions", [])
    for c in contradictions[:5]:
        desc  = c.get("description") or c.get("conflict") or str(c)[:40]
        cid_f = f"fail_{_slugify(desc)}"
        add_node(cid_f, desc[:35], "FailureMode", {"severity": c.get("severity", "medium")})
        add_edge(proj_id, cid_f, "CONTRADICTS")

    return {"nodes": nodes, "edges": edges}


def _empty_graph(project_name: str) -> dict:
    """Return a minimal placeholder graph so the canvas is never completely blank."""
    proj_id = f"project_{_slugify(project_name)}"
    nodes = [
        {"id": proj_id, "label": project_name.replace("_", " ").title(), "type": "Project", "properties": {}},
        {"id": "agent_extraction",   "label": "Extraction Agent",   "type": "Agent", "properties": {"description": "Parses raw query"}},
        {"id": "agent_planner",      "label": "Planner Agent",      "type": "Agent", "properties": {"description": "Generates Gantt timeline"}},
        {"id": "agent_research",     "label": "Research Agent",     "type": "Agent", "properties": {"description": "Retrieves papers"}},
        {"id": "agent_validation",   "label": "Validation Agent",   "type": "Agent", "properties": {"description": "Validates constraints"}},
        {"id": "agent_optimization", "label": "Optimization Agent", "type": "Agent", "properties": {"description": "Cost optimizations"}},
    ]
    edges = [
        {"source": proj_id, "target": "agent_extraction",   "type": "DELEGATES_TO"},
        {"source": proj_id, "target": "agent_planner",      "type": "DELEGATES_TO"},
        {"source": proj_id, "target": "agent_research",     "type": "DELEGATES_TO"},
        {"source": proj_id, "target": "agent_validation",   "type": "DELEGATES_TO"},
        {"source": proj_id, "target": "agent_optimization", "type": "DELEGATES_TO"},
    ]
    return {"nodes": nodes, "edges": edges}
