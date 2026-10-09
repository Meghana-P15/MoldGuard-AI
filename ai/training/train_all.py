from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBClassifier, XGBRegressor

from ai.moldguard_ai.config import FEATURES

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "demo_injection_molding.csv"
MODELS = ROOT / "models"


def train():
    if not DATA.exists():
        raise FileNotFoundError(f"{DATA} not found. Run python -m ai.training.generate_demo_data")

    df = pd.read_csv(DATA)
    X = df[FEATURES].copy()

    # Risk model
    label_to_id = {"G": 0, "Y": 1, "R": 2}
    id_to_label = {0: "G", 1: "Y", 2: "R"}
    y_text = df["label_viability"].astype(str)
    y = y_text.map(label_to_id).astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.22, random_state=42, stratify=y
    )
    risk = XGBClassifier(
        n_estimators=220,
        max_depth=4,
        learning_rate=0.055,
        subsample=0.90,
        colsample_bytree=0.90,
        objective="multi:softprob",
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=2,
    )
    risk.fit(X_train, y_train)
    y_pred = risk.predict(X_test)
    y_test_text = [id_to_label[int(v)] for v in y_test]
    y_pred_text = [id_to_label[int(v)] for v in y_pred]

    report = classification_report(
        y_test_text, y_pred_text, labels=["G", "Y", "R"], output_dict=True, zero_division=0
    )
    cm = confusion_matrix(y_test_text, y_pred_text, labels=["G", "Y", "R"]).tolist()

    # Energy model
    y_e = df["energy"].astype(float)
    Xe_train, Xe_test, ye_train, ye_test = train_test_split(
        X, y_e, test_size=0.22, random_state=42
    )
    energy = XGBRegressor(
        n_estimators=220,
        max_depth=4,
        learning_rate=0.055,
        subsample=0.90,
        colsample_bytree=0.90,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=2,
    )
    energy.fit(Xe_train, ye_train)
    e_pred = energy.predict(Xe_test)

    metrics = {
        "WARNING": "These metrics are from SYNTHETIC demo data and are not valid real-world claims.",
        "risk": {
            "classification_report": report,
            "confusion_matrix_labels": ["G", "Y", "R"],
            "confusion_matrix": cm,
        },
        "energy": {
            "mae": float(mean_absolute_error(ye_test, e_pred)),
            "rmse": float(mean_squared_error(ye_test, e_pred) ** 0.5),
            "r2": float(r2_score(ye_test, e_pred)),
        },
    }

    MODELS.mkdir(parents=True, exist_ok=True)
    joblib.dump(risk, MODELS / "risk_model.joblib")
    joblib.dump(energy, MODELS / "energy_model.joblib")
    (MODELS / "metadata.json").write_text(
        json.dumps(
            {
                "model_mode": "demo",
                "features": FEATURES,
                "labels": ["G", "Y", "R"],
                "source": "synthetic smoke-test data",
            },
            indent=2,
        )
    )
    (MODELS / "demo_metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"Saved model artifacts to {MODELS}")


if __name__ == "__main__":
    train()
