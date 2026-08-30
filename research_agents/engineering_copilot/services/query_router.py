"""
Query router and intent classification engine for EngineeringCopilotAgent (Sections 6–9).
Classifies 30+ user intents and extracts engineering entities (MPN, REQ-ID, subsystems, tasks).
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from research_agents.engineering_copilot.schemas import UserIntentLiteral


class EngineeringQueryRouter:
    """Classifies natural-language user queries and extracts domain entities."""

    def classify_intent_and_entities(self, query: str) -> Tuple[UserIntentLiteral, Dict[str, Any]]:
        q_lower = query.lower().strip()
        entities: Dict[str, Any] = {}

        # Extract potential entity IDs via regex
        req_match = re.search(r"(req[-\w]+)", query, re.IGNORECASE)
        if req_match:
            entities["requirement_id"] = req_match.group(1).upper()

        comp_match = re.search(r"(\d{3}-\d{4}-\d{2}|[A-Z0-9]{3,}-[A-Z0-9-]{3,})", query)
        if comp_match:
            entities["component_id"] = comp_match.group(1)

        task_match = re.search(r"(task[-\w]+|wp[-\w]+)", query, re.IGNORECASE)
        if task_match:
            entities["task_id"] = task_match.group(1).upper()

        dec_match = re.search(r"(dec[-\w]+)", query, re.IGNORECASE)
        if dec_match:
            entities["decision_id"] = dec_match.group(1).upper()

        # Deterministic Intent Matching
        if "trace" in q_lower or "lineage" in q_lower:
            if "req" in q_lower:
                return "REQUIREMENT_TRACE", entities
            elif "comp" in q_lower or "part" in q_lower:
                return "COMPONENT_IMPACT", entities
            return "TRACEABILITY_QUERY", entities

        if "impact" in q_lower or "replace" in q_lower or "substitute" in q_lower or "what happens if" in q_lower:
            if "comp" in q_lower or "part" in q_lower or "sensor" in q_lower or entities.get("component_id"):
                return "COMPONENT_IMPACT", entities
            return "CHANGE_IMPACT", entities

        if "compare" in q_lower or "diff" in q_lower or "vs" in q_lower:
            if "bom" in q_lower:
                return "BOM_COMPARISON", entities
            return "VERSION_COMPARISON", entities

        if "next" in q_lower or "what should happen" in q_lower or "what should i do" in q_lower:
            return "NEXT_ACTION", entities

        if "status" in q_lower or "state" in q_lower:
            return "PROJECT_STATUS", entities

        if "health" in q_lower:
            return "PROJECT_HEALTH", entities

        if "summary" in q_lower or "summarize" in q_lower or "overview" in q_lower:
            return "PROJECT_SUMMARY", entities

        if "block" in q_lower or "fail" in q_lower or "stuck" in q_lower or "why is" in q_lower:
            return "FAILURE_QUERY", entities

        if "bom" in q_lower or "bill of materials" in q_lower:
            return "BOM_QUERY", entities

        if "procurement" in q_lower or "supplier" in q_lower or "buy" in q_lower or "cost" in q_lower:
            return "PROCUREMENT_QUERY", entities

        if "decision" in q_lower or "why did we" in q_lower or "why was" in q_lower or "choose" in q_lower or "select" in q_lower:
            return "DECISION_EXPLANATION", entities

        if "qa" in q_lower or "test" in q_lower or "verify" in q_lower:
            return "QA_QUERY", entities

        if "timeline" in q_lower or "history" in q_lower or "events" in q_lower:
            return "TIMELINE_QUERY", entities

        if "ignore previous instructions" in q_lower or "ignore all instructions" in q_lower or "system prompt" in q_lower:
            return "UNKNOWN", entities

        if "run" in q_lower or "execute" in q_lower or "deploy" in q_lower or "modify" in q_lower or "change" in q_lower or "start" in q_lower or "delete" in q_lower:
            return "ACTION_REQUEST", entities

        if "req" in q_lower or "requirement" in q_lower:
            return "REQUIREMENT_QUERY", entities

        if "arch" in q_lower or "subsystem" in q_lower or "interface" in q_lower:
            return "ARCHITECTURE_QUERY", entities

        if "comp" in q_lower or "part" in q_lower or entities.get("component_id"):
            return "COMPONENT_QUERY", entities

        return "UNKNOWN", entities
