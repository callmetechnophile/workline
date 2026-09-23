"""
Configuration management for WORKLINE CLI and Local Moss Retrieval.
"""

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import List, Optional, Set


@dataclass
class MossConfig:
    """Configuration for local Moss indexing and retrieval."""
    enabled: bool = True
    index_dirname: str = ".wl/index"
    metadata_filename: str = ".wl/moss.wl"
    runtime: str = "local"
    schema_version: int = 1
    top_k: int = 10
    score_threshold: float = 0.25
    max_chunk_size: int = 512
    max_chunk_overlap: int = 64
    embedding_dim: int = 128
    
    # Invariant: Strict zero-secrets filter
    secret_patterns: Set[str] = field(default_factory=lambda: {
        ".env",
        ".env.*",
        "*.env",
        "credentials*",
        "*.pem",
        "*.key",
        "*.token",
        "*.secret",
        "id_rsa*",
        "id_ed25519*",
        "private*",
        "secrets/*",
        ".git/*",
        "__pycache__/*",
        "node_modules/*",
        ".venv/*",
    })


@dataclass
class LiveKitConfig:
    """Configuration for LiveKit realtime agent communication."""
    enabled: bool = True
    agent_name: str = "workline-realtime-agent"
    room_mode: str = "project"
    realtime: bool = True
    room_prefix: str = "workline-project-"
    url: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None

    @classmethod
    def load(cls, project_root: Optional[Path] = None) -> "LiveKitConfig":
        """Load LiveKit configuration from .wl/livekit.wl and environment variables."""
        cfg = cls(
            url=os.environ.get("LIVEKIT_URL"),
            api_key=os.environ.get("LIVEKIT_API_KEY"),
            api_secret=os.environ.get("LIVEKIT_API_SECRET"),
            agent_name=os.environ.get("LIVEKIT_AGENT_NAME", "workline-realtime-agent"),
            room_prefix=os.environ.get("LIVEKIT_ROOM_PREFIX", "workline-project-"),
        )
        
        if project_root:
            lk_file = project_root / ".wl" / "livekit.wl"
            if lk_file.exists():
                import yaml
                try:
                    data = yaml.safe_load(lk_file.read_text(encoding="utf-8")) or {}
                    lk_data = data.get("livekit", {})
                    cfg.enabled = lk_data.get("enabled", True)
                    cfg.agent_name = lk_data.get("agent_name", cfg.agent_name)
                    cfg.room_mode = lk_data.get("room_mode", cfg.room_mode)
                    cfg.realtime = lk_data.get("realtime", cfg.realtime)
                    cfg.room_prefix = lk_data.get("room_prefix", cfg.room_prefix)
                except Exception:
                    pass
        return cfg


@dataclass
class WorklineCLIConfig:
    """Master configuration for WORKLINE CLI runtime."""
    offline: bool = False
    active_project_path: Optional[Path] = None
    moss: MossConfig = field(default_factory=MossConfig)
    livekit: LiveKitConfig = field(default_factory=LiveKitConfig)
    llm_provider: str = "local"  # "local", "bedrock", "openai", "none"
    llm_model: str = "anthropic.claude-3-5-sonnet"
    
    @classmethod
    def load(cls, project_dir: Optional[Path] = None, offline: bool = False) -> "WorklineCLIConfig":
        """Load configuration from environment variables and optional project directory."""
        env_offline = os.environ.get("WORKLINE_OFFLINE", "").lower() in ("1", "true", "yes")
        is_offline = offline or env_offline
        
        env_proj = os.environ.get("WORKLINE_PROJECT_PATH")
        proj_path = Path(env_proj).resolve() if env_proj else (project_dir.resolve() if project_dir else None)
        
        return cls(
            offline=is_offline,
            active_project_path=proj_path,
            moss=MossConfig(),
            livekit=LiveKitConfig.load(proj_path),
            llm_provider=os.environ.get("WORKLINE_LLM_PROVIDER", "local"),
            llm_model=os.environ.get("WORKLINE_LLM_MODEL", "anthropic.claude-3-5-sonnet"),
        )

