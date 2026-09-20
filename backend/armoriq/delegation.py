from typing import List, Dict, Any, Optional
from backend.armoriq.receipts import generate_receipt, verify_receipt, CryptographicReceipt, save_tool_receipt
from backend.armoriq.scope_map import AGENT_SCOPES
from backend.armoriq.policies import ScopeViolationError, validate_tool_invocation

# MCP Tool Imports
from backend.mcp.tools.project_tools import search_projects, fetch_sources
from backend.mcp.tools.extraction_tools import extract_components
from backend.mcp.tools.paper_tools import search_papers, summarize_papers
from backend.mcp.tools.validation_tools import validate_architecture
from backend.mcp.tools.optimization_tools import optimize_components
from backend.mcp.tools.roadmap_tools import generate_roadmap, generate_gantt
from backend.mcp.tools.export_tools import export_pdf, export_csv, export_markdown, export_docx

# Production Grade Services
from backend.services.cost_service import calculate_total_cost
from backend.services.alternative_service import find_alternatives
from backend.services.electrical_service import check_voltage_compatibility
from backend.services.pin_service import generate_pin_map
from backend.services.bom_service import export_bom, generate_optimized_bom, calculate_landed_cost, find_alternative_components

# Tier 2 Production Grade Services
from backend.services.power_service import calculate_power_budget
from backend.services.dependency_service import generate_dependency_graph
from backend.services.wiring_service import generate_wiring_diagram

# Tier 3 Production Grade Services
from backend.services.collaboration_service import invite_member, assign_role, add_comment
from backend.services.versioning_service import save_version, rollback_version, fork_project
from backend.services.thermal_service import analyze_thermal_risk
from backend.services.contradiction_service import detect_contradictions
from backend.services.paper_ranking_service import rank_papers
from backend.services.datasheet_service import fetch_datasheet_links
from backend.services.connection_chatbot_service import ask_connection_assistant
from backend.database.graph.graph_service import GraphService

# Global in-memory audit log list for quick tracking
AUDIT_LOGS: List[Dict[str, Any]] = []

def log_audit_trail(agent: str, action: str, allowed_scope: List[str], tool_invoked: Optional[str] = None, status: str = "SUCCESS", details: str = "", receipt_id: Optional[str] = None, parent_receipt_id: Optional[str] = None):
    log_entry = {
        "agent": agent,
        "action": action, # "DELEGATION" or "TOOL_EXECUTION" or "PLAN_CAPTURE"
        "allowed_scope": allowed_scope,
        "tool_invoked": tool_invoked,
        "status": status,
        "details": details,
        "receipt_id": receipt_id,
        "parent_receipt_id": parent_receipt_id
    }
    AUDIT_LOGS.append(log_entry)

    # AWS Observability & Event Integration (CloudWatch & EventBridge)
    try:
        import asyncio
        from backend.workline.observability.cloudwatch import cloudwatch_metrics
        from backend.workline.events.eventbridge import event_publisher

        is_violation = (status == "FAILED" or "exceeds max boundaries" in details or "ScopeViolationError" in details)
        d_type = "PolicyViolation" if is_violation else ("AgentDelegated" if action == "DELEGATION" else "ToolExecuted")
        d_payload = {"agent": agent, "details": details, "tool": tool_invoked, "receipt_id": receipt_id}

        try:
            loop = asyncio.get_running_loop()
            if is_violation:
                loop.create_task(cloudwatch_metrics.record_policy_violation(agent, tool_invoked or "general"))
                loop.create_task(event_publisher.publish_event(detail_type=d_type, detail=d_payload, source="workline.armoriq"))
            else:
                loop.create_task(event_publisher.publish_event(detail_type=d_type, detail=d_payload, source="workline.armoriq"))
        except RuntimeError:
            # Outside active event loop: record directly in event buffer
            event_publisher._published_events.append({
                "detail_type": d_type,
                "detail": d_payload,
                "source": "workline.armoriq",
                "timestamp": 0.0,
            })
    except Exception:
        pass

    return log_entry

