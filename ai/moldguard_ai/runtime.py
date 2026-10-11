from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List
import json

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from .config import FEATURES, CLASS_NAMES


@dataclass
class ModelBundle:
    risk_model: Any
    energy_model: Any
    metadata: Dict[str, Any]
    ood_model: Any | None = None
    model_mode: str = "demo"

    @classmethod
    def load(cls, model_dir: str | Path) -> "ModelBundle":
        model_dir = Path(model_dir)
        risk_path = model_dir / "risk_model.joblib"
        energy_path = model_dir / "energy_model.joblib"
        ood_path = model_dir / "ood_model.joblib"
        meta_path = model_dir / "metadata.json"

        if not risk_path.exists() or not energy_path.exists():
            raise FileNotFoundError(
                f"Model artifacts not found in {model_dir}. "
                "Run: python -m ai.training.generate_demo_data && "
                "python -m ai.training.train_all"
            )

        metadata = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        return cls(
            risk_model=joblib.load(risk_path),
            energy_model=joblib.load(energy_path),
            ood_model=joblib.load(ood_path) if ood_path.exists() else None,
            metadata=metadata,
            model_mode=metadata.get("model_mode", "unknown"),
        )

    def _frame(self, params: Dict[str, float]) -> pd.DataFrame:
        missing = [f for f in FEATURES if f not in params]
        if missing:
            raise ValueError(f"Missing model features: {missing}")
        return pd.DataFrame(
            [[float(params[f]) for f in FEATURES]],
            columns=FEATURES,
        )

    def predict_probabilities(self, params: Dict[str, float]) -> Dict[str, float]:
        X = self._frame(params)
        probs = self.risk_model.predict_proba(X)[0]
        labels = self.metadata.get("labels", CLASS_NAMES)
        prob_map = {label: float(probs[i]) for i, label in enumerate(labels)}
        return {c: float(prob_map.get(c, 0.0)) for c in CLASS_NAMES}

    def distribution_check(self, params: Dict[str, float]) -> Dict[str, Any]:
        if self.ood_model is None:
            return {
                "status": "UNKNOWN",
                "score": None,
                "note": "OOD detector artifact is not available.",
            }

        X = self._frame(params)
        # IsolationForest: decision_function > 0 is usually inlier.
        score = float(self.ood_model.decision_function(X)[0])
        pred = int(self.ood_model.predict(X)[0])
        return {
            "status": "IN_DISTRIBUTION" if pred == 1 else "OUT_OF_DISTRIBUTION",
            "score": round(score, 5),
            "note": (
                "This checks whether the input resembles the feature distribution "
                "seen during training; it is not a physical safety certificate."
            ),
        }

    def predict_risk(self, params: Dict[str, float]) -> Dict[str, Any]:
        X = self._frame(params)
        probabilities = self.predict_probabilities(params)
        pred = max(probabilities, key=probabilities.get)
        return {
            "prediction": pred,
            "probabilities": probabilities,
            "risk_level": {"G": "LOW", "Y": "MEDIUM", "R": "HIGH"}.get(pred, "UNKNOWN"),
            "top_risk_factors": self._xgb_contributions(X, pred),
        }

    def predict_energy(self, params: Dict[str, float]) -> Dict[str, float]:
        X = self._frame(params)
        pred = float(self.energy_model.predict(X)[0])
        mae = float(self.metadata.get("energy_validation_mae", 0.0) or 0.0)
        return {
            "value": pred,
            "interval_low": max(0.0, pred - mae),
            "interval_high": pred + mae,
            "validation_mae": mae,
        }

    def _xgb_contributions(
        self,
        X: pd.DataFrame,
        predicted_class: str,
    ) -> List[Dict[str, Any]]:
        try:
            booster = self.risk_model.get_booster()
            dm = xgb.DMatrix(X, feature_names=FEATURES)
            raw = booster.predict(dm, pred_contribs=True, strict_shape=True)

            if raw.ndim == 3:
                labels = self.metadata.get("labels", CLASS_NAMES)
                class_idx = labels.index(predicted_class)
                vals = raw[0, class_idx, :-1]
            elif raw.ndim == 2:
                vals = raw[0, :-1]
            else:
                return []

            ranked = sorted(
                zip(FEATURES, vals),
                key=lambda x: abs(float(x[1])),
                reverse=True,
            )[:4]

            return [
                {
                    "feature": feature,
                    "impact": round(float(value), 5),
                    "direction": "increases" if value >= 0 else "decreases",
                }
                for feature, value in ranked
            ]
        except Exception:
            # Explanation failure must not break prediction serving.
            return []
