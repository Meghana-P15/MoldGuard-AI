from pathlib import Path
import threading
import uuid

from ai.moldguard_ai.runtime import ModelBundle
from ai.moldguard_ai.optimizer import optimize_settings
from ai.moldguard_ai.guardrails import decision_from_prediction
from ai.moldguard_ai.material_impact import (
    risk_weighted_material_proxy,
    compare_material_proxy,
)
from backend.app.services.artifact_service import ArtifactService


class ModelService:
    _lock = threading.Lock()
    _bundle = None

    @classmethod
    def bundle(cls) -> ModelBundle:
        with cls._lock:
            if cls._bundle is None:
                model_dir = ArtifactService.ensure_local_models()
                cls._bundle = ModelBundle.load(Path(model_dir))
        return cls._bundle

    @classmethod
    def predict(
        cls,
        params: dict,
        cycles: int,
        part_weight_g: float | None = None,
    ) -> dict:
        bundle = cls.bundle()
        risk = bundle.predict_risk(params)
        energy = bundle.predict_energy(params)
        distribution = bundle.distribution_check(params)
        decision = decision_from_prediction(
            risk["probabilities"],
            distribution["status"],
        )
        material = risk_weighted_material_proxy(
            risk["probabilities"],
            cycles,
            part_weight_g,
        )

        return {
            **risk,
            **decision,
            "distribution": distribution,
            "predicted_energy": round(float(energy["value"]), 5),
            "energy_interval": {
                "low": round(float(energy["interval_low"]), 5),
                "high": round(float(energy["interval_high"]), 5),
                "validation_mae": round(float(energy["validation_mae"]), 5),
            },
            "projected_energy": round(float(energy["value"] * cycles), 5),
            "material_impact": material,
            "model_mode": bundle.model_mode,
            "note": (
                "Demo model: synthetic smoke-test data only."
                if bundle.model_mode == "demo"
                else "Prediction from configured trained model."
            ),
        }

    @classmethod
    def optimize(
        cls,
        params: dict,
        cycles: int,
        part_weight_g: float | None = None,
    ) -> dict:
        bundle = cls.bundle()
        result = optimize_settings(bundle, params)
        current_total = result["current"]["energy"] * cycles
        optimized_total = result["optimized"]["energy"] * cycles

        result["projected"] = {
            "cycles": cycles,
            "current_energy": round(current_total, 5),
            "optimized_energy": round(optimized_total, 5),
            "energy_saved": round(current_total - optimized_total, 5),
        }
        result["material_impact"] = compare_material_proxy(
            result["current"]["probabilities"],
            result["optimized"]["probabilities"],
            cycles,
            part_weight_g,
        )
        result["model_mode"] = bundle.model_mode
        return result

    @classmethod
    def analyze(
        cls,
        params: dict,
        cycles: int,
        part_weight_g: float | None = None,
    ) -> dict:
        run_id = str(uuid.uuid4())
        prediction = cls.predict(params, cycles, part_weight_g)
        optimization = cls.optimize(params, cycles, part_weight_g)

        return {
            "run_id": run_id,
            "prediction": prediction,
            "optimization": optimization,
        }
