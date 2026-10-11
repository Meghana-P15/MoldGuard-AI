"""Optional Optuna hyperparameter tuning using only the two real datasets.

Usage:
    python -m ai.training.tune_optuna --task risk --trials 30
    python -m ai.training.tune_optuna --task energy --trials 30
"""
from __future__ import annotations

import argparse
import json

import optuna
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

from ai.training.common import (
    build_energy_frame,
    build_risk_frame,
    load_energy_data,
    load_molding_data,
)


def tune_risk(trials: int):
    X, y, _ = build_risk_frame(load_molding_data())
    Xtr, Xva, ytr, yva = train_test_split(X, y, test_size=.22, random_state=42)

    def objective(trial):
        model = XGBRegressor(
            n_estimators=trial.suggest_int("n_estimators", 180, 650),
            max_depth=trial.suggest_int("max_depth", 3, 8),
            learning_rate=trial.suggest_float("learning_rate", .01, .10, log=True),
            subsample=trial.suggest_float("subsample", .75, 1.0),
            colsample_bytree=trial.suggest_float("colsample_bytree", .75, 1.0),
            objective="reg:squarederror", random_state=42, n_jobs=2,
        )
        model.fit(Xtr, ytr)
        return mean_absolute_error(yva, model.predict(Xva))

    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=trials)
    return study.best_trial.params


def tune_energy(trials: int):
    X, y, _ = build_energy_frame(load_energy_data())
    Xtr, Xva, ytr, yva = train_test_split(X, y, test_size=.20, random_state=42)

    def objective(trial):
        model = XGBRegressor(
            n_estimators=trial.suggest_int("n_estimators", 180, 650),
            max_depth=trial.suggest_int("max_depth", 3, 8),
            learning_rate=trial.suggest_float("learning_rate", .01, .10, log=True),
            subsample=trial.suggest_float("subsample", .75, 1.0),
            colsample_bytree=trial.suggest_float("colsample_bytree", .75, 1.0),
            objective="reg:squarederror", random_state=42, n_jobs=2,
        )
        model.fit(Xtr, ytr)
        return mean_absolute_error(yva, model.predict(Xva))

    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=trials)
    return study.best_trial.params


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=["risk", "energy"], required=True)
    parser.add_argument("--trials", type=int, default=30)
    args = parser.parse_args()
    result = tune_risk(args.trials) if args.task == "risk" else tune_energy(args.trials)
    print(json.dumps(result, indent=2))
