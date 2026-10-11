from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

from ai.moldguard_ai.config import ENERGY_FEATURES
from ai.training.common import build_energy_frame, load_energy_data, model_dir


def _profile(frame):
    return {feature: float(frame[feature].median()) for feature in ENERGY_FEATURES}


def train_energy(output_dir: Path | None = None) -> Dict[str, Any]:
    output_dir = output_dir or model_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    raw = load_energy_data()
    X, y, rows = build_energy_frame(raw)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    model = XGBRegressor(
        n_estimators=420,
        max_depth=5,
        learning_rate=0.035,
        subsample=0.92,
        colsample_bytree=0.92,
        min_child_weight=2,
        reg_lambda=1.0,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=2,
    )
    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    mae = float(mean_absolute_error(y_test, pred))
    rmse = float(mean_squared_error(y_test, pred) ** 0.5)
    r2 = float(r2_score(y_test, pred))

    metrics = {
        "rows_used": int(len(X)),
        "target": "TOTAL_ACT_POWER (watts)",
        "features": ENERGY_FEATURES,
        "mae_watts": mae,
        "rmse_watts": rmse,
        "r2": r2,
    }

    # Store only medians calculated from real measured telemetry. They are used as
    # inference profiles when live telemetry is not connected to the demo UI.
    profiles = {"GLOBAL": _profile(X)}
    material_profiles = {}
    for prodname, idx in rows.groupby("PRODNAME").groups.items():
        material_profiles[str(prodname)] = _profile(X.loc[list(idx)])

    metadata = {
        "energy_rows": int(len(X)),
        "energy_target": "TOTAL_ACT_POWER",
        "energy_target_unit": "W",
        "energy_features": ENERGY_FEATURES,
        "energy_validation_mae_watts": mae,
        "energy_validation_rmse_watts": rmse,
        "energy_r2": r2,
        "energy_machine_names": sorted(str(x) for x in rows["MACHINENAME"].dropna().unique()),
        "energy_material_profiles": sorted(material_profiles.keys()),
        "energy_molds": sorted(str(x) for x in rows["MOLD_NAME"].dropna().unique()),
        "energy_profiles": {"GLOBAL": profiles["GLOBAL"], **material_profiles},
        "power_quantiles_watts": {
            "p05": float(np.quantile(y, 0.05)),
            "median": float(np.quantile(y, 0.50)),
            "p95": float(np.quantile(y, 0.95)),
        },
    }

    joblib.dump(model, output_dir / "energy_model.joblib")
    (output_dir / "energy_metrics.json").write_text(json.dumps(metrics, indent=2))
    return {"metrics": metrics, "metadata": metadata}


if __name__ == "__main__":
    result = train_energy()
    print(json.dumps(result["metrics"], indent=2))
