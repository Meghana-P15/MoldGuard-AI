from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, request

FEATURES = ["Tinj", "tinj", "Pinj", "Ph", "Bp", "th"]
MODEL_DIR = Path("/opt/ml/model")

app = Flask(__name__)

risk_model = joblib.load(MODEL_DIR / "risk_model.joblib")
energy_model = joblib.load(MODEL_DIR / "energy_model.joblib")
ood_model = (
    joblib.load(MODEL_DIR / "ood_model.joblib")
    if (MODEL_DIR / "ood_model.joblib").exists()
    else None
)
metadata = json.loads((MODEL_DIR / "metadata.json").read_text())
labels = metadata.get("labels", ["G", "Y", "R"])


@app.get("/ping")
def ping():
    return jsonify({"status": "ok"})


@app.post("/invocations")
def invocations():
    payload = request.get_json(force=True)
    if "instances" in payload:
        rows = payload["instances"]
    else:
        rows = [payload]

    frame = pd.DataFrame(
        [[float(row[f]) for f in FEATURES] for row in rows],
        columns=FEATURES,
    )

    probs = risk_model.predict_proba(frame)
    energy = energy_model.predict(frame)
    ood = ood_model.predict(frame) if ood_model is not None else [0] * len(frame)

    outputs = []
    for i in range(len(frame)):
        probability_map = {label: float(probs[i][j]) for j, label in enumerate(labels)}
        predicted = max(probability_map, key=probability_map.get)
        outputs.append(
            {
                "prediction": predicted,
                "probabilities": probability_map,
                "predicted_energy": float(energy[i]),
                "distribution": (
                    "IN_DISTRIBUTION"
                    if ood_model is not None and int(ood[i]) == 1
                    else "OUT_OF_DISTRIBUTION"
                    if ood_model is not None
                    else "UNKNOWN"
                ),
            }
        )

    return jsonify({"predictions": outputs})
