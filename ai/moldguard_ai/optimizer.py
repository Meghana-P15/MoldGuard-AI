from __future__ import annotations

from typing import Any, Dict

import numpy as np

from .config import FEATURES, LOCAL_STEP_FRACTION, PARAM_BOUNDS
from .runtime import ModelBundle


def _normalized_change(candidate: Dict[str, float], current: Dict[str, float]) -> float:
    values = []
    for feature in FEATURES:
        lo, hi = PARAM_BOUNDS[feature]
        values.append(abs(candidate[feature] - current[feature]) / max(hi - lo, 1e-9))
    return float(np.mean(values))


def _score(defect_rate: float, energy: float, reference_energy: float, change: float) -> float:
    # Lower is better. Quality has the largest weight, then energy, then setting stability.
    energy_ratio = energy / max(reference_energy, 1e-12)
    quality_penalty = min(max(defect_rate / 0.06, 0.0), 2.0)
    return 0.68 * quality_penalty + 0.22 * energy_ratio + 0.10 * change


def optimize_settings(
    bundle: ModelBundle,
    current: Dict[str, float],
    material: str | None = None,
    n_candidates: int = 1800,
    seed: int = 42,
) -> Dict[str, Any]:
    rng = np.random.default_rng(seed)
    current_defect = bundle.predict_defect_rate(current)
    current_energy = bundle.predict_energy(current, material)["kwh_per_cycle"]

    candidates = []
    for _ in range(n_candidates):
        row = {}
        for feature in FEATURES:
            lo, hi = PARAM_BOUNDS[feature]
            value = float(current[feature])
            radius = (hi - lo) * LOCAL_STEP_FRACTION[feature]
            row[feature] = float(
                rng.uniform(max(lo, value - radius), min(hi, value + radius))
            )
        candidates.append(row)

    defects = bundle.predict_defect_rate_batch(candidates)
    ood_flags = bundle.predict_ood_batch(candidates)

    best = {
        "params": {f: float(current[f]) for f in FEATURES},
        "defect_rate": current_defect,
        "energy": current_energy,
        "score": _score(current_defect, current_energy, current_energy, 0.0),
    }
    filtered = 0
    base_power = bundle.predict_power_watts(material)

    for i, candidate in enumerate(candidates):
        if int(ood_flags[i]) != 1:
            filtered += 1
            continue
        defect_rate = float(defects[i])
        energy = base_power * float(candidate["tinj"]) / 3_600_000.0
        change = _normalized_change(candidate, current)

        # Reject candidates that materially worsen predicted defect rate just to save energy.
        if defect_rate > current_defect + 0.002:
            continue
        score = _score(defect_rate, energy, current_energy, change)
        if score < best["score"]:
            best = {
                "params": candidate,
                "defect_rate": defect_rate,
                "energy": energy,
                "score": score,
            }

    energy_reduction_pct = (
        (current_energy - best["energy"]) / max(current_energy, 1e-12) * 100.0
    )
    return {
        "current": {
            "parameters": {f: float(current[f]) for f in FEATURES},
            "predicted_defect_rate": round(float(current_defect), 6),
            "predicted_defect_percent": round(float(current_defect * 100.0), 4),
            "energy_kwh_per_cycle": round(float(current_energy), 8),
        },
        "recommended_parameters": {k: round(float(v), 3) for k, v in best["params"].items()},
        "optimized": {
            "predicted_defect_rate": round(float(best["defect_rate"]), 6),
            "predicted_defect_percent": round(float(best["defect_rate"] * 100.0), 4),
            "energy_kwh_per_cycle": round(float(best["energy"]), 8),
        },
        "improvement": {
            "defect_rate_change_percentage_points": round(
                float((best["defect_rate"] - current_defect) * 100.0), 4
            ),
            "energy_reduction_percent": round(float(energy_reduction_pct), 3),
        },
        "candidate_search": {
            "generated": n_candidates,
            "ood_filtered": filtered,
            "selected_is_in_distribution": True,
        },
        "optimizer_note": (
            "Constrained multi-objective search over 1,800 local candidates. "
            "The objective minimizes predicted real defect rate, estimated energy use, and setting changes. "
            "Out-of-distribution candidates are rejected and every recommendation requires engineer review."
        ),
    }
