from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

from ai.moldguard_ai.config import (
    FEATURES,
    GOOD_MAX_DEFECT_RATE,
    WARNING_MAX_DEFECT_RATE,
)
from ai.training.common import build_risk_frame, load_molding_data, model_dir


def _band(values):
    values = np.asarray(values, dtype=float)
    return np.where(
        values <= GOOD_MAX_DEFECT_RATE,
        "G",
        np.where(values <= WARNING_MAX_DEFECT_RATE, "Y", "R"),
    )


def train_risk(output_dir: Path | None = None) -> Dict[str, Any]:
    """Train a real defect-rate regressor plus an OOD detector.

    The model predicts measured %Defectuosos directly. G/Y/R is applied only
    after prediction using explicit operational thresholds; it is not a
    synthetic classification target.
    """
    output_dir = output_dir or model_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    raw = load_molding_data()
    X, defect, rows = build_risk_frame(raw)

    X_train, X_test, y_train, y_test = train_test_split(
        X, defect, test_size=0.22, random_state=42
    )

    model = XGBRegressor(
        n_estimators=520,
        max_depth=5,
        learning_rate=0.03,
        subsample=0.90,
        colsample_bytree=0.90,
        min_child_weight=2,
        reg_lambda=1.0,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=2,
    )
    model.fit(X_train, y_train)
    pred = np.clip(model.predict(X_test), 0.0, 1.0)

    mae = float(mean_absolute_error(y_test, pred))
    rmse = float(mean_squared_error(y_test, pred) ** 0.5)
    r2 = float(r2_score(y_test, pred))
    band_accuracy = float(accuracy_score(_band(y_test), _band(pred)))

    # OOD detector uses only measured real process settings.
    ood = IsolationForest(
        n_estimators=350,
        contamination=0.03,
        random_state=42,
        n_jobs=2,
    )
    ood.fit(X_train)
    train_scores = ood.decision_function(X_train)

    metrics = {
        "rows_used": int(len(X)),
        "target": "%Defectuosos (fraction; 0.05 = 5%)",
        "model": "XGBRegressor",
        "mae_defect_rate": mae,
        "mae_percentage_points": mae * 100.0,
        "rmse_defect_rate": rmse,
        "rmse_percentage_points": rmse * 100.0,
        "r2": r2,
        "decision_band_accuracy": band_accuracy,
        "decision_thresholds": {
            "good_max": GOOD_MAX_DEFECT_RATE,
            "warning_max": WARNING_MAX_DEFECT_RATE,
        },
    }

    feature_stats = {}
    for feature in FEATURES:
        s = X[feature]
        feature_stats[feature] = {
            "min": float(s.min()),
            "p01": float(s.quantile(0.01)),
            "median": float(s.median()),
            "p99": float(s.quantile(0.99)),
            "max": float(s.max()),
        }

    target_range = max(float(defect.max() - defect.min()), 1e-9)
    reliability = float(np.clip(1.0 - mae / target_range, 0.0, 1.0))

    metadata = {
        "risk_rows": int(len(X)),
        "risk_model_type": "defect_rate_regression_with_thresholds",
        "risk_target": "%Defectuosos",
        "defect_thresholds": {
            "good_max": GOOD_MAX_DEFECT_RATE,
            "warning_max": WARNING_MAX_DEFECT_RATE,
        },
        "defect_validation_mae": mae,
        "defect_validation_rmse": rmse,
        "defect_r2": r2,
        "defect_model_reliability_estimate": reliability,
        "feature_stats": feature_stats,
        "ood_score_p05": float(np.quantile(train_scores, 0.05)),
        "ood_score_p95": float(np.quantile(train_scores, 0.95)),
        "known_machines": sorted(str(x) for x in rows["Maquina"].dropna().unique()),
        "known_products_sample": sorted(str(x) for x in rows["Nombre_producto"].dropna().unique())[:100],
        "part_weight": {
            "median_g": float(rows["Peso_producto_gramos"].median()),
            "min_g": float(rows["Peso_producto_gramos"].min()),
            "max_g": float(rows["Peso_producto_gramos"].max()),
        },
    }

    joblib.dump(model, output_dir / "risk_model.joblib")
    joblib.dump(ood, output_dir / "ood_model.joblib")
    (output_dir / "risk_metrics.json").write_text(json.dumps(metrics, indent=2))
    return {"metrics": metrics, "metadata": metadata}


if __name__ == "__main__":
    result = train_risk()
    print(json.dumps(result["metrics"], indent=2))
