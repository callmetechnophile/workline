from typing import Dict, Any, List
from backend.armoriq.delegation import capture_plan, delegate, invoke_tool, AUDIT_LOGS
from backend.armoriq.policies import ScopeViolationError

# Sub-Agent Imports
from backend.agents.retrieval_agent import run_retrieval
from backend.agents.extraction_agent import run_extraction
from backend.agents.research_agent import run_research
from backend.agents.validation_agent import run_validation
from backend.agents.optimization_agent import run_optimization
from backend.agents.planning_agent import run_planning
from backend.agents.export_agent import run_export
from backend.agents.knowledge_graph_agent import run_knowledge_graph_agent
from backend.services.collaboration_service import create_team, get_team_members, get_project_comments, fetch_activity_logs

from datetime import datetime


def run_engineering_pipeline(
    user_intent: str,
    target_days: int = 30,
    project_name: str = None,
    engineering_template: str = None,
    team_id: str = None,
    project_id: str = None,
) -> Dict[str, Any]:
    # Clear previous audit logs for a fresh research run
    AUDIT_LOGS.clear()
    
    # 1. Capture Root Plan
    root_receipt = capture_plan(user_intent)
    root_receipt_dict = root_receipt.model_dump()
    
    # 1b. Run Knowledge Graph Agent to query engineering relationships
    graph_receipt = delegate(
        agent_name="KnowledgeGraphAgent",
        requested_scope=["graph.read"],
        parent_receipt=root_receipt_dict
    )
    graph_context = run_knowledge_graph_agent(user_intent, graph_receipt.model_dump())
    
    # 2. RUN MANDATORY ARMORIQ BLOCKING TEST
    # Delegate Research Agent with ONLY paper search scopes
    research_receipt = delegate(
        agent_name="Research Agent",
        requested_scope=["search_papers", "summarize_papers"],
        parent_receipt=root_receipt_dict
    )
    
    blocked_test_triggered = False
    try:
        # Trigger illegal tool execution to demonstrate ArmorIQ block capability
        invoke_tool(
            agent_name="Research Agent",
            tool_name="export_pdf",  # Out of scope!
            args={"data": {}},
            receipt_dict=research_receipt.model_dump()
        )
    except ScopeViolationError:
        blocked_test_triggered = True
        # Caught successfully! The block log is saved inside AUDIT_LOGS.
        
    # 3. Proceed with Retrieval Agent
    retrieval_receipt = delegate(
        agent_name="Retrieval Agent",
        requested_scope=["search_projects", "fetch_sources"],
        parent_receipt=root_receipt_dict
    )
    retrieval_res = run_retrieval(user_intent, retrieval_receipt.model_dump())
    
    # 4. Proceed with Extraction Agent
    extraction_receipt = delegate(
        agent_name="Extraction Agent",
        requested_scope=["extract_components"],
        parent_receipt=root_receipt_dict
    )
    # Feed retrieval details to extract components
    retrieved_text = retrieval_res.get("source_details", {}).get("content_markdown", "") if retrieval_res.get("source_details") else user_intent
    extraction_res = run_extraction(retrieved_text, extraction_receipt.model_dump())
    components = extraction_res.get("components", [])
    
    # 4b. BOM Optimization Engine (runs ProcurementAgent)
    procurement_receipt = delegate(
        agent_name="ProcurementAgent",
        requested_scope=["generate_optimized_bom", "calculate_landed_cost", "find_alternative_components"],
        parent_receipt=root_receipt_dict
    )
    procurement_res = invoke_tool(
        agent_name="ProcurementAgent",
        tool_name="generate_optimized_bom",
        args={"components": components, "mode": "normal"},
        receipt_dict=procurement_receipt.model_dump()
    )
    
    # Overwrite components with the optimized, platform-ranked BOM items
    components = procurement_res["bom_items"]
    cost_res = procurement_res["totals"]
    
    # Extract alternatives list for the tabbed drawer display
    alternatives_list = []
    for item in components:
        alternatives_list.append({
            "component": item["component"],
            "alternatives": [
                {
                    "alternative": a["alternative"],
                    "name": a["alternative"],
                    "type": "cheaper" if a["final_cost"] < item["final_cost"] else "upgraded",
                    "reason": a["reason"],
                    "approx_cost_usd": float(a["final_cost"] / 83.0),
                    "base_cost": a.get("base_cost", a["final_cost"]),
                    "shipping_cost": a.get("shipping_cost", 0),
                    "final_cost": a["final_cost"]
                } for a in item.get("alternatives", [])
            ]
        })

    # 4d. Voltage Checker
    voltage_receipt = delegate(
        agent_name="Voltage Checker",
        requested_scope=["check_voltage_compatibility"],
        parent_receipt=root_receipt_dict
    )
    # Voltage Checker requires component names mapping
    voltage_components = [{"name": c["component"], "category": c["category"]} for c in components]
    voltage_res = invoke_tool(
        agent_name="Voltage Checker",
        tool_name="check_voltage_compatibility",
        args={"components": voltage_components},
        receipt_dict=voltage_receipt.model_dump()
    )

    # 4e. Pin Generator
    pin_receipt = delegate(
        agent_name="Pin Generator",
        requested_scope=["generate_pin_map"],
        parent_receipt=root_receipt_dict
    )
    pin_res = invoke_tool(
        agent_name="Pin Generator",
        tool_name="generate_pin_map",
        args={"components": voltage_components},
        receipt_dict=pin_receipt.model_dump()
    )

    # 4f. [NEW] Datasheet Intelligence
    datasheet_receipt = delegate(
        agent_name="Extraction Agent",
        requested_scope=["fetch_datasheets"],
        parent_receipt=root_receipt_dict
    )
    datasheets_res = invoke_tool(
        agent_name="Extraction Agent",
        tool_name="fetch_datasheets",
        args={"components": components},
        receipt_dict=datasheet_receipt.model_dump()
    )

    # 4g. [NEW] Power Budget Calculator
    power_receipt = delegate(
        agent_name="Voltage Checker",
        requested_scope=["calculate_power_budget"],
        parent_receipt=root_receipt_dict
    )
    power_res = invoke_tool(
        agent_name="Voltage Checker",
        tool_name="calculate_power_budget",
        args={"components": components},
        receipt_dict=power_receipt.model_dump()
    )

    # 4h. [NEW] Dependency Graph Generator
    dependency_receipt = delegate(
        agent_name="Planner Agent",
        requested_scope=["generate_dependency_graph"],
        parent_receipt=root_receipt_dict
    )
    dependency_res = invoke_tool(
        agent_name="Planner Agent",
        tool_name="generate_dependency_graph",
        args={"components": components},
        receipt_dict=dependency_receipt.model_dump()
    )

    # 4i. [NEW] Wiring Diagram Generator
    wiring_receipt = delegate(
        agent_name="Pin Generator",
        requested_scope=["generate_wiring_diagram"],
        parent_receipt=root_receipt_dict
    )
    wiring_res = invoke_tool(
        agent_name="Pin Generator",
        tool_name="generate_wiring_diagram",
        args={"components": components},
        receipt_dict=wiring_receipt.model_dump()
    )
    
    # 5. Run Research Agent (Allowed Scope)
    research_res = run_research(user_intent, research_receipt.model_dump())

    # 5b. [NEW] Research Paper Ranking Engine
    ranking_receipt = delegate(
        agent_name="Research Agent",
        requested_scope=["rank_papers"],
        parent_receipt=root_receipt_dict
    )
    ranked_papers = invoke_tool(
        agent_name="Research Agent",
        tool_name="rank_papers",
        args={"papers": research_res.get("papers", []), "query": user_intent},
        receipt_dict=ranking_receipt.model_dump()
    )

    # 5c. [NEW] Research Contradiction Detector
    contradiction_receipt = delegate(
        agent_name="ContradictionAgent",
        requested_scope=["detect_contradictions"],
        parent_receipt=root_receipt_dict
    )
    contradiction_res = invoke_tool(
        agent_name="ContradictionAgent",
        tool_name="detect_contradictions",
        args={"papers": ranked_papers},
        receipt_dict=contradiction_receipt.model_dump()
    )

    # Only top 3 papers should be deeply analyzed
    top_3_papers = ranked_papers[:3]
    summaries = []
    for paper in top_3_papers:
        paper_sum = invoke_tool(
            agent_name="Research Agent",
            tool_name="summarize_papers",
            args={"paper_id": paper["id"]},
            receipt_dict=research_receipt.model_dump()
        )
        if paper_sum:
            summaries.append(
                f"### {paper['title']} ({paper.get('publish_year', paper.get('year', 2020))})\n"
                f"* **Score**: {paper['score']}/100\n"
                f"* **Summary**: {paper_sum.get('summary', '')}\n"
                f"* **Key Finding**: {paper_sum.get('key_finding', '')}"
            )
            
    consolidated_summary = {
        "summary": "\n\n".join(summaries) if summaries else "No papers selected for deep summary.",
        "key_finding": "Consolidated literature shows reliable, peer-reviewed engineering paths."
    }
    
    # 6. Proceed with Validation Agent (Electrical Service embedded)
    validation_receipt = delegate(
        agent_name="Validation Agent",
        requested_scope=["validate_architecture"],
        parent_receipt=root_receipt_dict
    )
    validation_res = run_validation(components, user_intent, validation_receipt.model_dump())

    # 6b. [NEW] Thermal Risk Analyzer
    thermal_receipt = delegate(
        agent_name="ThermalAgent",
        requested_scope=["analyze_thermal_risk"],
        parent_receipt=root_receipt_dict
    )
    thermal_res = invoke_tool(
        agent_name="ThermalAgent",
        tool_name="analyze_thermal_risk",
        args={"components": components, "enclosure_temp": 25.0},
        receipt_dict=thermal_receipt.model_dump()
    )
    
    # 7. Proceed with Optimization Agent
    optimization_receipt = delegate(
        agent_name="Optimization Agent",
        requested_scope=["optimize_components"],
        parent_receipt=root_receipt_dict
    )
    optimization_res = run_optimization(components, optimization_receipt.model_dump())
    
    # 8. Proceed with Planning Agent
    planning_receipt = delegate(
        agent_name="Planning Agent",
        requested_scope=["generate_roadmap", "generate_gantt"],
        parent_receipt=root_receipt_dict
    )
    planning_res = run_planning(validation_res, planning_receipt.model_dump(), target_days=target_days)
    
    # 8b. Procurement BOM Exports (Allowed Scope)
    bom_receipt = delegate(
        agent_name="BOM Export Engine",
        requested_scope=["export_bom"],
        parent_receipt=root_receipt_dict
    )
    bom_export_res = invoke_tool(
        agent_name="BOM Export Engine",
        tool_name="export_bom",
        args={"components": components, "cost_summary": cost_res},
        receipt_dict=bom_receipt.model_dump()
    )

    # Compile intermediate package state to pass to Export Agent
    package_data = {
        "intent": user_intent,
        "components": components,
        "validation": validation_res,
        "optimization": optimization_res,
        "roadmap": planning_res.get("roadmap", []),
        "gantt": planning_res.get("gantt", []),
        "cost_summary": cost_res,
        "alternatives": alternatives_list,
        "voltage_risks": voltage_res,
        "pin_mapping": pin_res,
        "bom_exports": bom_export_res,
        "datasheets": datasheets_res,
        "power_analysis": power_res,
        "dependency_graph": dependency_res,
        "wiring_diagram": wiring_res,
        "papers": ranked_papers,
        "paper_summary": consolidated_summary,
        "contradictions": contradiction_res,
        "thermal_analysis": thermal_res,
        "audit_trail": list(AUDIT_LOGS)
    }

    # 8c. [NEW] Versioning Engine
    from backend.mcp.tools.export_tools import generate_project_title
    clean_p_name = (project_name or "").strip() or generate_project_title(user_intent)
    actual_project_id = project_id or f"PROJ-{clean_p_name[:8].replace(' ', '_').upper()}"
    
    version_receipt = delegate(
        agent_name="VersionAgent",
        requested_scope=["save_version"],
        parent_receipt=root_receipt_dict
    )
    version_res = invoke_tool(
        agent_name="VersionAgent",
        tool_name="save_version",
        args={
            "project_id": actual_project_id,
            "version_num": 1,
            "data": package_data,
            "modified_by": "engineer_1",
            "change_summary": f"Generated engineering blueprint for {clean_p_name}"
        },
        receipt_dict=version_receipt.model_dump()
    )

    # 8d. [NEW] Team Workspace Integration
    collab_receipt = delegate(
        agent_name="CollaborationAgent",
        requested_scope=["invite_member", "comment"],
        parent_receipt=root_receipt_dict
    )
    # Ensure a default team exists
    active_team_name = team_id or f"Team {clean_p_name}"
    team_res = create_team(active_team_name)
    invite_member_res = invoke_tool(
        agent_name="CollaborationAgent",
        tool_name="invite_member",
        args={
            "team_id": team_res["id"],
            "user_id": "engineer_1",
            "email": "engineer1@armourline.io",
            "role": "Engineer"
        },
        receipt_dict=collab_receipt.model_dump()
    )
    
    # Try adding a default comment for demonstration
    try:
        invoke_tool(
            agent_name="CollaborationAgent",
            tool_name="comment",
            args={
                "project_id": actual_project_id,
                "section": "Wiring",
                "author": "engineer_1",
                "content": "Verify PCA9685 I2C logic level conversion before physical assembly."
            },
            receipt_dict=collab_receipt.model_dump()
        )
    except Exception:
        pass

    team_members = get_team_members(team_res["id"])
    comments = get_project_comments(actual_project_id)
    activities = fetch_activity_logs(team_res["id"])
    
    # Fetch all project versions
    from backend.services.versioning_service import get_project_versions
    all_versions = get_project_versions(actual_project_id)
    
    # 9. Invoke Export Agent to build PDF bundle
    export_receipt = delegate(
        agent_name="Export Agent",
        requested_scope=["export_pdf", "export_csv", "export_markdown", "export_docx"],
        parent_receipt=root_receipt_dict
    )
    export_res = run_export(package_data, export_receipt.model_dump())
    
    # 10. Generate Decision Trace Table data
    decision_trace = generate_decision_trace(user_intent)
    
    # Automatically Ingest generated project graph into Qdrant / Knowledge Graph
    try:
        from backend.graph.graph_service import GraphService
        GraphService().ingest_project("engineer@armourline.io", active_team_name, actual_project_id, package_data, list(AUDIT_LOGS))
    except Exception as e:
        import logging
        logging.getLogger("PlannerAgent").warning(f"Failed to ingest complete EKG project graph to Knowledge Graph: {e}")
    
    now_iso = datetime.utcnow().isoformat()

    # 11. Compile final output payload
    return {
        "project_id": actual_project_id,
        "project_name": clean_p_name,
        "system_specification": user_intent,
        "intent": user_intent,
        "target_timeline_days": target_days,
        "engineering_template": engineering_template or "",
        "team_id": active_team_name,
        "owner_id": "owner@workline.io",
        "status": "active",
        "created_at": now_iso,
        "updated_at": now_iso,
        "components": components,
        "projects": retrieval_res.get("projects", []),
        "papers": ranked_papers,
        "paper_summary": consolidated_summary,
        "validation": validation_res,
        "optimization": optimization_res,
        "roadmap": planning_res.get("roadmap", []),
        "gantt": planning_res.get("gantt", []),
        "exports": export_res,
        "decision_trace": decision_trace,
        "audit_trail": list(AUDIT_LOGS), # copy current logs
        "blocked_test_success": blocked_test_triggered,
        
        # Payloads
        "cost_summary": cost_res,
        "alternatives": alternatives_list,
        "voltage_risks": voltage_res,
        "pin_mapping": pin_res,
        "bom_exports": bom_export_res,
        
        # Tier 2 execution layer features
        "datasheets": datasheets_res,
        "power_analysis": power_res,
        "dependency_graph": dependency_res,
        "wiring_diagram": wiring_res,
        
        # Tier 3 execution layer features
        "contradictions": contradiction_res,
        "thermal_analysis": thermal_res,
        "team_workspace": {
            "team_id": team_res["id"],
            "team_name": team_res["name"],
            "members": team_members,
            "comments": comments,
            "activities": activities
        },
        "version_history": {
            "project_id": actual_project_id,
            "versions": all_versions
        }
    }

