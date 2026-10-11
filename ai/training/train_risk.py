from __future__ import annotations

from pathlib import Path
from typing import Tuple, Dict, Any
import json

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from ai.moldguard_ai.config import FEATURES
from ai.training.data_validation import validate_canonical_frame


LABEL_TO_ID = {"G": 0, "Y": 1, "R": 2}
ID_TO_LABEL = {0: "G", 1: "Y", 2: "R"}


def train_risk(
    df: pd.DataFrame,
    model_dir: Path,
    target: str = "label_viability",
    model_params: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    validate_canonical_frame(df, [target])

    X = df[FEATURES].copy()
    y_text = df[target].astype(str)
    unknown = sorted(set(y_text) - set(LABEL_TO_ID))
    if unknown:
        raise ValueError(f"Unknown risk labels: {unknown}")
    y = y_text.map(LABEL_TO_ID).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.22,
        random_state=42,
        stratify=y,
    )

    params = {
        "n_estimators": 280,
        "max_depth": 4,
        "learning_rate": 0.045,
        "min_child_weight": 2,
        "subsample": 0.90,
        "colsample_bytree": 0.90,
        "reg_lambda": 1.2,
    }
    if model_params:
        params.update(model_params)

    model = XGBClassifier(
        **params,
        objective="multi:softprob",
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=2,
    )
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    y_test_text = [ID_TO_LABEL[int(v)] for v in y_test]
    pred_text = [ID_TO_LABEL[int(v)] for v in pred]

    report = classification_report(
        y_test_text,
        pred_text,
        labels=["G", "Y", "R"],
        output_dict=True,
        zero_division=0,
    )
    cm = confusion_matrix(
        y_test_text,
        pred_text,
        labels=["G", "Y", "R"],
    ).tolist()

    # Novelty / OOD detector for safer recommendations.
    ood = IsolationForest(
        n_estimators=250,
        contamination=0.04,
        random_state=42,
        n_jobs=2,
    )
    ood.fit(X_train)

    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_dir / "risk_model.joblib")
    joblib.dump(ood, model_dir / "ood_model.joblib")

    return {
        "macro_f1": float(report["macro avg"]["f1-score"]),
        "weighted_f1": float(report["weighted avg"]["f1-score"]),
        "classification_report": report,
        "confusion_matrix_labels": ["G", "Y", "R"],
        "confusion_matrix": cm,
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "model_params": params,
    }
