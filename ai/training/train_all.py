from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBClassifier, XGBRegressor

from ai.moldguard_ai.config import FEATURES, PARAM_BOUNDS

ROOT = Path(__file__).resolve().parents[1]
MOLDING_DATA = ROOT / "data" / "modelo.xlsx"
ENERGY_DATA = ROOT / "data" / "test_dataset.csv"
MODELS = ROOT / "models"


def _robust_scale(series: pd.Series, out_lo: float, out_hi: float) -> pd.Series:
    """Map a real measured column into the app's canonical operating range.

    The transformation is fit in-memory only. No third/processed dataset is written.
    """
    s = pd.to_numeric(series, errors="coerce").astype(float)
    lo = float(s.quantile(0.01))
    hi = float(s.quantile(0.99))
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        return pd.Series(np.full(len(s), (out_lo + out_hi) / 2.0), index=s.index)
    s = s.clip(lo, hi)
    return out_lo + (s - lo) * (out_hi - out_lo) / (hi - lo)


def _load_real_training_frames() -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    if not MOLDING_DATA.exists():
        raise FileNotFoundError(f"Missing real molding dataset: {MOLDING_DATA}")
    if not ENERGY_DATA.exists():
        raise FileNotFoundError(f"Missing real energy dataset: {ENERGY_DATA}")

    mold = pd.read_excel(MOLDING_DATA)
    power = pd.read_csv(ENERGY_DATA)

    # Use only true injection-molding rows from the mixed molding/blow-molding file.
    mold = mold[
        (pd.to_numeric(mold["Presion_inyeccion_bares"], errors="coerce") > 0)
        & (pd.to_numeric(mold["Presion_retencion_bares"], errors="coerce") > 0)
        & (pd.to_numeric(mold["Tiempo_ciclo"], errors="coerce") > 0)
    ].copy()

    # Six real process measurements are transformed to the existing MoldGuard API ranges.
    source_map = {
        "Tinj": "Temp_mat_fundido",
        "tinj": "Tiempo_ciclo",
        "Pinj": "Presion_inyeccion_bares",
        "Ph": "Presion_retencion_bares",
        "Bp": "Temp_molde_centigrados ",
        "th": "Tiempo_retencion_inyeccion_seg",
    }

    X = pd.DataFrame(index=mold.index)
    for feature, source_col in source_map.items():
        lo, hi = PARAM_BOUNDS[feature]
        X[feature] = _robust_scale(mold[source_col], lo, hi)

    # Quality labels come only from the measured real defect percentage.
    defect = pd.to_numeric(mold["%Defectuosos"], errors="coerce")
    valid = defect.notna() & X.notna().all(axis=1)
    X = X.loc[valid].reset_index(drop=True)
    defect = defect.loc[valid].reset_index(drop=True)
    mold_valid = mold.loc[valid].reset_index(drop=True)

    q50 = float(defect.quantile(0.50))
    q80 = float(defect.quantile(0.80))
    y_risk = pd.Series(np.where(defect <= q50, "G", np.where(defect <= q80, "Y", "R")))

    # Energy source remains independent: measured TOTAL_ACT_POWER from test_dataset.csv.
    # Convert measured power (W) into kWh-per-cycle samples using the real cycle-time
    # distribution from modelo.xlsx. Because the datasets have no shared row key, we do
    # NOT claim row-wise pairing; the energy distribution is calibrated by quantile rank.
    measured_watts = pd.to_numeric(power["TOTAL_ACT_POWER"], errors="coerce")
    measured_watts = measured_watts[np.isfinite(measured_watts) & (measured_watts > 0)].reset_index(drop=True)
    if len(measured_watts) < 100:
        raise ValueError("Not enough valid TOTAL_ACT_POWER readings in test_dataset.csv")

    cycle_seconds = pd.to_numeric(mold_valid["Tiempo_ciclo"], errors="coerce").clip(lower=1.0)
    # Rank a real process-load proxy, then map it to the same quantiles of real measured power.
    process_load = (
        pd.to_numeric(mold_valid["Presion_inyeccion_bares"], errors="coerce").fillna(0)
        * cycle_seconds
        * pd.to_numeric(mold_valid["Cavidades_molde"], errors="coerce").fillna(1).clip(lower=1)
    )
    ranks = process_load.rank(method="average", pct=True).to_numpy()
    sorted_power = np.sort(measured_watts.to_numpy(dtype=float))
    idx = np.clip((ranks * (len(sorted_power) - 1)).astype(int), 0, len(sorted_power) - 1)
    matched_watts = sorted_power[idx]
    y_energy = pd.Series((matched_watts * cycle_seconds.to_numpy()) / 3_600_000.0)

    return X, y_risk, y_energy


def train():
    X, y_text, y_e = _load_real_training_frames()

    label_to_id = {"G": 0, "Y": 1, "R": 2}
    id_to_label = {0: "G", 1: "Y", 2: "R"}
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
        "NOTE": (
            "Risk model uses measured molding/defect data from modelo.xlsx. "
            "Energy values are calibrated from measured TOTAL_ACT_POWER in test_dataset.csv. "
            "The two source datasets have no common row key and are not claimed to be row-wise paired."
        ),
        "rows_used": int(len(X)),
        "risk": {
            "classification_report": report,
            "confusion_matrix_labels": ["G", "Y", "R"],
            "confusion_matrix": cm,
        },
        "energy": {
            "mae_kwh_per_cycle": float(mean_absolute_error(ye_test, e_pred)),
            "rmse_kwh_per_cycle": float(mean_squared_error(ye_test, e_pred) ** 0.5),
            "r2": float(r2_score(ye_test, e_pred)),
        },
    }

    MODELS.mkdir(parents=True, exist_ok=True)
    joblib.dump(risk, MODELS / "risk_model.joblib")
    joblib.dump(energy, MODELS / "energy_model.joblib")
    (MODELS / "metadata.json").write_text(
        json.dumps(
            {
                "model_mode": "real_dual_dataset",
                "features": FEATURES,
                "labels": ["G", "Y", "R"],
                "raw_datasets": ["modelo.xlsx", "test_dataset.csv"],
                "training_rows": int(len(X)),
                "source": "Two real-world datasets loaded directly at training time; no generated training CSV.",
                "energy_pairing_note": "Independent datasets; energy distribution calibrated by rank, not row-wise joined.",
            },
            indent=2,
        )
    )
    (MODELS / "demo_metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"Trained directly from {MOLDING_DATA.name} + {ENERGY_DATA.name}")
    print(f"Saved model artifacts to {MODELS}")


if __name__ == "__main__":
    train()
