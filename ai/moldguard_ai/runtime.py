from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List
import json

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from .config import (
    ENERGY_FEATURES,
    FEATURES,
    GOOD_MAX_DEFECT_RATE,
    WARNING_MAX_DEFECT_RATE,
)


@dataclass
class ModelBundle:
    risk_model: Any
    energy_model: Any
    ood_model: Any
    metadata: Dict[str, Any]
    model_mode: str

    @classmethod
    def load(cls, model_dir: str | Path) -> "ModelBundle":
        model_dir = Path(model_dir)
        required = {
            "risk": model_dir / "risk_model.joblib",
            "energy": model_dir / "energy_model.joblib",
            "ood": model_dir / "ood_model.joblib",
            "metadata": model_dir / "metadata.json",
        }
        missing = [str(path) for path in required.values() if not path.exists()]
        if missing:
            raise FileNotFoundError(
                "Model artifacts are missing. Run `python -m ai.training.train_all`. "
                f"Missing: {missing}"
            )
        metadata = json.loads(required["metadata"].read_text())
        return cls(
            risk_model=joblib.load(required["risk"]),
            energy_model=joblib.load(required["energy"]),
            ood_model=joblib.load(required["ood"]),
            metadata=metadata,
            model_mode=metadata.get("model_mode", "unknown"),
        )

    def _frame(self, params: Dict[str, float]) -> pd.DataFrame:
        missing = [feature for feature in FEATURES if feature not in params]
        if missing:
            raise ValueError(f"Missing model features: {missing}")
        return pd.DataFrame(
            [[float(params[feature]) for feature in FEATURES]], columns=FEATURES
        )

    def _frames(self, rows: List[Dict[str, float]]) -> pd.DataFrame:
        return pd.DataFrame(
            [[float(row[f]) for f in FEATURES] for row in rows], columns=FEATURES
        )

    def _risk_band(self, defect_rate: float) -> str:
        thresholds = self.metadata.get("defect_thresholds", {})
        good_max = float(thresholds.get("good_max", GOOD_MAX_DEFECT_RATE))
        warning_max = float(thresholds.get("warning_max", WARNING_MAX_DEFECT_RATE))
        if defect_rate <= good_max:
            return "G"
        if defect_rate <= warning_max:
            return "Y"
        return "R"

    def predict_defect_rate(self, params: Dict[str, float]) -> float:
        value = float(self.risk_model.predict(self._frame(params))[0])
        return float(np.clip(value, 0.0, 1.0))

    def predict_defect_rate_batch(self, rows: List[Dict[str, float]]) -> np.ndarray:
        return np.clip(self.risk_model.predict(self._frames(rows)), 0.0, 1.0)

    def predict_risk(self, params: Dict[str, float]) -> Dict[str, Any]:
        X = self._frame(params)
        predicted_defect_rate = float(np.clip(self.risk_model.predict(X)[0], 0.0, 1.0))
        pred = self._risk_band(predicted_defect_rate)
        mae = float(self.metadata.get("defect_validation_mae", 0.0))
        return {
            "prediction": pred,
            "risk_level": {"G": "LOW", "Y": "MEDIUM", "R": "HIGH"}[pred],
            "predicted_defect_rate": predicted_defect_rate,
            "predicted_defect_percent": predicted_defect_rate * 100.0,
            "uncertainty_defect_rate": mae,
            "uncertainty_percentage_points": mae * 100.0,
            "range_defect_rate": [
                max(0.0, predicted_defect_rate - mae),
                min(1.0, predicted_defect_rate + mae),
            ],
            "model_reliability_estimate": float(
                self.metadata.get("defect_model_reliability_estimate", 0.0)
            ),
            "thresholds": self.metadata.get("defect_thresholds", {}),
            "top_risk_factors": self._xgb_contributions(X),
        }

    def predict_ood(self, params: Dict[str, float]) -> Dict[str, Any]:
        X = self._frame(params)
        raw_score = float(self.ood_model.decision_function(X)[0])
        in_distribution = bool(self.ood_model.predict(X)[0] == 1)
        lo = float(self.metadata.get("ood_score_p05", -0.1))
        hi = float(self.metadata.get("ood_score_p95", 0.1))
        familiarity = float(np.clip((raw_score - lo) / max(hi - lo, 1e-9), 0.0, 1.0))
        return {
            "in_distribution": in_distribution,
            "familiarity_score": familiarity,
            "ood_score": raw_score,
            "label": "IN_DISTRIBUTION" if in_distribution else "OUT_OF_DISTRIBUTION",
        }

    def predict_ood_batch(self, rows: List[Dict[str, float]]) -> np.ndarray:
        return self.ood_model.predict(self._frames(rows))

    def _energy_profile(self, material: str | None = None) -> Dict[str, float]:
        profiles = self.metadata.get("energy_profiles", {})
        profile = profiles.get(material or "") or profiles.get("GLOBAL")
        if not profile:
            raise ValueError("Energy telemetry profile is missing from metadata")
        return {feature: float(profile[feature]) for feature in ENERGY_FEATURES}

    def predict_power_watts(self, material: str | None = None) -> float:
        profile = self._energy_profile(material)
        X = pd.DataFrame([[profile[f] for f in ENERGY_FEATURES]], columns=ENERGY_FEATURES)
        return max(0.0, float(self.energy_model.predict(X)[0]))

    def predict_energy(self, params: Dict[str, float], material: str | None = None) -> Dict[str, float]:
        cycle_seconds = max(float(params["tinj"]), 0.001)
        power_watts = self.predict_power_watts(material)
        kwh_per_cycle = power_watts * cycle_seconds / 3_600_000.0
        mae_watts = float(self.metadata.get("energy_validation_mae_watts", 0.0))
        uncertainty = mae_watts * cycle_seconds / 3_600_000.0
        return {
            "predicted_power_watts": power_watts,
            "kwh_per_cycle": kwh_per_cycle,
            "uncertainty_kwh": uncertainty,
            "lower_kwh_per_cycle": max(0.0, kwh_per_cycle - uncertainty),
            "upper_kwh_per_cycle": kwh_per_cycle + uncertainty,
        }

    def _xgb_contributions(self, X: pd.DataFrame) -> List[Dict[str, Any]]:
        try:
            booster = self.risk_model.get_booster()
            dm = xgb.DMatrix(X, feature_names=FEATURES)
            raw = booster.predict(dm, pred_contribs=True)
            vals = raw[0, :-1]
            ranked = sorted(
                zip(FEATURES, vals), key=lambda item: abs(float(item[1])), reverse=True
            )[:3]
            return [
                {
                    "feature": feature,
                    "impact": round(float(value) * 100.0, 5),
                    "direction": "increases" if value >= 0 else "decreases",
                }
                for feature, value in ranked
            ]
        except Exception:
            return []