def capture_plan(user_intent: str) -> CryptographicReceipt:
    # Captures root plan with Planner Agent
    planner_scope = AGENT_SCOPES["Planner Agent"]
    receipt = generate_receipt(
        agent="Planner Agent",
        scope=planner_scope,
        parent_receipt_id=None,
        input_data={"user_intent": user_intent}
    )
    log_audit_trail(
        agent="Planner Agent",
        action="PLAN_CAPTURE",
        allowed_scope=planner_scope,
        status="SUCCESS",
        details=f"Captured plan for intent: '{user_intent}'",
        receipt_id=receipt.receipt_id
    )
    return receipt

def delegate(agent_name: str, requested_scope: List[str], parent_receipt: Dict[str, Any]) -> CryptographicReceipt:
    import os
    if os.environ.get("DISABLE_ARMORIQ") == "true":
        return generate_receipt(
            agent=agent_name,
            scope=requested_scope,
            parent_receipt_id=parent_receipt.get("receipt_id") if parent_receipt else None
        )
        
    # 1. Verify parent receipt
    if not verify_receipt(parent_receipt):
        log_audit_trail(
            agent=agent_name,
            action="DELEGATION",
            allowed_scope=requested_scope,
            status="FAILED",
            details="Parent receipt validation failed.",
            parent_receipt_id=parent_receipt.get("receipt_id")
        )
        raise ValueError("Invalid parent receipt signature")
        
    # 2. Check if agent_name is valid
    if agent_name not in AGENT_SCOPES:
        log_audit_trail(
            agent=agent_name,
            action="DELEGATION",
            allowed_scope=requested_scope,
            status="FAILED",
            details=f"Agent '{agent_name}' is not registered in security scope map.",
            parent_receipt_id=parent_receipt.get("receipt_id")
        )
        raise ValueError(f"Unknown agent: {agent_name}")
        
    # 3. Check requested scope is subset of agent's max boundary
    max_scope = AGENT_SCOPES[agent_name]
    for tool in requested_scope:
        if tool not in max_scope:
            log_audit_trail(
                agent=agent_name,
                action="DELEGATION",
                allowed_scope=requested_scope,
                status="FAILED",
                details=f"Delegation failed: Requested tool '{tool}' exceeds max boundaries.",
                parent_receipt_id=parent_receipt.get("receipt_id")
            )
            raise ScopeViolationError(
                agent=agent_name,
                tool=tool,
                allowed_scope=max_scope,
                details="Delegation requested tool exceeding maximum boundary."
            )
            
    # 4. Generate sub-receipt
    child_receipt = generate_receipt(
        agent=agent_name,
        scope=requested_scope,
        parent_receipt_id=parent_receipt.get("receipt_id"),
        input_data=requested_scope
    )
    
    log_audit_trail(
        agent=agent_name,
        action="DELEGATION",
        allowed_scope=requested_scope,
        status="SUCCESS",
        details=f"Delegated from {parent_receipt.get('agent')} to {agent_name}",
        receipt_id=child_receipt.receipt_id,
        parent_receipt_id=parent_receipt.get("receipt_id")
    )
    
    return child_receipt

