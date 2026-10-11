from __future__ import annotations

from typing import Any, Dict

import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_score
from xgboost import XGBClassifier

from ai.moldguard_ai.config import FEATURES
from ai.training.train_risk import LABEL_TO_ID


def tune_risk_params(
    df: pd.DataFrame,
    target: str = "label_viability",
    trials: int = 20,
) -> Dict[str, Any]:
    import optuna

    X = df[FEATURES]
    y = df[target].astype(str).map(LABEL_TO_ID).astype(int)
    cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=42)

    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 150, 500),
            "max_depth": trial.suggest_int("max_depth", 3, 7),
            "learning_rate": trial.suggest_float("learning_rate", 0.02, 0.12, log=True),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 6),
            "subsample": trial.suggest_float("subsample", 0.75, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.75, 1.0),
            "reg_lambda": trial.suggest_float("reg_lambda", 0.5, 3.0),
        }
        model = XGBClassifier(
            **params,
            objective="multi:softprob",
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=2,
        )
        scores = cross_val_score(model, X, y, cv=cv, scoring="f1_macro", n_jobs=1)
        return float(scores.mean())

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=max(1, trials))
    return {
        "best_macro_f1_cv": float(study.best_value),
        "best_params": dict(study.best_params),
    }
