"""SageMaker training entrypoint for MoldGuard canonical data.

Expected channel:
  /opt/ml/input/data/train/*.csv

Required canonical columns:
  Tinj,tinj,Pinj,Ph,Bp,th,label_viability,energy

Optional environment variable:
  MOLDGUARD_OPTUNA_TRIALS=20
"""
from __future__ import annotations

from pathlib import Path
import json
import os

import pandas as pd

from ai.training.train_risk import train_risk
from ai.training.train_energy import train_energy
from ai.training.optuna_tuning import tune_risk_params


def main():
    train_dir = Path(os.environ.get("SM_CHANNEL_TRAIN", "/opt/ml/input/data/train"))
    model_dir = Path(os.environ.get("SM_MODEL_DIR", "/opt/ml/model"))
    trials = int(os.environ.get("MOLDGUARD_OPTUNA_TRIALS", "0"))

    csvs = sorted(train_dir.glob("*.csv"))
    if not csvs:
        raise FileNotFoundError(f"No CSV files found in {train_dir}")

    df = pd.concat([pd.read_csv(p) for p in csvs], ignore_index=True)

    tuning = None
    risk_params = None
    if trials > 0:
        tuning = tune_risk_params(df, trials=trials)
        risk_params = tuning["best_params"]

    risk_metrics = train_risk(df, model_dir, model_params=risk_params)
    energy_metrics = train_energy(df, model_dir)

    metadata = {
        "model_mode": "real",
        "features": ["Tinj", "tinj", "Pinj", "Ph", "Bp", "th"],
        "labels": ["G", "Y", "R"],
        "energy_validation_mae": energy_metrics["mae"],
        "risk_macro_f1": risk_metrics["macro_f1"],
        "artifact_version": "4.0",
        "training_environment": "Amazon SageMaker",
        "optuna_tuning": tuning,
    }
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
    (model_dir / "training_metrics.json").write_text(
        json.dumps(
            {
                "risk": risk_metrics,
                "energy": energy_metrics,
                "tuning": tuning,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