def invoke_tool(agent_name: str, tool_name: str, args: Dict[str, Any], receipt_dict: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Validate scope and cryptographic receipt using policies
        validate_tool_invocation(agent_name, tool_name, receipt_dict)
        
        # Dispatch to the actual tool
        result = {}
        if tool_name == "search_projects":
            result = search_projects(args.get("query", ""))
        elif tool_name == "fetch_sources":
            result = fetch_sources(args.get("url", ""))
        elif tool_name == "extract_components":
            result = extract_components(args.get("raw_text", ""))
        elif tool_name == "calculate_total_cost":
            result = calculate_total_cost(args.get("components", []))
        elif tool_name == "find_alternatives":
            result = find_alternatives(args.get("component_name", ""))
        elif tool_name == "check_voltage_compatibility":
            result = check_voltage_compatibility(args.get("components", []))
        elif tool_name == "generate_pin_map":
            result = generate_pin_map(args.get("components", []))
        elif tool_name == "export_bom":
            result = export_bom(args.get("components", []), args.get("cost_summary", {}))
        elif tool_name == "calculate_power_budget":
            result = calculate_power_budget(args.get("components", []))
        elif tool_name == "generate_dependency_graph":
            result = generate_dependency_graph(args.get("components", []))
        elif tool_name == "generate_wiring_diagram":
            result = generate_wiring_diagram(args.get("components", []))
        elif tool_name == "rank_papers":
            result = rank_papers(args.get("papers", []), args.get("query", ""))
        elif tool_name == "fetch_datasheets":
            result = [fetch_datasheet_links(c.get("component") or c.get("name", "")) for c in args.get("components", [])]
        elif tool_name == "ask_connection_assistant":
            result = ask_connection_assistant(args.get("message", ""), args.get("context", {}))
        elif tool_name == "generate_optimized_bom":
            result = generate_optimized_bom(args.get("components", []), args.get("mode", "normal"))
        elif tool_name == "calculate_landed_cost":
            result = calculate_landed_cost(args.get("component", {}), args.get("mode", "normal"))
        elif tool_name == "find_alternative_components":
            result = find_alternative_components(args.get("component_name", ""))
        elif tool_name == "search_papers":
            result = search_papers(args.get("query", ""))
        elif tool_name == "summarize_papers":
            result = summarize_papers(args.get("paper_id", ""))
        elif tool_name == "validate_architecture":
            result = validate_architecture(args.get("components", []), args.get("concept", ""))
        elif tool_name == "optimize_components":
            result = optimize_components(args.get("components", []))
        elif tool_name == "generate_roadmap":
            result = generate_roadmap(args.get("validation_results", {}), args.get("target_days", 22))
        elif tool_name == "generate_gantt":
            result = generate_gantt(args.get("roadmap", []))
        elif tool_name == "export_pdf":
            result = export_pdf(args.get("data", {}))
        elif tool_name == "export_csv":
            result = export_csv(args.get("data", {}))
        elif tool_name == "export_markdown":
            result = export_markdown(args.get("data", {}))
        elif tool_name == "export_docx":
            result = export_docx(args.get("data", {}))
        elif tool_name == "invite_member":
            result = invite_member(args.get("team_id"), args.get("user_id"), args.get("email"), args.get("role"))
        elif tool_name == "assign_role":
            result = assign_role(args.get("member_id"), args.get("role"))
        elif tool_name == "comment":
            result = add_comment(args.get("project_id"), args.get("section"), args.get("author"), args.get("content"))
        elif tool_name == "save_version":
            result = save_version(args.get("project_id"), args.get("version_num"), args.get("data"), args.get("modified_by"), args.get("change_summary"))
        elif tool_name == "rollback_version":
            result = rollback_version(args.get("project_id"), args.get("version_num"))
        elif tool_name == "fork_project":
            result = fork_project(args.get("project_id"), args.get("version_num"), args.get("new_name"), args.get("user_id"))
        elif tool_name == "analyze_thermal_risk":
            result = analyze_thermal_risk(args.get("components", []), args.get("enclosure_temp", 25.0))
        elif tool_name == "detect_contradictions":
            result = detect_contradictions(args.get("papers", []))
        elif tool_name == "graph.read":
            result = GraphService().run_read_query(args.get("query_name"), args.get("params", {}))
        elif tool_name in ("graph.insert", "graph.update"):
            result = GraphService().run_write_query(args.get("query_name"), args.get("params", {}))
        elif tool_name == "analyze_engineering_idea":
            from backend.workline.pipeline.idea_understanding import analyze_engineering_idea
            result = analyze_engineering_idea(args.get("idea", ""), args.get("project_id", "default_project"))
        elif tool_name in ("research_components", "recommend_components"):
            import asyncio
            import concurrent.futures
            from backend.workline.pipeline.component_research import research_components_for_project
            def _run_comp_research():
                return asyncio.run(research_components_for_project(
                    idea_understanding=args.get("idea_understanding", {}),
                    requirements=args.get("requirements", []),
                    constraints=args.get("constraints", []),
                    project_id=args.get("project_id", "default_project"),
                ))
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                rec, alt, evid, viol = pool.submit(_run_comp_research).result()
            result = {
                "recommended_components": rec,
                "alternatives": alt,
                "evidence": evid,
                "violations": viol,
            }
        elif tool_name == "search_scholarly_papers":
            from backend.workline.pipeline.scholarly_research import search_scholarly_research
            result = search_scholarly_research(
                idea=args.get("idea", ""),
                requirements=args.get("requirements", []),
                domain=args.get("domain", ""),
                project_id=args.get("project_id", "default_project"),
                max_papers=args.get("max_papers", 6),
            )
        elif tool_name == "retrieve_datasheet":
            import asyncio
            import concurrent.futures
            from backend.mcp.nexar_client import nexar_mcp_client
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                result = pool.submit(lambda: asyncio.run(nexar_mcp_client.get_datasheet(args.get("mpn", "")))).result() or {}
        elif tool_name == "populate_knowledge_graph":
            import asyncio
            import concurrent.futures
            from backend.workline.pipeline.graph_populator import knowledge_graph_populator
            def _run_populator():
                return asyncio.run(knowledge_graph_populator.populate_pipeline_graph(
                    project_id=args.get("project_id", "default_project"),
                    project_name=args.get("project_name", "Engineering Project"),
                    system_specification=args.get("system_specification", ""),
                    requirements=args.get("requirements", []),
                    constraints=args.get("constraints", []),
                    components=args.get("components", []),
                    research_papers=args.get("research_papers", []),
                    violations=args.get("violations", []),
                ))
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                result = pool.submit(_run_populator).result()
        elif tool_name.startswith("nexar_mcp_"):
            import asyncio
            import concurrent.futures
            from backend.mcp.nexar_client import nexar_mcp_client
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    mcp_res = pool.submit(lambda: asyncio.run(nexar_mcp_client.execute_tool(tool_name, args))).result()
            except Exception:
                mcp_res = asyncio.run(nexar_mcp_client.execute_tool(tool_name, args))
            result = mcp_res.model_dump()
        else:
            raise ValueError(f"Unknown tool name: {tool_name}")
            
        # Log successful invocation
        log_audit_trail(
            agent=agent_name,
            action="TOOL_EXECUTION",
            allowed_scope=receipt_dict.get("scope", []),
            tool_invoked=tool_name,
            status="SUCCESS",
            details=f"Successfully executed tool '{tool_name}'",
            receipt_id=receipt_dict.get("receipt_id"),
            parent_receipt_id=receipt_dict.get("parent_receipt_id")
        )
        # Expose invocation receipt
        save_tool_receipt(
            agent=agent_name,
            parent=receipt_dict.get("receipt_id", ""),
            tool=tool_name,
            scope=receipt_dict.get("scope", []),
            status="SUCCESS",
            execution_result=result
        )
        return result
        
    except ScopeViolationError as sve:
        # Log blocked invocation in audit logs
        log_audit_trail(
            agent=agent_name,
            action="TOOL_EXECUTION",
            allowed_scope=receipt_dict.get("scope", []),
            tool_invoked=tool_name,
            status="BLOCKED",
            details=str(sve),
            receipt_id=receipt_dict.get("receipt_id"),
            parent_receipt_id=receipt_dict.get("parent_receipt_id")
        )
        # Expose invocation receipt for block logs
        save_tool_receipt(
            agent=agent_name,
            parent=receipt_dict.get("receipt_id", ""),
            tool=tool_name,
            scope=receipt_dict.get("scope", []),
            status="BLOCKED",
            execution_result=str(sve)
        )
        # Raise error again to be handled by backend
        raise sve
    except Exception as e:
        # Log failed invocation in audit logs
        log_audit_trail(
            agent=agent_name,
            action="TOOL_EXECUTION",
            allowed_scope=receipt_dict.get("scope", []),
            tool_invoked=tool_name,
            status="FAILED",
            details=f"Tool failed with unexpected error: {str(e)}",
            receipt_id=receipt_dict.get("receipt_id"),
            parent_receipt_id=receipt_dict.get("parent_receipt_id")
        )
        # Expose invocation receipt for failure logs
        save_tool_receipt(
            agent=agent_name,
            parent=receipt_dict.get("receipt_id", ""),
            tool=tool_name,
            scope=receipt_dict.get("scope", []),
            status="FAILED",
            execution_result=str(e)
        )
        raise e
