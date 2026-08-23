from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ResearchRequest(BaseModel):
    project_name: Optional[str] = None
    system_specification: Optional[str] = None
    intent: Optional[str] = None
    target_days: Optional[int] = 30
    engineering_template: Optional[str] = None
    team_id: Optional[str] = None
    project_id: Optional[str] = None

class ExportResult(BaseModel):
    filename: str
    url: str
    status: str

class ResearchResponse(BaseModel):
    project_id: str = "PROJ-DEFAULT"
    project_name: str = "Untitled Engineering Project"
    system_specification: str = ""
    intent: str
    target_timeline_days: int = 30
    engineering_template: Optional[str] = None
    team_id: Optional[str] = None
    owner_id: Optional[str] = None
    status: str = "active"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    components: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    papers: List[Dict[str, Any]]
    paper_summary: Dict[str, Any]
    validation: Dict[str, Any]
    optimization: Dict[str, Any]
    roadmap: List[Dict[str, Any]]
    gantt: List[Dict[str, Any]]
    exports: Dict[str, ExportResult]
    decision_trace: List[Dict[str, str]]
    audit_trail: List[Dict[str, Any]]
    blocked_test_success: bool
    cost_summary: Optional[Dict[str, Any]] = None
    alternatives: Optional[List[Dict[str, Any]]] = None
    voltage_risks: Optional[List[Dict[str, Any]]] = None
    pin_mapping: Optional[List[Dict[str, Any]]] = None
    bom_exports: Optional[Dict[str, Any]] = None
    datasheets: Optional[List[Dict[str, Any]]] = None
    power_analysis: Optional[Dict[str, Any]] = None
    dependency_graph: Optional[Dict[str, Any]] = None
    wiring_diagram: Optional[Dict[str, Any]] = None
    contradictions: Optional[List[Dict[str, Any]]] = None
    thermal_analysis: Optional[List[Dict[str, Any]]] = None
    team_workspace: Optional[Dict[str, Any]] = None
    version_history: Optional[Dict[str, Any]] = None

