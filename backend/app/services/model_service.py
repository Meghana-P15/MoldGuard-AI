from pathlib import Path
import threading

from ai.moldguard_ai.runtime import ModelBundle
from ai.moldguard_ai.optimizer import optimize_settings
from backend.app.config import settings


class ModelService:
    _lock = threading.Lock()
    _bundle = None

    @classmethod
    def bundle(cls) -> ModelBundle:
        with cls._lock:
            if cls._bundle is None:
                cls._bundle = ModelBundle.load(Path(settings.model_dir))
        return cls._bundle

    @classmethod
    def predict(cls, params: dict, cycles: int) -> dict:
        bundle = cls.bundle()
        risk = bundle.predict_risk(params)
        energy = bundle.predict_energy(params)
        return {
            **risk,
            "predicted_energy": round(float(energy), 5),
            "projected_energy": round(float(energy * cycles), 5),
            "model_mode": bundle.model_mode,
            "note": (
                "Demo model: synthetic smoke-test data only."
                if bundle.model_mode == "demo"
                else "Prediction from configured trained model."
            ),
        }

    @classmethod
    def optimize(cls, params: dict, cycles: int) -> dict:
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
        result["model_mode"] = bundle.model_mode
        return result
