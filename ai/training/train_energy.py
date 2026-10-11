from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

from ai.moldguard_ai.config import FEATURES
from ai.training.data_validation import validate_canonical_frame


def train_energy(
    df: pd.DataFrame,
    model_dir: Path,
    target: str = "energy",
) -> Dict[str, Any]:
    validate_canonical_frame(df, [target])

    X = df[FEATURES].copy()
    y = df[target].astype(float)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.22,
        random_state=42,
    )

    model = XGBRegressor(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.045,
        min_child_weight=2,
        subsample=0.90,
        colsample_bytree=0.90,
        reg_lambda=1.2,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=2,
    )
    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, pred)
    rmse = mean_squared_error(y_test, pred) ** 0.5
    r2 = r2_score(y_test, pred)

    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_dir / "energy_model.joblib")

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
    }
