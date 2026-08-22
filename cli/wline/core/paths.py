"""Path resolution and directory constants for Workline."""

import os
from pathlib import Path
from typing import Optional


def get_config_dir() -> Path:
    """Return the Workline configuration directory (~/.workline by default)."""
    env_cfg = os.environ.get("WORKLINE_CONFIG_DIR")
    if env_cfg:
        return Path(env_cfg).resolve()
    return Path.home() / ".workline"


def get_config_file() -> Path:
    """Return path to config.yaml."""
    return get_config_dir() / "config.yaml"


def get_active_project_file() -> Path:
    """Return path to active_project file."""
    return get_config_dir() / "active_project"


def get_default_workspace_dir() -> Path:
    """Return default workspace root directory (~/Workline)."""
    return Path.home() / "Workline"


def get_workspace_dir() -> Path:
    """
    Return currently configured workspace root directory.
    Priority: WORKLINE_WORKSPACE env var > config.yaml > ~/Workline.
    """
    env_ws = os.environ.get("WORKLINE_WORKSPACE")
    if env_ws:
        return Path(env_ws).resolve()

    cfg_file = get_config_file()
    if cfg_file.exists():
        import yaml
        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and isinstance(data, dict) and "workspace" in data:
                    ws_val = data.get("workspace")
                    if ws_val:
                        return Path(ws_val).expanduser().resolve()
        except Exception:
            pass

    return get_default_workspace_dir().resolve()


def ensure_config_dir() -> Path:
    """Ensure that the configuration directory exists and return it."""
    cfg_dir = get_config_dir()
    cfg_dir.mkdir(parents=True, exist_ok=True)
    return cfg_dir


def set_active_project_name(name: str) -> None:
    """Record active project name in ~/.workline/active_project."""
    ensure_config_dir()
    active_file = get_active_project_file()
    active_file.write_text(name.strip(), encoding="utf-8")


def get_active_project_name() -> Optional[str]:
    """Retrieve active project name from ~/.workline/active_project."""
    active_file = get_active_project_file()
    if active_file.exists():
        name = active_file.read_text(encoding="utf-8").strip()
        return name if name else None
    return None


def clear_active_project() -> None:
    """Clear the active project reference."""
    active_file = get_active_project_file()
    if active_file.exists():
        try:
            active_file.unlink()
        except Exception:
            pass
