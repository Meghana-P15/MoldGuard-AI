"""SageMaker-compatible training entrypoint.

Expected training channel layout:
  /opt/ml/input/data/training/modelo.xlsx
  /opt/ml/input/data/training/test_dataset.csv

Artifacts are written to /opt/ml/model by default.
"""
from __future__ import annotations

import os
from pathlib import Path

training = Path(os.getenv("SM_CHANNEL_TRAINING", "/opt/ml/input/data/training"))
os.environ.setdefault("MOLDING_DATA_PATH", str(training / "modelo.xlsx"))
os.environ.setdefault("ENERGY_DATA_PATH", str(training / "test_dataset.csv"))
os.environ.setdefault("MODEL_DIR", os.getenv("SM_MODEL_DIR", "/opt/ml/model"))

from ai.training.train_all import train

if __name__ == "__main__":
    train()
