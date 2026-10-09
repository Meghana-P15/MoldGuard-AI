from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List
import json
import numpy as np
import pandas as pd
import joblib
import xgboost as xgb

from .config import FEATURES, CLASS_NAMES


@dataclass
class ModelBundle:
    risk_model: Any
    energy_model: Any
    metadata: Dict[str, Any]
    model_mode: str = "demo"

    @classmethod
    def load(cls, model_dir: str | Path) -> "ModelBundle":
        model_dir = Path(model_dir)
        risk_path = model_dir / "risk_model.joblib"
        energy_path = model_dir / "energy_model.joblib"
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
            metadata=metadata,
            model_mode=metadata.get("model_mode", "unknown"),
        )

    def _frame(self, params: Dict[str, float]) -> pd.DataFrame:
        missing = [f for f in FEATURES if f not in params]
        if missing:
            raise ValueError(f"Missing model features: {missing}")
        return pd.DataFrame([[float(params[f]) for f in FEATURES]], columns=FEATURES)


    def predict_probabilities(self, params: Dict[str, float]) -> Dict[str, float]:
        """Fast class-probability inference without explanation overhead."""
        X = self._frame(params)
        probs = self.risk_model.predict_proba(X)[0]
        labels = self.metadata.get("labels", CLASS_NAMES)
        prob_map = {label: float(probs[i]) for i, label in enumerate(labels)}
        return {c: float(prob_map.get(c, 0.0)) for c in CLASS_NAMES}

    def predict_risk(self, params: Dict[str, float]) -> Dict[str, Any]:
        X = self._frame(params)
        probs = self.risk_model.predict_proba(X)[0]
        # XGBoost classifier is trained on integer classes 0/1/2 mapped to G/Y/R.
        labels = self.metadata.get("labels", CLASS_NAMES)
        pred_idx = int(np.argmax(probs))
        pred = labels[pred_idx]
        prob_map = {label: float(probs[i]) for i, label in enumerate(labels)}
        return {
            "prediction": pred,
            "probabilities": {c: float(prob_map.get(c, 0.0)) for c in CLASS_NAMES},
            "risk_level": {"G": "LOW", "Y": "MEDIUM", "R": "HIGH"}.get(pred, "UNKNOWN"),
            "top_risk_factors": self._xgb_contributions(X, pred),
        }

    def predict_energy(self, params: Dict[str, float]) -> float:
        X = self._frame(params)
        return float(self.energy_model.predict(X)[0])

    def _xgb_contributions(self, X: pd.DataFrame, predicted_class: str) -> List[Dict[str, Any]]:
        # XGBoost pred_contribs returns SHAP contribution values from the booster.
        try:
            booster = self.risk_model.get_booster()
            dm = xgb.DMatrix(X, feature_names=FEATURES)
            raw = booster.predict(dm, pred_contribs=True, strict_shape=True)

            # Expected multiclass shape: (rows, classes, features+1)
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
            )[:3]

            return [
                {
                    "feature": feature,
                    "impact": round(float(value), 5),
                    "direction": "increases" if value >= 0 else "decreases",
                }
                for feature, value in ranked
            ]
        except Exception:
            # Explanation should never break prediction serving.
            return []
