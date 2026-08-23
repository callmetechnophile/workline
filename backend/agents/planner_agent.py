from typing import Dict, Any, List
from datetime import datetime
from backend.workline.pipeline.orchestrator import SequentialPipelineOrchestrator


def run_engineering_pipeline(
    user_intent: str,
    target_days: int = 30,
    project_name: str = None,
    engineering_template: str = None,
    team_id: str = None,
    project_id: str = None,
) -> Dict[str, Any]:
    """
    R1 Entrypoint for autonomous engineering pipeline.
    Delegates to SequentialPipelineOrchestrator for sequential R2->R3->R4->R5 execution.
    """
    resolved_project_name = project_name or user_intent.split("\n")[0][:60].strip() or "Untitled Engineering Project"
    resolved_project_id = project_id or f"PROJ-{resolved_project_name[:4].upper()}"
    
    orchestrator = SequentialPipelineOrchestrator()
    return orchestrator.execute_pipeline(
        project_id=resolved_project_id,
        user_intent=user_intent,
        project_name=resolved_project_name,
        target_days=target_days,
        engineering_template=engineering_template,
        team_id=team_id,
    )


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
