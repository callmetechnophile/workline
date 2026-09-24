"""
WORKLINE Environment State & Session Manager.

Maintains machine-local activation state, active project session,
and service degradation flags.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from cli.wline.core.paths import ensure_config_dir, get_config_dir

ActivationStatus = Literal["INACTIVE", "STARTING", "ACTIVE", "DEGRADED", "STOPPING", "ERROR"]


@dataclass
class ServiceHealth:
    name: str
    status: str  # "READY", "DEGRADED", "UNAVAILABLE", "NOT_CONFIGURED"
    detail: str = ""
    is_essential: bool = False


@dataclass
class EnvironmentState:
    status: ActivationStatus = "INACTIVE"
    activated_at: Optional[str] = None
    last_ping: Optional[str] = None
    active_project_id: Optional[str] = None
    active_project_name: Optional[str] = None
    active_project_path: Optional[str] = None
    active_api_profile: str = "default"
    services: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    degraded_reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnvironmentState":
        return cls(
            status=data.get("status", "INACTIVE"),
            activated_at=data.get("activated_at"),
            last_ping=data.get("last_ping"),
            active_project_id=data.get("active_project_id"),
            active_project_name=data.get("active_project_name"),
            active_project_path=data.get("active_project_path"),
            active_api_profile=data.get("active_api_profile", "default"),
            services=data.get("services", {}),
            degraded_reasons=data.get("degraded_reasons", []),
        )


class EnvironmentSessionManager:
    """Manages the persistent WORKLINE activation session at ~/.workline/session.json."""

    @staticmethod
    def get_session_file() -> Path:
        return get_config_dir() / "session.json"

    @classmethod
    def load_state(cls) -> EnvironmentState:
        session_file = cls.get_session_file()
        if session_file.exists():
            try:
                data = json.loads(session_file.read_text(encoding="utf-8"))
                return EnvironmentState.from_dict(data)
            except Exception:
                pass
        return EnvironmentState()

    @classmethod
    def save_state(cls, state: EnvironmentState) -> None:
        ensure_config_dir()
        state.last_ping = datetime.now(timezone.utc).isoformat()
        cls.get_session_file().write_text(
            json.dumps(state.to_dict(), indent=2),
            encoding="utf-8",
        )

    @classmethod
    def activate(
        cls,
        services: Dict[str, ServiceHealth],
        active_project_path: Optional[Path] = None,
    ) -> EnvironmentState:
        state = cls.load_state()
        state.activated_at = datetime.now(timezone.utc).isoformat()
        state.services = {k: asdict(v) for k, v in services.items()}

        degraded: List[str] = []
        for name, sh in services.items():
            if sh.status in ("UNAVAILABLE", "DEGRADED"):
                degraded.append(f"{name}: {sh.detail or sh.status}")

        if any(sh.status == "UNAVAILABLE" and sh.is_essential for sh in services.values()):
            state.status = "ERROR"
        elif degraded:
            state.status = "DEGRADED"
            state.degraded_reasons = degraded
        else:
            state.status = "ACTIVE"
            state.degraded_reasons = []

        if active_project_path:
            cls._attach_project_to_state(state, active_project_path)

        cls.save_state(state)
        return state

    @classmethod
    def set_active_project(cls, project_path: Path) -> EnvironmentState:
        state = cls.load_state()
        cls._attach_project_to_state(state, project_path)
        cls.save_state(state)
        return state

    @classmethod
    def clear_active_project(cls) -> EnvironmentState:
        state = cls.load_state()
        state.active_project_id = None
        state.active_project_name = None
        state.active_project_path = None
        cls.save_state(state)
        return state

    @classmethod
    def get_active_project_root(cls) -> Optional[Path]:
        state = cls.load_state()
        if state.active_project_path:
            p = Path(state.active_project_path)
            if p.exists():
                return p
        return None

    @classmethod
    def deactivate(cls) -> EnvironmentState:
        state = cls.load_state()
        state.status = "INACTIVE"
        cls.save_state(state)
        return state

    @classmethod
    def is_active(cls) -> bool:
        state = cls.load_state()
        return state.status in ("ACTIVE", "DEGRADED")

    @staticmethod
    def _attach_project_to_state(state: EnvironmentState, project_path: Path) -> None:
        from cli.workline.project.filesystem import find_project_root
        root = find_project_root(project_path) or project_path.resolve()
        state.active_project_path = str(root)
        state.active_project_name = root.name

        readme = root / "README.wl"
        if readme.exists():
            try:
                from cli.workline.project.readme import parse_readme_wl
                identity = parse_readme_wl(readme)
                state.active_project_id = identity.project_id
                state.active_project_name = identity.name
            except Exception:
                pass
