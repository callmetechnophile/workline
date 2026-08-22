"""Finance Agent: Estimates component costs, total BOM price, shipping, and unit economics."""

from typing import Any, Dict, Optional
from backend.workline.agents.shared.prompts import FINANCE_AGENT_PROMPT
from backend.workline.agents.shared.schemas import AgentFinding, AgentOutput
from backend.workline.agents.shared.tools import WorklineToolSuite


class FinanceAgent:
    """Specialist agent analyzing procurement budget, shipping assumptions, and unit costs."""

    def __init__(self, tools: Optional[WorklineToolSuite] = None):
        self.tools = tools or WorklineToolSuite()
        self.name = "finance_agent"
        self.prompt = FINANCE_AGENT_PROMPT

    async def execute(self, project_id: str, context: Dict[str, Any]) -> AgentOutput:
        """Calculate preliminary budget and BOM pricing breakdown."""
        line_items = [
            {"name": "ESP32-S3-WROOM-1-N8R8", "qty": 1, "unit_usd": 3.50, "subtotal_usd": 3.50},
            {"name": "DRV8833PWPR Dual H-Bridge", "qty": 1, "unit_usd": 1.45, "subtotal_usd": 1.45},
            {"name": "BME280 Sensor", "qty": 1, "unit_usd": 3.20, "subtotal_usd": 3.20},
            {"name": "MPU-6050 6-DoF IMU", "qty": 1, "unit_usd": 2.10, "subtotal_usd": 2.10},
            {"name": "TPS62840 Buck Regulator", "qty": 1, "unit_usd": 1.15, "subtotal_usd": 1.15},
            {"name": "Passives (Capacitors, Resistors, Diodes)", "qty": 18, "unit_usd": 0.08, "subtotal_usd": 1.44},
            {"name": "Connectors & Terminals", "qty": 4, "unit_usd": 0.40, "subtotal_usd": 1.60},
        ]

        total_component_cost = sum(item["subtotal_usd"] for item in line_items)
        estimated_pcb_manufacturing = 5.00  # 5 boards prototype estimate
        estimated_shipping = 4.50
        total_estimated_budget = total_component_cost + estimated_pcb_manufacturing + estimated_shipping

        finance_data = {
            "component_subtotal_usd": round(total_component_cost, 2),
            "estimated_pcb_usd": estimated_pcb_manufacturing,
            "estimated_shipping_usd": estimated_shipping,
            "total_estimated_budget_usd": round(total_estimated_budget, 2),
            "line_items": line_items,
        }

        findings = [
            AgentFinding(
                category="Finance",
                title="BOM Budget Estimate",
                detail=f"Total estimated single-unit hardware cost: ${total_estimated_budget:.2f} USD.",
                severity="INFO",
            )
        ]

        return AgentOutput(
            agent=self.name,
            status="COMPLETED",
            stage="procurement_analysis",
            summary=f"Estimated BOM hardware cost at ${total_component_cost:.2f} USD (${total_estimated_budget:.2f} including PCB and freight).",
            findings=findings,
            data=finance_data,
        )
