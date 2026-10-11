"""Optuna tuning CLI for the MoldGuard risk classifier."""
from __future__ import annotations

import argparse
import json
import pandas as pd

from ai.training.optuna_tuning import tune_risk_params


def main(csv_path: str, target: str = "label_viability", trials: int = 30):
    df = pd.read_csv(csv_path)
    result = tune_risk_params(df, target=target, trials=trials)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--target", default="label_viability")
    parser.add_argument("--trials", type=int, default=30)
    args = parser.parse_args()
    main(args.csv, args.target, args.trials)
