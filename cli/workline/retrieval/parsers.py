"""
File parsers for WORKLINE project resources.
Parses .wl, .md, .txt, .json, and .csv files into normalized EngineeringRecord objects.
Extracts deep engineering semantics (MPN, subsystem, category, constraints).
"""

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from cli.workline.retrieval.record import EngineeringRecord


def infer_resource_type(rel_posix: str, data: Dict[str, Any]) -> str:
    """Infer the normalized resource type from file path and content."""
    # Check explicit type in content
    if "type" in data:
        t = str(data["type"]).lower()
        if t in ("component", "bom", "requirement", "architecture", "decision", "task", "research", "analysis"):
            return t
            
    parts = rel_posix.split("/")
    if parts:
        top = parts[0].lower()
        if top.startswith("component"):
            return "component"
        if top.startswith("req"):
            return "requirement"
        if top.startswith("arch"):
            return "architecture"
        if top.startswith("bom"):
            return "bom"
        if top.startswith("research") or top.startswith("paper"):
            return "research"
        if top.startswith("doc"):
            return "document"
        if top.startswith("analy"):
            return "analysis"
        if top.startswith("decis"):
            return "decision"
        if top.startswith("task"):
            return "task"
        if top.startswith("agent"):
            return "agent"
        if top.startswith("team"):
            return "team"
        if top.startswith("history"):
            return "activity"
            
    if rel_posix == "README.wl":
        return "project"
        
    return "document"


def parse_file_into_records(
    file_path: Path,
    rel_posix: str,
    project_id: str,
) -> List[EngineeringRecord]:
    """
    Parse a project file into one or more normalized EngineeringRecord objects.
    Extracts rich engineering metadata for indexing.
    """
    ext = file_path.suffix.lower()
    stat = file_path.stat()
    mtime = stat.st_mtime
    
    with open(file_path, "rb") as f:
        raw_bytes = f.read()
    checksum = hashlib.sha256(raw_bytes).hexdigest()
    
    # 1. Parse CSV (e.g. BOM)
    if ext == ".csv":
        return _parse_csv_records(file_path, rel_posix, project_id, checksum, mtime)
        
    # 2. Parse JSON
    if ext == ".json":
        try:
            content_str = raw_bytes.decode("utf-8")
            data = json.loads(content_str)
            res_type = infer_resource_type(rel_posix, data if isinstance(data, dict) else {})
            title = data.get("title") or data.get("name") or Path(rel_posix).stem
            return [
                EngineeringRecord(
                    record_id=f"REC-{hashlib.md5(rel_posix.encode()).hexdigest()[:10]}",
                    project_id=project_id,
                    resource_type=res_type,
                    title=str(title),
                    path=rel_posix,
                    content=content_str,
                    metadata=data if isinstance(data, dict) else {"items": data},
                    checksum=checksum,
                    mtime=mtime,
                )
            ]
        except Exception:
            pass

    # 3. Parse .wl, .md, .txt
    try:
        content_str = raw_bytes.decode("utf-8", errors="replace")
    except Exception:
        content_str = ""

    # Parse YAML content if .wl
    meta_dict: Dict[str, Any] = {}
    title = Path(rel_posix).stem
    if ext in (".wl", ".yaml", ".yml"):
        try:
            # Strip decorative headers
            lines = content_str.splitlines()
            clean_lines = []
            for l in lines:
                s = l.strip()
                if s.startswith("WORKLINE_") or (s and set(s) == {"="}):
                    continue
                clean_lines.append(l)
            parsed = yaml.safe_load("\n".join(clean_lines))
            if isinstance(parsed, dict):
                meta_dict = parsed
                title = parsed.get("name") or parsed.get("title") or parsed.get("mpn") or title
        except Exception:
            pass

    res_type = infer_resource_type(rel_posix, meta_dict)
    
    # Enrich metadata for engineering concepts
    if res_type == "component":
        meta_dict["mpn"] = meta_dict.get("mpn") or Path(rel_posix).parent.name
        meta_dict["category"] = meta_dict.get("category", "")
        meta_dict["manufacturer"] = meta_dict.get("manufacturer", "")
        meta_dict["system"] = meta_dict.get("system", "")
        meta_dict["subsystem"] = meta_dict.get("subsystem", "")
    elif res_type == "requirement":
        meta_dict["requirement_id"] = meta_dict.get("requirement_id", Path(rel_posix).stem)
        meta_dict["category"] = meta_dict.get("category", "")
        meta_dict["subsystem"] = meta_dict.get("subsystem", "")
    elif res_type == "decision":
        meta_dict["decision_id"] = meta_dict.get("decision_id", Path(rel_posix).stem)
        meta_dict["status"] = meta_dict.get("status", "")
    elif res_type == "task":
        meta_dict["task_id"] = meta_dict.get("task_id", Path(rel_posix).stem)
        meta_dict["status"] = meta_dict.get("status", "")
        meta_dict["assignee"] = meta_dict.get("assignee", "")

    # For BOM .wl files, create individual line-item records as well
    records = [
        EngineeringRecord(
            record_id=f"REC-{hashlib.md5(rel_posix.encode()).hexdigest()[:10]}",
            project_id=project_id,
            resource_type=res_type,
            title=str(title),
            path=rel_posix,
            content=content_str,
            metadata=meta_dict,
            checksum=checksum,
            mtime=mtime,
        )
    ]

    # If it's a BOM file with items list, also index items individually for granular search
    if res_type == "bom" and "items" in meta_dict and isinstance(meta_dict["items"], list):
        for idx, item in enumerate(meta_dict["items"]):
            if isinstance(item, dict):
                mpn = item.get("mpn", f"item-{idx}")
                item_rec = EngineeringRecord(
                    record_id=f"REC-BOM-{hashlib.md5(f'{rel_posix}:{idx}:{mpn}'.encode()).hexdigest()[:10]}",
                    project_id=project_id,
                    resource_type="bom",
                    title=f"BOM Item: {mpn}",
                    path=rel_posix,
                    content=yaml.dump(item, sort_keys=False),
                    metadata=item,
                    checksum=checksum,
                    mtime=mtime,
                )
                records.append(item_rec)

    return records