def generate_decision_trace(intent: str) -> List[Dict[str, str]]:
    intent_lower = intent.lower()
    if "solar" in intent_lower or "vacuum" in intent_lower:
        return [
            {
                "decision": "Integrate 12.8V LiFePO4 battery pack buffer instead of direct panel wiring.",
                "rationale": "Prevents motor stalling, electronics burn-in, and voltage drops under cloud coverage.",
                "agent": "Research Agent"
            },
            {
                "decision": "Substitute flexible solar panel with rigid glass solar panel.",
                "rationale": "Reduces costs by 30% if structural configuration allows for rigid base mounts.",
                "agent": "Optimization Agent"
            },
            {
                "decision": "Deploy a Maximum Power Point Tracking (MPPT) controller.",
                "rationale": "Boosts energy capture efficiency by 34% compared to PWM controllers.",
                "agent": "Validation Agent"
            }
        ]
    elif "drone" in intent_lower or "delivery" in intent_lower:
        return [
            {
                "decision": "Use ArduPilot / Matek H743-WING as flight controller alternative to Pixhawk.",
                "rationale": "Saves $90.00 while maintaining identical autonomous telemetry flight paths.",
                "agent": "Optimization Agent"
            },
            {
                "decision": "Separate telemetry antennas and GPS modules from high current lines by 15cm.",
                "rationale": "Mitigates severe RF interference and signal degradation from motor draws.",
                "agent": "Validation Agent"
            },
            {
                "decision": "Implement dual-GPS backup compass module setup.",
                "rationale": "Ensures navigational fail-safes during complex autonomous package dropoffs.",
                "agent": "Research Agent"
            }
        ]
    else:
        return [
            {
                "decision": "Use low-power ESP32 controller with built-in Wi-Fi.",
                "rationale": "Reduces power and PCB space compared to multi-chip alternatives.",
                "agent": "Research Agent"
            },
            {
                "decision": "Implement linear voltage regulator for clean sensor readings.",
                "rationale": "Filters high frequency switching noise from standard wall adapters.",
                "agent": "Validation Agent"
            }
        ]
