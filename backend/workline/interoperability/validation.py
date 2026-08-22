"""Result validator for external agent outputs."""

from typing import Any, Dict, List, Tuple
from backend.workline.interoperability.capabilities import AgentCapability


class AgentResultValidator:
    """Validates external agent responses against capability schemas and security policies."""

    @classmethod
    def validate_result(
        cls,
        capability: AgentCapability,
        result: Any,
        max_size_bytes: int = 10 * 1024 * 1024,  # 10 MB limit
    ) -> Tuple[bool, List[str]]:
        """Validate external result payload against the capability's output schema.
        
        Returns:
            (is_valid, list_of_error_messages)
        """
        errors: List[str] = []

        if result is None:
            return False, ["Result payload is None"]

        if not isinstance(result, dict):
            return False, [f"Expected dictionary result payload, got {type(result).__name__}"]

        schema = capability.output_schema
        if not schema:
            # If no strict schema defined, basic validation passes
            return True, []

        # Check required fields if declared in schema
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in result:
                errors.append(f"Missing required output field: '{field}'")

        # Check declared property types
        properties = schema.get("properties", {})
        for field, spec in properties.items():
            if field in result:
                val = result[field]
                expected_type = spec.get("type")
                if expected_type == "string" and not isinstance(val, str):
                    errors.append(f"Field '{field}' expected string, got {type(val).__name__}")
                elif expected_type == "number" and not isinstance(val, (int, float)):
                    errors.append(f"Field '{field}' expected number, got {type(val).__name__}")
                elif expected_type == "integer" and not isinstance(val, int):
                    errors.append(f"Field '{field}' expected integer, got {type(val).__name__}")
                elif expected_type == "boolean" and not isinstance(val, bool):
                    errors.append(f"Field '{field}' expected boolean, got {type(val).__name__}")
                elif expected_type == "array" and not isinstance(val, list):
                    errors.append(f"Field '{field}' expected array, got {type(val).__name__}")
                elif expected_type == "object" and not isinstance(val, dict):
                    errors.append(f"Field '{field}' expected object, got {type(val).__name__}")

        return (len(errors) == 0, errors)
