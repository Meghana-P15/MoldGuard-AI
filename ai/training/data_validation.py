from __future__ import annotations

from typing import Iterable
import pandas as pd

from ai.moldguard_ai.config import FEATURES


def validate_canonical_frame(
    df: pd.DataFrame,
    required_targets: Iterable[str] = (),
) -> None:
    required = [*FEATURES, *required_targets]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    null_features = df[FEATURES].isna().sum()
    bad = null_features[null_features > 0]
    if not bad.empty:
        raise ValueError(
            "Feature columns contain missing values: "
            + ", ".join(f"{k}={int(v)}" for k, v in bad.items())
        )

    non_numeric = [
        c for c in FEATURES
        if not pd.api.types.is_numeric_dtype(df[c])
    ]
    if non_numeric:
        raise ValueError(f"Feature columns must be numeric: {non_numeric}")
