from pathlib import Path
import json

import pandas as pd

from ai.moldguard_ai.config import FEATURES
from ai.training.train_risk import train_risk
from ai.training.train_energy import train_energy

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "demo_injection_molding.csv"
MODELS = ROOT / "models"


def train():
    if not DATA.exists():
        raise FileNotFoundError(
            f"{DATA} not found. Run python -m ai.training.generate_demo_data"
        )

    df = pd.read_csv(DATA)

    risk_metrics = train_risk(df, MODELS)
    energy_metrics = train_energy(df, MODELS)

    metadata = {
        "model_mode": "demo",
        "features": FEATURES,
        "labels": ["G", "Y", "R"],
        "source": "synthetic smoke-test data",
        "energy_validation_mae": energy_metrics["mae"],
        "risk_macro_f1": risk_metrics["macro_f1"],
        "artifact_version": "2.0",
    }

    metrics = {
        "WARNING": (
            "These metrics are from SYNTHETIC demo data and are not valid "
            "real-world performance claims."
        ),
        "risk": risk_metrics,
        "energy": energy_metrics,
    }

    MODELS.mkdir(parents=True, exist_ok=True)
    (MODELS / "metadata.json").write_text(json.dumps(metadata, indent=2))
    (MODELS / "demo_metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"Saved enhanced model artifacts to {MODELS}")


if __name__ == "__main__":
    train()
