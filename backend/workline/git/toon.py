"""TOON (Token-Oriented Object Notation) Serializer and Deserializer.

Provides a compact, human-readable structured format for Workline project manifests (.toon)
and package components.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import yaml
from backend.workline.git.models import WorklineToonManifest, ProjectGitManifest, ProjectGitHubManifest


class ToonSerializer:
    """Encodes and decodes Workline project metadata in canonical TOON format."""

    @staticmethod
    def encode(data: Any, indent_level: int = 0) -> str:
        """Serializes dictionary or list to clean indented TOON format."""
        lines = []
        indent = "  " * indent_level
        if isinstance(data, dict):
            for key, value in sorted(data.items(), key=lambda x: str(x[0])):
                if isinstance(value, dict):
                    lines.append(f"{indent}{key}:")
                    nested = ToonSerializer.encode(value, indent_level + 1)
                    if nested:
                        lines.append(nested)
                elif isinstance(value, list):
                    lines.append(f"{indent}{key}:")
                    for item in value:
                        if isinstance(item, dict):
                            lines.append(f"{indent}  -")
                            nested_item = ToonSerializer.encode(item, indent_level + 2)
                            if nested_item:
                                lines.append(nested_item)
                        else:
                            lines.append(f"{indent}  - {ToonSerializer._format_scalar(item)}")
                else:
                    lines.append(f"{indent}{key}: {ToonSerializer._format_scalar(value)}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    lines.append(f"{indent}-")
                    nested_item = ToonSerializer.encode(item, indent_level + 1)
                    if nested_item:
                        lines.append(nested_item)
                else:
                    lines.append(f"{indent}- {ToonSerializer._format_scalar(item)}")
        else:
            lines.append(f"{indent}{ToonSerializer._format_scalar(data)}")
        return "\n".join(lines)

    @staticmethod
    def _format_scalar(val: Any) -> str:
        if val is None:
            return "null"
        if isinstance(val, bool):
            return "true" if val else "false"
        if isinstance(val, (int, float)):
            return str(val)
        # String
        s = str(val)
        if "\n" in s or ":" in s or s.startswith(" ") or s.endswith(" ") or s in ("true", "false", "null") or s.startswith("-"):
            escaped = s.replace('"', '\\"')
            return f'"{escaped}"'
        return s

    @staticmethod
    def decode(toon_str: str) -> Any:
        """Parses TOON formatted text into nested Python dictionaries and lists."""
        if not toon_str or not toon_str.strip():
            return {}
        try:
            res = yaml.safe_load(toon_str)
            return res if res is not None else {}
        except Exception:
            # Fallback scalar parser
            return {}

    @classmethod
    def dict_to_toon(cls, data: Dict[str, Any]) -> str:
        """Serialize arbitrary dictionary to canonical TOON string."""
        return cls.encode(data)

    @classmethod
    def dict_from_toon(cls, toon_str: str) -> Dict[str, Any]:
        """Deserialize TOON string to Python dictionary."""
        res = cls.decode(toon_str)
        return res if isinstance(res, dict) else {"items": res} if isinstance(res, list) else {"value": res}

    @classmethod
    def manifest_to_toon(cls, manifest: WorklineToonManifest) -> str:
        """Convert WorklineToonManifest model to TOON string."""
        return cls.encode(manifest.model_dump())

    @classmethod
    def manifest_from_toon(cls, toon_str: str) -> WorklineToonManifest:
        """Parse TOON string into WorklineToonManifest model."""
        data = cls.decode(toon_str)
        if not isinstance(data, dict):
            data = {}
        return WorklineToonManifest.model_validate(data)
