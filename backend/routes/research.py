from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from backend.schemas.research_schemas import ResearchRequest, ResearchResponse
from backend.agents.planner_agent import run_engineering_pipeline

router = APIRouter(prefix="/api")

class ChatRequest(BaseModel):
    message: str
    intent: str
    recommendation: str

@router.post("/research", response_model=ResearchResponse)
def execute_research(payload: ResearchRequest):
    try:
        spec = (payload.system_specification or payload.intent or "").strip()
        if not spec:
            raise HTTPException(status_code=400, detail="System specification & engineering goal cannot be empty")
        
        raw_name = payload.project_name
        if raw_name is not None and not raw_name.strip():
            raise HTTPException(status_code=400, detail="Project name cannot be empty or whitespace only")
            
        p_name = raw_name.strip() if raw_name else spec[:50].strip()
        target_days = payload.target_days or 30

        result = run_engineering_pipeline(
            user_intent=spec,
            target_days=target_days,
            project_name=p_name,
            engineering_template=payload.engineering_template,
            team_id=payload.team_id,
            project_id=payload.project_id,
        )
        if isinstance(result, dict):
            if "components" not in result and "bom" in result:
                result["components"] = result["bom"]
            if "papers" not in result and "research_papers" in result:
                result["papers"] = result["research_papers"]
            if "paper_summary" not in result and "research_summary" in result:
                result["paper_summary"] = {"summary": result.get("research_summary", "")}
            if "exports" not in result:
                result["exports"] = {}
            if "decision_trace" not in result:
                result["decision_trace"] = []
            if "blocked_test_success" not in result:
                result["blocked_test_success"] = False
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engineering pipeline failed: {str(e)}")


class HarvestRequest(BaseModel):
    project_id: Optional[str] = "PROJ-DEFAULT"
    project_name: Optional[str] = None
    system_specification: Optional[str] = None
    keywords: Optional[str] = None


