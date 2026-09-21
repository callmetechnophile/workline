import os
import json
import httpx
from typing import Dict, Any, List, Optional


def ask_connection_assistant(message: str, context: Dict[str, Any], user_id: Optional[str] = None) -> str:
    """
    Acts as an engineering connection and team collaboration advisor.
    Evaluates electrical connections, pin compatibility, and team collaboration state
    (tasks, decisions, approvals, activity) using Amazon Bedrock DeepSeek R1.
    """
    msg_lower = message.lower()
    effective_user = user_id or context.get("user_id") or "anonymous"
    team_id = context.get("team_id")
    project_id = context.get("project_id")

    # Team collaboration context collection with strict permission filtering
    team_context_str = ""
    team_members_list = []
    active_tasks_list = []
    pending_approvals_list = []
    decisions_list = []

    try:
        from backend.workline.collaboration.permissions import permission_service, ArtifactType, ActionType
        from backend.workline.collaboration.teams.service import team_service
        from backend.workline.collaboration.tasks.service import task_service
        from backend.workline.collaboration.approvals.service import approval_service, ApprovalStatus
        from backend.workline.decision.service import decision_service

        if not team_id and effective_user != "anonymous":
            user_teams = team_service.list_user_teams(effective_user)
            if user_teams:
                team_id = user_teams[0].id

        if team_id:
            team = team_service.get_team(team_id)
            if team:
                team_members_list = [f"{m.user_id} ({m.role.value})" for m in team.members]

            # Tasks with READ permission
            if permission_service.can_perform(effective_user, team_id, ArtifactType.TASK, ActionType.READ):
                tasks = task_service.list_tasks(team_id=team_id)
                for t in tasks:
                    assignee = t.assignee_id or "Unassigned"
                    art_ref = f" -> {t.related_artifact.artifact_type.value}:{t.related_artifact.artifact_name}" if t.related_artifact else ""
                    active_tasks_list.append(f"- [{t.status.value}] {t.title} (Assignee: {assignee}, Priority: {t.priority.value}{art_ref})")

            # Approvals with READ permission
            if permission_service.can_perform(effective_user, team_id, ArtifactType.TEAM_MANAGEMENT, ActionType.READ):
                reqs = approval_service.list_requests(team_id=team_id, status=ApprovalStatus.PENDING)
                for r in reqs:
                    pending_approvals_list.append(f"- [{r.request_type.value}] {r.title} (Requested by: {r.requester_id}, Approver: {r.required_role.value})")

            # Decisions with READ permission
            if permission_service.can_perform(effective_user, team_id, ArtifactType.DECISION, ActionType.READ):
                decs = decision_service.list_decisions(project_id=project_id)
                for d in decs:
                    choice = d.selected_candidate or "Pending"
                    decisions_list.append(f"- Decision '{d.title}': Selected candidate '{choice}'. Rationale: {d.rationale or d.description}")

        parts = []
        if team_members_list:
            parts.append(f"Team Members: {', '.join(team_members_list)}")
        if active_tasks_list:
            parts.append("Team Tasks:\n" + "\n".join(active_tasks_list[:10]))
        if pending_approvals_list:
            parts.append("Pending Approvals:\n" + "\n".join(pending_approvals_list[:5]))
        if decisions_list:
            parts.append("Engineering Decisions:\n" + "\n".join(decisions_list[:5]))

        if parts:
            team_context_str = "\n\nActive Team Collaboration Context:\n" + "\n".join(parts)
    except Exception:
        pass
    
    # 1. Check if user is asking for component selection / sourcing via Nexar MCP
    if any(k in msg_lower for k in ("find", "recommend", "regulator", "mcu", "resistor", "sensor", "converter", "ldo", "transistor", "component")):
        try:
            import asyncio
            from backend.mcp.nexar_client import nexar_mcp_client
            loop = None
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                pass

            candidates_data = []
            if loop and loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    mcp_res = pool.submit(asyncio.run, nexar_mcp_client.execute_tool(nexar_mcp_client.TOOL_SEARCH_COMPONENTS, {"query": message, "limit": 3})).result()
                    if mcp_res.success and mcp_res.data:
                        candidates_data = mcp_res.data
            else:
                mcp_res = asyncio.run(nexar_mcp_client.execute_tool(nexar_mcp_client.TOOL_SEARCH_COMPONENTS, {"query": message, "limit": 3}))
                if mcp_res.success and mcp_res.data:
                    candidates_data = mcp_res.data

            if candidates_data:
                comp_lines = []
                for idx, c in enumerate(candidates_data[:3], 1):
                    mpn = c.get("manufacturer_part_number") or c.get("mpn")
                    mfr = c.get("manufacturer")
                    desc = c.get("description", "")
                    price = c.get("pricing", {}).get("unit_price", "N/A")
                    stock = c.get("availability", {}).get("stock", 0)
                    ds = c.get("datasheet", {}).get("url", "")
                    comp_lines.append(
                        f"{idx}. **{mfr} {mpn}**: {desc}\n"
                        f"   - Stock: {stock:,} units | Price: INR {price}\n"
                        f"   - Datasheet: {ds or 'Not listed'}"
                    )
                
                return (
                    f"🔍 **[Octopart / Nexar MCP Intelligence]**\n"
                    f"Found the following component candidates matching your project constraints:\n\n"
                    + "\n\n".join(comp_lines) +
                    "\n\n👉 *To add any of these parts to your Bill of Materials or Knowledge Base, please select 'Add to BOM' or 'Save to Knowledge Base' in the Documents Index.*"
                )
        except Exception:
            pass

    # 2. Route through centralized Amazon Bedrock Model Router (DeepSeek R1)
    try:
        from backend.workline.ai.bedrock.router import model_router
        bom_summary = ", ".join([c.get("component") or c.get("name", "") for c in context.get("bom", [])])
        wiring_summary = json.dumps(context.get("wiring", []), indent=2)
        power_summary = json.dumps(context.get("power", {}).get("summary", {}), indent=2)

        system_prompt = f"""You are WORKLINE AI's Engineering & Team Collaboration Copilot powered by DeepSeek R1.
Focus on:
- electrical connections, pinout compatibilities, and protocol constraints (I2C, SPI, UART, PWM, CAN, GPIO)
- datasheet interpretation and power budget analysis
- engineering team collaboration: work assignments, tasks, decisions, pending approvals, and ownership

You have access to the active project context:
- BOM: {bom_summary}
- Wiring Connections: {wiring_summary}
- Power Budget Summary: {power_summary}
{team_context_str}

Rules:
1. Do NOT answer unrelated generic questions.
2. Keep replies concise, technical, and blueprint-focused.
3. When answering team questions (who is working on what, pending approvals, engineering decisions), reference the collaboration context.
4. Only disclose collaboration data present in the context.
"""
        ai_res = model_router.research(prompt=message, system_instruction=system_prompt)
        if ai_res and ai_res.text:
            return ai_res.text
    except Exception:
        pass
            
    # --- Local Fallback Rules for Offline Sandbox Stability ---
    # Collaboration Fallbacks
    if any(k in msg_lower for k in ("who is working", "assigned to", "task", "tasks", "work items")):
        if active_tasks_list:
            return "📋 **[Collaboration Agent - Active Work Items]**\n" + "\n".join(active_tasks_list)
        return "📋 **[Collaboration Agent]**: There are currently no active tasks assigned in this team workspace."

    if any(k in msg_lower for k in ("pending approval", "approvals", "pending reviews")):
        if pending_approvals_list:
            return "🛡️ **[Collaboration Agent - Pending Approvals]**\n" + "\n".join(pending_approvals_list)
        return "🛡️ **[Collaboration Agent]**: All sensitive engineering changes are currently approved. No pending gate reviews."

    if any(k in msg_lower for k in ("decision", "why did we choose", "tradeoff", "trade-off")):
        if decisions_list:
            return "⚖️ **[Collaboration Agent - Engineering Decisions]**\n" + "\n".join(decisions_list)
        return "⚖️ **[Collaboration Agent]**: No formal architecture or component trade-off decisions recorded yet for this project."

    if any(k in msg_lower for k in ("who is on the team", "team members", "who is in", "teammates")):
        if team_members_list:
            return f"👥 **[Team Roster]**: {', '.join(team_members_list)}"
        return "👥 **[Team Roster]**: No team members recorded for this workspace."

    components = context.get("bom", [])
    comp_names = [c.get("component") or c.get("name", "").lower() for c in components]
    
    if "mpu" in msg_lower or "sensor" in msg_lower or "flex" in msg_lower:
        return (
            "⚠️ [Connection Assistant]: MPU6050 / Flex sensors require analog or I2C serial lines. "
            "Verify that your sensor SDA/SCL lines are mapped to ESP32 GPIO 21 (SDA) and GPIO 22 (SCL). "
            "Flex Sensors should be connected to Analog ADC pins (GPIO 32, 33, 34, 35, 36) with 10k ohm pull-down resistors. "
            "Caution: Flex sensors operate at 3.3V logic. Connecting directly to a 5V supply will overload the input gates."
        )
    elif "pwm" in msg_lower or "servo" in msg_lower or "motor" in msg_lower:
        return (
            "⚙️ [Connection Assistant]: Servos (SG90 / MG996R) draw high transient currents. "
            "In your active configuration, connect them to PCA9685 channels 0 to 5. "
            "Ensure the orange PWM wire goes to the signal pin, red to the center V+ pin, and brown to GND. "
            "Do NOT power servos directly from the ESP32 5V/3.3V logic pins; use the 7.4V battery pack terminal on the PCA9685 board."
        )
    elif "voltage" in msg_lower or "power" in msg_lower or "current" in msg_lower:
        power_w = context.get("power", {}).get("summary", {}).get("total_power_load_w", 0.0)
        runtime = context.get("power", {}).get("summary", {}).get("estimated_runtime_hours", 0.0)
        return (
            f"⚡ [Connection Assistant]: Power Budget Summary: Total system load is {power_w} Watts. "
            f"Estimated battery runtime is {runtime} hours. "
            "Verify that common ground (GND) is connected across all boards (ESP32, PCA9685, battery) to prevent logic glitches. "
            "Ensure voltage level shifters are connected between 3.3V logic (ESP32) and 5.0V logic (PCA9685/Servos) buses."
        )
        
    # Default fallback summarizing the loaded context
    bom_list = ", ".join([c.get("component") or c.get("name", "") for c in components])
    return (
        f"📝 [Connection Assistant]: Project Context: {bom_list or 'No components extracted'}.\n"
        "Regarding your query: Focus on pin wiring safety. Ensure I2C lines have pull-up resistors, "
        "voltage levels match logic thresholds, and motors are isolated from controller logic rails."
    )
