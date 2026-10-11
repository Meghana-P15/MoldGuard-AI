from __future__ import annotations

import json
from pathlib import Path

from ai.moldguard_ai.config import (
    FEATURES,
    FEATURE_LABELS,
    FEATURE_SOURCE_COLUMNS,
    FEATURE_UNITS,
    PARAM_BOUNDS,
    GOOD_MAX_DEFECT_RATE,
    WARNING_MAX_DEFECT_RATE,
)
from ai.training.common import energy_data_path, model_dir, molding_data_path
from ai.training.train_energy import train_energy
from ai.training.train_risk import train_risk

ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = ROOT / "knowledge" / "docs"


def _write_real_data_operating_envelope(metadata: dict):
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    stats = metadata["feature_stats"]
    lines = [
        "# Real-data operating envelope",
        "",
        "Generated from measured injection-molding records in `modelo.xlsx`.",
        "This is a data-familiarity reference, not an OEM or factory SOP.",
        "",
        "## Observed process ranges",
        "",
    ]
    for f in FEATURES:
        s = stats[f]
        lines.append(
            f"- **{FEATURE_LABELS[f]} ({f})**: observed {s['min']:.3f} to {s['max']:.3f} {FEATURE_UNITS[f]}; "
            f"central 98% approximately {s['p01']:.3f} to {s['p99']:.3f} {FEATURE_UNITS[f]}."
        )
    lines += [
        "",
        "## Defect-rate decision thresholds",
        "",
        f"- GOOD: predicted defect rate ≤ {GOOD_MAX_DEFECT_RATE*100:.1f}%",
        f"- WARNING: > {GOOD_MAX_DEFECT_RATE*100:.1f}% and ≤ {WARNING_MAX_DEFECT_RATE*100:.1f}%",
        f"- HIGH RISK: > {WARNING_MAX_DEFECT_RATE*100:.1f}%",
        "",
        "## Human-review rule",
        "",
        "Settings flagged out-of-distribution by the Isolation Forest require process-engineer review.",
        "Recommendations are decision support only and are never sent directly to machine controls.",
    ]
    (KNOWLEDGE_DIR / "real_data_operating_envelope.md").write_text("\n".join(lines))


def train():
    out = model_dir()
    out.mkdir(parents=True, exist_ok=True)

    risk = train_risk(out)
    energy = train_energy(out)
    metadata = {
        "model_mode": "real_data_only",
        "architecture": "defect_xgboost_regression+thresholds+ood_isolation_forest+energy_xgboost+optimizer+semantic_rag",
        "features": FEATURES,
        "feature_labels": FEATURE_LABELS,
        "feature_units": FEATURE_UNITS,
        "feature_source_columns": FEATURE_SOURCE_COLUMNS,
        "parameter_bounds": PARAM_BOUNDS,
        "raw_datasets": [molding_data_path().name, energy_data_path().name],
        "synthetic_data_used": False,
        "pairing_note": (
            "The molding and electrical datasets are independent real-world sources and are not row-wise joined. "
            "Defect-rate/OOD models use modelo.xlsx. The energy regressor uses test_dataset.csv directly."
        ),
        **risk["metadata"],
        **energy["metadata"],
    }
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2))
    (out / "training_summary.json").write_text(
        json.dumps({"risk": risk["metrics"], "energy": energy["metrics"]}, indent=2)
    )
    _write_real_data_operating_envelope(metadata)

    print(f"Defect/OOD training source: {molding_data_path()}")
    print(f"Energy training source:     {energy_data_path()}")
    print(f"Saved model artifacts to:   {out}")
    print("Synthetic data used: False")


if __name__ == "__main__":
    train()
