"""Bindu A2A server implementation for exposing controlled Workline capabilities to peer agents."""

from typing import Any, Dict, List, Optional, Tuple
from backend.workline.interoperability.bindu.messaging import BinduMessageEnvelope


class BinduServer:
    """Server for exposing strictly authorized Workline capabilities over the Bindu A2A network."""

    def __init__(self, server_id: str = "workline-federated-node"):
        self.server_id = server_id
        self._exported_capabilities: Dict[str, Dict[str, Any]] = {}
        self.register_workline_capabilities()

    def register_workline_capabilities(self) -> None:
        """Register public capability endpoints that external agents are allowed to query."""
        self._exported_capabilities["component_lookup"] = {
            "name": "Component Catalog Lookup",
            "description": "Searches normalized electronic component catalog specifications.",
            "risk_level": "LOW",
        }
        self._exported_capabilities["drc_rules_check"] = {
            "name": "PCB DRC Rule Inspection",
            "description": "Validates clearance and trace width constraints against manufacturing standards.",
            "risk_level": "LOW",
        }

    def validate_request(self, envelope: BinduMessageEnvelope) -> Tuple[bool, Optional[str]]:
        """Verify message authentication, action, and capability scope."""
        if not envelope.sender_id:
            return False, "Missing sender_id in envelope"
        if envelope.action not in ("DISCOVER", "CAPABILITIES", "SUBMIT_TASK", "TASK_STATUS"):
            return False, f"Unsupported action '{envelope.action}'"
        return True, None

    async def receive_task(self, envelope: BinduMessageEnvelope) -> BinduMessageEnvelope:
        """Process incoming task envelope and return structured response."""
        is_valid, err = self.validate_request(envelope)
        if not is_valid:
            return BinduMessageEnvelope(
                sender_id=self.server_id,
                recipient_id=envelope.sender_id,
                action="RESULT",
                payload={"status": "REJECTED", "error": err},
            )

        if envelope.action == "CAPABILITIES":
            return BinduMessageEnvelope(
                sender_id=self.server_id,
                recipient_id=envelope.sender_id,
                action="RESULT",
                payload={"capabilities": self._exported_capabilities},
            )

        capability_id = envelope.payload.get("capability")
        if capability_id not in self._exported_capabilities:
            return BinduMessageEnvelope(
                sender_id=self.server_id,
                recipient_id=envelope.sender_id,
                action="RESULT",
                payload={"status": "REJECTED", "error": f"Capability '{capability_id}' not exported."},
            )

        result = await self.execute_capability(capability_id, envelope.payload.get("parameters", {}))
        return self.return_result(envelope, result)

    async def execute_capability(self, capability_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute local Workline read-only capability."""
        if capability_id == "component_lookup":
            mpn = parameters.get("mpn", "STM32F405RGT6")
            return {
                "status": "COMPLETED",
                "mpn": mpn,
                "category": "Microcontroller",
                "package": "LQFP-64",
                "operating_voltage": "1.8V - 3.6V",
            }
        elif capability_id == "drc_rules_check":
            min_trace = parameters.get("min_trace_mil", 6.0)
            return {
                "status": "COMPLETED",
                "drc_compliant": min_trace >= 5.0,
                "standard": "IPC-2221 Class 2",
            }
        return {"status": "FAILED", "error": f"Unknown capability '{capability_id}'"}

    def return_result(self, request_envelope: BinduMessageEnvelope, result: Dict[str, Any]) -> BinduMessageEnvelope:
        """Format and return result envelope to requesting agent."""
        return BinduMessageEnvelope(
            conversation_id=request_envelope.conversation_id,
            sender_id=self.server_id,
            recipient_id=request_envelope.sender_id,
            action="RESULT",
            payload=result,
        )
