"""Filesystem model checkpoint manager and metadata persistence."""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, Field

from cli.wline.core.paths import get_config_dir
from backend.workline.pcb.pinn.metrics import PINNValidationMetrics


class ModelCheckpointMetadata(BaseModel):
    """Metadata tracking trained PINN model provenance and reproducibility."""
    model_id: str
    project_id: str
    dataset_id: str
    dataset_version: int = 1
    physics_problem: str = "Steady-State PCB Thermal Distribution"
    architecture: Dict[str, Any]
    training_config: Dict[str, Any]
    metrics: PINNValidationMetrics
    checkpoint_file: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CheckpointManager:
    """Manages saving and loading model artifacts and reproducibility logs."""

    def __init__(self):
        self._dir = get_config_dir() / "models" / "pinn"
        self._dir.mkdir(parents=True, exist_ok=True)
        self._metadata_dir = get_config_dir() / "models" / "metadata"
        self._metadata_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(
        self,
        project_id: str,
        dataset_id: str,
        state_dict: Dict[str, Any],
        metrics: PINNValidationMetrics,
        training_config: Dict[str, Any],
    ) -> ModelCheckpointMetadata:
        """Stores binary/JSON weights on filesystem and saves metadata record."""
        model_id = f"pinn_thm_{uuid.uuid4().hex[:8]}"
        ckpt_filename = f"{model_id}.json"
        ckpt_path = self._dir / ckpt_filename

        with open(ckpt_path, "w", encoding="utf-8") as fp:
            json.dump(state_dict, fp, indent=2)

        meta = ModelCheckpointMetadata(
            model_id=model_id,
            project_id=project_id,
            dataset_id=dataset_id,
            dataset_version=1,
            architecture={
                "input_dim": state_dict.get("input_dim", 7),
                "hidden_dim": state_dict.get("hidden_dim", 48),
                "hidden_layers": state_dict.get("hidden_layers", 3),
                "activation": state_dict.get("activation", "tanh"),
            },
            training_config=training_config,
            metrics=metrics,
            checkpoint_file=str(ckpt_path),
        )

        meta_path = self._metadata_dir / f"{model_id}.json"
        with open(meta_path, "w", encoding="utf-8") as fp:
            fp.write(meta.model_dump_json(indent=2))

        return meta

    def load_checkpoint(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Load state dict from disk."""
        ckpt_path = self._dir / f"{model_id}.json"
        if ckpt_path.exists():
            try:
                with open(ckpt_path, "r", encoding="utf-8") as fp:
                    return json.load(fp)
            except Exception:
                pass
        return None