@router.get("/research/papers")
def get_research_papers(project_id: Optional[str] = None, query: Optional[str] = None):
    """Retrieve peer-reviewed research papers for an active project or search query."""
    try:
        from backend.database import get_pipeline_runs_for_project, get_pipeline_stages_for_run
        from backend.workline.pipeline.scholarly_research import search_scholarly_research

        resolved_id = project_id or "PROJ-DEFAULT"
        
        # 1. Try to fetch from completed pipeline stages for this project
        runs = get_pipeline_runs_for_project(resolved_id)
        if runs:
            for run in runs:
                stages = get_pipeline_stages_for_run(run["run_id"])
                for st in stages:
                    if st.get("stage") == "R3_RESEARCH" and st.get("stage_data"):
                        data = st["stage_data"]
                        if data.get("research_papers"):
                            return {
                                "project_id": resolved_id,
                                "papers": data.get("research_papers", []),
                                "research_papers": data.get("research_papers", []),
                                "summary": data.get("findings", ""),
                                "contradictions": data.get("contradictions", []),
                            }

        # 2. If not found in runs or query provided, run live scholarly search
        search_query = (query or resolved_id.replace("PROJ-", "")).strip() or "Hardware Engineering Architecture"
        papers = search_scholarly_research(
            idea=search_query,
            requirements=[],
            domain="Hardware Engineering",
            project_id=resolved_id,
            max_papers=6,
        )
        return {
            "project_id": resolved_id,
            "papers": papers,
            "research_papers": papers,
            "summary": f"Synthesized peer-reviewed engineering literature for '{search_query}'.",
            "contradictions": [],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch research papers: {str(e)}")


@router.post("/research/harvest")
def harvest_research_papers(payload: HarvestRequest):
    """Harvest real academic research papers on-demand for a project using arXiv, Crossref, and Semantic Scholar."""
    try:
        from backend.workline.pipeline.scholarly_research import search_scholarly_research
        from backend.agents.research_agent import run_research
        from backend.armoriq.delegation import capture_plan, delegate, invoke_tool

        project_id = payload.project_id or "PROJ-DEFAULT"
        query = (
            payload.keywords
            or payload.system_specification
            or payload.project_name
            or project_id.replace("PROJ-", "")
        ).strip() or "Hardware Engineering Architecture"

        root_receipt = capture_plan(query)
        research_receipt = delegate(
            agent_name="Research Agent",
            requested_scope=["search_scholarly_papers", "search_papers", "summarize_papers"],
            parent_receipt=root_receipt.model_dump(),
        )

        papers = invoke_tool(
            agent_name="Research Agent",
            tool_name="search_scholarly_papers",
            args={
                "idea": query,
                "requirements": [f"Hardware design and implementation of {query}"],
                "domain": "Hardware Engineering",
                "project_id": project_id,
                "max_papers": 6,
            },
            receipt_dict=research_receipt.model_dump(),
        )

        if not papers:
            papers = search_scholarly_research(
                idea=query,
                requirements=[],
                domain="Hardware Engineering",
                project_id=project_id,
                max_papers=6,
            )

        # Detect contradictions
        contradictions = []
        try:
            contradiction_receipt = delegate(
                agent_name="ContradictionAgent",
                requested_scope=["detect_contradictions"],
                parent_receipt=root_receipt.model_dump(),
            )
            con_res = invoke_tool(
                agent_name="ContradictionAgent",
                tool_name="detect_contradictions",
                args={"papers": papers},
                receipt_dict=contradiction_receipt.model_dump(),
            )
            contradictions = con_res if isinstance(con_res, list) else con_res.get("contradictions", [])
        except Exception:
            pass

        summaries = []
        for p in papers[:3]:
            abstract = p.get("abstract") or p.get("summary") or ""
            summaries.append(f"### {p.get('title')} ({p.get('publication_year', 2024)})\n* **Authors**: {p.get('authors')}\n* **DOI**: {p.get('doi', 'N/A')}\n* **Summary**: {abstract[:300]}")
        summary_text = "\n\n".join(summaries) if summaries else f"Synthesized research for {query}."

        return {
            "status": "SUCCESS",
            "project_id": project_id,
            "papers": papers,
            "research_papers": papers,
            "summary": summary_text,
            "contradictions": contradictions,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to harvest research papers: {str(e)}")

@router.post("/chat")
def chat_advisor(payload: ChatRequest):
    try:
        msg_lower = payload.message.lower()
        
        # High-fidelity thematic replies based on project details
        if "battery" in msg_lower or "power" in msg_lower or "energy" in msg_lower:
            reply = f"For the '{payload.intent}', power stability is paramount. We recommend integrating a 12.8V LiFePO4 battery pack connected to a dedicated charge controller as suggested: '{payload.recommendation}'. This cushions voltage drops and avoids motor stalling."
        elif "sensor" in msg_lower or "control" in msg_lower:
            reply = f"If using microcontroller nodes (like ESP32/Arduino) for control, ensure they are isolated from inductive motor draws using optocouplers or dedicated buck converters to filter high frequency switching noise."
        elif "cost" in msg_lower or "price" in msg_lower or "alternative" in msg_lower:
            reply = "To optimize your budget, you can select standard silicon diodes for back-EMF protection rather than premium components, and utilize integrated PCB distribution boards to reduce manual terminal wiring costs."
        elif "fuse" in msg_lower or "safety" in msg_lower:
            reply = f"Fusing individual power rails is critical. I suggest using modular 10A-15A blade fuses on your main line: '{payload.recommendation}'. This prevents cascade failures if a single brushless motor or servo experiences a rotor lock."
        else:
            reply = f"Analyzing '{payload.intent}': Regarding the architecture recommendation: '{payload.recommendation}', ensure that all modular connections are securely locked and you have integrated transient voltage suppressors (TVS diodes) on the primary power bus."
            
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot query failed: {str(e)}")

import os
import json

@router.get("/receipts")
def list_receipts():
    try:
        from backend.armoriq.receipts import RECEIPTS_DIR
        receipts = []
        if os.path.exists(RECEIPTS_DIR):
            for filename in os.listdir(RECEIPTS_DIR):
                if filename.endswith(".json"):
                    filepath = os.path.join(RECEIPTS_DIR, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        try:
                            receipts.append(json.load(f))
                        except Exception:
                            pass
        # Sort receipts by timestamp descending
        receipts.sort(key=lambda r: float(r.get("timestamp", 0.0)), reverse=True)
        return receipts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ViolationRequest(BaseModel):
    agent: str
    tool: str

@router.post("/violations/simulate")
def simulate_violation(payload: ViolationRequest):
    try:
        from backend.armoriq.receipts import generate_receipt
        from backend.armoriq.delegation import invoke_tool
        from backend.armoriq.policies import ScopeViolationError
        
        # 1. Create a dummy receipt with agent's standard scope
        from backend.armoriq.scope_map import AGENT_SCOPES
        agent_scope = AGENT_SCOPES.get(payload.agent, [])
        
        dummy_receipt = generate_receipt(
            agent=payload.agent,
            scope=agent_scope,
            parent_receipt_id="dummy-parent-id"
        )
        
        # 2. Invoke tool
        invoke_tool(
            agent_name=payload.agent,
            tool_name=payload.tool,
            args={"data": {}},
            receipt_dict=dummy_receipt.model_dump()
        )
        
        return {"status": "SUCCESS", "message": "Invoked successfully (unexpected!)"}
    except ScopeViolationError as sve:
        # Find the latest blocked receipt hash
        from backend.armoriq.receipts import RECEIPTS_DIR
        blocked_hash = "N/A"
        latest_time = 0.0
        if os.path.exists(RECEIPTS_DIR):
            for filename in os.listdir(RECEIPTS_DIR):
                if filename.endswith(".json"):
                    filepath = os.path.join(RECEIPTS_DIR, filename)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            r_data = json.load(f)
                            if r_data.get("status") == "blocked" and r_data.get("agent") == payload.agent:
                                r_time = float(r_data.get("timestamp", 0.0))
                                if r_time > latest_time:
                                    latest_time = r_time
                                    blocked_hash = r_data.get("hash", "N/A")
                    except Exception:
                        pass
                        
        return {
            "status": "BLOCKED",
            "violated_scope": payload.tool,
            "requesting_agent": payload.agent,
            "expected_authority": agent_scope,
            "rejection_reason": f"Tool '{payload.tool}' is not in the delegated scope for '{payload.agent}'. Allowed scope: {agent_scope}.",
            "blocked_receipt_hash": blocked_hash
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipeline/runs/{run_id}")
def get_pipeline_run_details(run_id: str):
    from backend.database import get_pipeline_run, get_pipeline_stages_for_run
    run = get_pipeline_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    stages = get_pipeline_stages_for_run(run_id)
    return {
        "run": run,
        "stages": stages
    }


@router.get("/pipeline/project/{project_id}")
def get_pipeline_runs_by_project(project_id: str):
    from backend.database import get_pipeline_runs_for_project
    runs = get_pipeline_runs_for_project(project_id)
    return {
        "project_id": project_id,
        "runs": runs
    }


