from __future__ import annotations

import threading

from ai.moldguard_ai.runtime import ModelBundle
from backend.app.services.artifact_service import ArtifactService


class ModelService:
    _lock = threading.Lock()
    _bundle: ModelBundle | None = None

    @classmethod
    def bundle(cls) -> ModelBundle:
        with cls._lock:
            if cls._bundle is None:
                model_dir = ArtifactService.ensure_local_models()
                cls._bundle = ModelBundle.load(model_dir)
        return cls._bundle

    @classmethod
    def metadata(cls) -> dict:
        return cls.bundle().metadata

    @classmethod
    def validate_context(cls, machine: str, material: str):
        meta = cls.metadata()
        machines = set(meta.get("known_machines", []))
        materials = set(meta.get("energy_material_profiles", []))
        if machines and machine not in machines:
            raise ValueError(
                f"Unknown machine '{machine}'. Choose one of the machines learned from modelo.xlsx."
            )
        if materials and material not in materials:
            raise ValueError(
                f"Unknown material/profile '{material}'. Choose one of {sorted(materials)} from test_dataset.csv."
            )