def _parse_csv_records(
    file_path: Path,
    rel_posix: str,
    project_id: str,
    checksum: str,
    mtime: float,
) -> List[EngineeringRecord]:
    """Parse CSV (e.g. BOM items) into discrete records."""
    records: List[EngineeringRecord] = []
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            raw_text = f.read()
            
            # Master document record
            f.seek(0)
            master_content = f.read()
            records.append(
                EngineeringRecord(
                    record_id=f"REC-{hashlib.md5(rel_posix.encode()).hexdigest()[:10]}",
                    project_id=project_id,
                    resource_type="bom",
                    title=f"BOM CSV: {Path(rel_posix).name}",
                    path=rel_posix,
                    content=master_content,
                    metadata={"total_rows": 0},
                    checksum=checksum,
                    mtime=mtime,
                )
            )
            
            f.seek(0)
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                mpn = row.get("mpn") or row.get("MPN") or row.get("Part Number") or f"row-{idx+1}"
                row_str = " | ".join(f"{k}: {v}" for k, v in row.items())
                records.append(
                    EngineeringRecord(
                        record_id=f"REC-CSV-{hashlib.md5(f'{rel_posix}:{idx}:{mpn}'.encode()).hexdigest()[:10]}",
                        project_id=project_id,
                        resource_type="bom",
                        title=f"BOM Item: {mpn}",
                        path=rel_posix,
                        content=row_str,
                        metadata=dict(row),
                        checksum=checksum,
                        mtime=mtime,
                    )
                )
    except Exception:
        pass
        
    return records
