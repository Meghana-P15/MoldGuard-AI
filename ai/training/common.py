from __future__ import annotations

import os
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

from ai.moldguard_ai.config import FEATURES, FEATURE_SOURCE_COLUMNS, ENERGY_FEATURES

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MOLDING_DATA = ROOT / "data" / "modelo.xlsx"
DEFAULT_ENERGY_DATA = ROOT / "data" / "test_dataset.csv"
DEFAULT_MODEL_DIR = ROOT / "models"


def molding_data_path() -> Path:
    return Path(os.getenv("MOLDING_DATA_PATH", str(DEFAULT_MOLDING_DATA)))


def energy_data_path() -> Path:
    return Path(os.getenv("ENERGY_DATA_PATH", str(DEFAULT_ENERGY_DATA)))


def model_dir() -> Path:
    return Path(os.getenv("MODEL_DIR", str(DEFAULT_MODEL_DIR)))


def load_molding_data() -> pd.DataFrame:
    path = molding_data_path()
    if not path.exists():
        raise FileNotFoundError(f"Missing real molding dataset: {path}")
    df = pd.read_excel(path)
    required = set(FEATURE_SOURCE_COLUMNS.values()) | {
        "%Defectuosos",
        "Maquina",
        "Nombre_producto",
        "Peso_producto_gramos",
        "Cavidades_molde",
    }
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"modelo.xlsx is missing required columns: {missing}")
    return df


def build_risk_frame(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """Build real process features and measured defect-rate target.

    %Defectuosos is stored as a fraction (for example 0.054 = 5.4%).
    No synthetic labels or generated target values are created.
    """
    mask = (
        (pd.to_numeric(df["Presion_inyeccion_bares"], errors="coerce") > 0)
        & (pd.to_numeric(df["Presion_retencion_bares"], errors="coerce") > 0)
        & (pd.to_numeric(df["Tiempo_ciclo"], errors="coerce") > 0)
    )
    subset = df.loc[mask].copy()

    X = pd.DataFrame(index=subset.index)
    for feature, source in FEATURE_SOURCE_COLUMNS.items():
        X[feature] = pd.to_numeric(subset[source], errors="coerce")

    defect = pd.to_numeric(subset["%Defectuosos"], errors="coerce")
    valid = X.notna().all(axis=1) & defect.notna() & np.isfinite(defect) & (defect >= 0)
    X = X.loc[valid].reset_index(drop=True)
    defect = defect.loc[valid].reset_index(drop=True)
    subset = subset.loc[valid].reset_index(drop=True)
    return X, defect, subset


def load_energy_data() -> pd.DataFrame:
    path = energy_data_path()
    if not path.exists():
        raise FileNotFoundError(f"Missing real energy dataset: {path}")
    df = pd.read_csv(path)
    required = {
        "TOTAL_ACT_POWER",
        "TOTAL_CURRENT",
        "A_VOLTAGE",
        "B_VOLTAGE",
        "C_VOLTAGE",
        "A_PF",
        "B_PF",
        "C_PF",
        "A_FREQ",
        "B_FREQ",
        "C_FREQ",
        "MOLD_SPEED",
        "PRODUCTION_STATUS",
        "MACHINENAME",
        "PRODNAME",
        "MOLD_NAME",
    }
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"test_dataset.csv is missing required columns: {missing}")
    return df


def build_energy_frame(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    work = df.copy()
    work["AVG_VOLTAGE"] = work[["A_VOLTAGE", "B_VOLTAGE", "C_VOLTAGE"]].apply(
        pd.to_numeric, errors="coerce"
    ).mean(axis=1)
    work["AVG_PF"] = work[["A_PF", "B_PF", "C_PF"]].apply(
        pd.to_numeric, errors="coerce"
    ).mean(axis=1)
    work["AVG_FREQ"] = work[["A_FREQ", "B_FREQ", "C_FREQ"]].apply(
        pd.to_numeric, errors="coerce"
    ).mean(axis=1)

    X = work[ENERGY_FEATURES].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(work["TOTAL_ACT_POWER"], errors="coerce")
    valid = X.notna().all(axis=1) & y.notna() & np.isfinite(y) & (y > 0)
    return (
        X.loc[valid].reset_index(drop=True),
        y.loc[valid].reset_index(drop=True),
        work.loc[valid].reset_index(drop=True),
    )
