"""
Template for adapting a real downloaded dataset.

Do not guess column names. Inspect the downloaded file first, then explicitly
map real columns into the six canonical features used by the app.
"""
from pathlib import Path
import pandas as pd

CANONICAL = ["Tinj", "tinj", "Pinj", "Ph", "Bp", "th"]

# Example ONLY — replace keys/values after inspecting the actual dataset.
COLUMN_MAP = {
    # "real_temperature_column": "Tinj",
    # "real_injection_time_column": "tinj",
    # "real_injection_pressure_column": "Pinj",
    # "real_holding_pressure_column": "Ph",
    # "real_back_pressure_column": "Bp",
    # "real_holding_time_column": "th",
}


def load_and_map(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if not COLUMN_MAP:
        raise RuntimeError("Fill COLUMN_MAP after inspecting the real dataset columns.")
    mapped = df.rename(columns=COLUMN_MAP)
    missing = [c for c in CANONICAL if c not in mapped.columns]
    if missing:
        raise ValueError(f"Missing canonical features after mapping: {missing}")
    return mapped
