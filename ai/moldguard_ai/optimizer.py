from __future__ import annotations

from typing import Dict, Any
import numpy as np
import pandas as pd

from .config import FEATURES, PARAM_BOUNDS, LOCAL_STEP_FRACTION, CLASS_NAMES
from .runtime import ModelBundle


def _normalize_energy(values: np.ndarray, reference: float) -> np.ndarray:
    return values / max(reference, 1e-9)


def _candidate_matrix(
    current: Dict[str, float],
    n_candidates: int,
    rng: np.random.Generator,
) -> np.ndarray:
    cols = []
    for f in FEATURES:
        value = float(current[f])
        lo, hi = PARAM_BOUNDS[f]
        radius = (hi - lo) * LOCAL_STEP_FRACTION[f]
        cols.append(
            rng.uniform(
                max(lo, value - radius),
                min(hi, value + radius),
                size=n_candidates,
            )
        )
    return np.column_stack(cols)


def optimize_settings(
    bundle: ModelBundle,
    current: Dict[str, float],
    n_candidates: int = 1800,
    seed: int = 42,
    minimum_good_improvement: float = 0.03,
) -> Dict[str, Any]:
    # Vectorized constrained search: nearby bounds, OOD filtering, and
    # multi-objective scoring for quality, reject risk, energy and setting change.
    rng = np.random.default_rng(seed)

    current_probs = bundle.predict_probabilities(current)
    current_energy = bundle.predict_energy(current)["value"]
    current_dist = bundle.distribution_check(current)

    X_current = np.array([float(current[f]) for f in FEATURES], dtype=float)
    X_candidates = _candidate_matrix(current, n_candidates, rng)
    candidate_df = pd.DataFrame(X_candidates, columns=FEATURES)

    if bundle.ood_model is not None:
        ood_pred = bundle.ood_model.predict(candidate_df)
        inlier_mask = ood_pred == 1
        skipped_ood = int((~inlier_mask).sum())
    else:
        inlier_mask = np.ones(n_candidates, dtype=bool)
        skipped_ood = 0

    if not inlier_mask.any():
        inlier_mask[:] = True

    valid_df = candidate_df.loc[inlier_mask].reset_index(drop=True)
    valid_matrix = valid_df[FEATURES].to_numpy(dtype=float)

    probs = bundle.risk_model.predict_proba(valid_df)
    labels = bundle.metadata.get("labels", CLASS_NAMES)
    good_idx = labels.index("G")
    reject_idx = labels.index("R")

    good = probs[:, good_idx]
    reject = probs[:, reject_idx]
    energy = np.asarray(bundle.energy_model.predict(valid_df), dtype=float)

    spans = np.array(
        [PARAM_BOUNDS[f][1] - PARAM_BOUNDS[f][0] for f in FEATURES],
        dtype=float,
    )
    change = np.mean(np.abs(valid_matrix - X_current) / spans, axis=1)

    score = (
        0.58 * good
        - 0.15 * reject
        - 0.17 * _normalize_energy(energy, current_energy)
        - 0.10 * change
    )

    best_idx = int(np.argmax(score))
    best_good = float(good[best_idx])
    best_reject = float(reject[best_idx])
    best_energy = float(energy[best_idx])
    best_params_arr = valid_matrix[best_idx]

    current_good = float(current_probs["G"])
    current_reject = float(current_probs["R"])
    meaningful = (best_good - current_good) >= minimum_good_improvement

    if not meaningful:
        best_good = current_good
        best_reject = current_reject
        best_energy = current_energy
        best_params = {f: float(current[f]) for f in FEATURES}
        best_probs = current_probs
    else:
        best_params = {
            f: float(best_params_arr[i])
            for i, f in enumerate(FEATURES)
        }
        best_probs = {
            label: float(probs[best_idx, i])
            for i, label in enumerate(labels)
        }
        for label in CLASS_NAMES:
            best_probs.setdefault(label, 0.0)

    energy_reduction_pct = (
        (current_energy - best_energy) / max(current_energy, 1e-9) * 100.0
    )

    return {
        "current": {
            "parameters": {f: float(current[f]) for f in FEATURES},
            "probabilities": current_probs,
            "good_probability": round(current_good, 5),
            "reject_probability": round(current_reject, 5),
            "energy": round(float(current_energy), 5),
            "distribution": current_dist,
        },
        "recommended_parameters": {
            k: round(float(v), 3) for k, v in best_params.items()
        },
        "optimized": {
            "probabilities": best_probs,
            "good_probability": round(best_good, 5),
            "reject_probability": round(best_reject, 5),
            "energy": round(best_energy, 5),
        },
        "improvement": {
            "good_probability_change": round(best_good - current_good, 5),
            "reject_probability_change": round(best_reject - current_reject, 5),
            "energy_reduction_percent": round(float(energy_reduction_pct), 3),
        },
        "guardrail": {
            "recommendation_available": meaningful,
            "accepted_candidates": int(inlier_mask.sum()),
            "skipped_out_of_distribution_candidates": skipped_ood,
            "note": (
                "Candidate scoring is vectorized, constrained to configured process "
                "bounds, and filters out-of-distribution candidates when available."
            ),
        },
        "optimizer_note": (
            "Decision-support recommendation only. A qualified process engineer must "
            "validate settings before they are applied to real equipment."
        ),
    }
