from __future__ import annotations

from typing import Dict, Any
import numpy as np

from .config import FEATURES, PARAM_BOUNDS, LOCAL_STEP_FRACTION
from .runtime import ModelBundle


def _normalize_energy(value: float, reference: float) -> float:
    return value / max(reference, 1e-9)


def _normalized_change(candidate: Dict[str, float], current: Dict[str, float]) -> float:
    changes = []
    for f in FEATURES:
        lo, hi = PARAM_BOUNDS[f]
        span = max(hi - lo, 1e-9)
        changes.append(abs(candidate[f] - current[f]) / span)
    return float(np.mean(changes))


def _score(
    good_probability: float,
    energy: float,
    reference_energy: float,
    change: float,
    quality_weight: float = 0.70,
    energy_weight: float = 0.20,
    change_weight: float = 0.10,
) -> float:
    # Higher is better.
    return (
        quality_weight * good_probability
        - energy_weight * _normalize_energy(energy, reference_energy)
        - change_weight * change
    )


def optimize_settings(
    bundle: ModelBundle,
    current: Dict[str, float],
    n_candidates: int = 1200,
    seed: int = 42,
) -> Dict[str, Any]:
    rng = np.random.default_rng(seed)

    current_risk = bundle.predict_risk(current)
    current_energy = bundle.predict_energy(current)
    current_good = current_risk["probabilities"]["G"]

    best = {
        "params": {f: float(current[f]) for f in FEATURES},
        "good_probability": current_good,
        "energy": current_energy,
        "score": _score(current_good, current_energy, current_energy, 0.0),
    }

    for _ in range(n_candidates):
        candidate = {}
        for f in FEATURES:
            value = float(current[f])
            lo, hi = PARAM_BOUNDS[f]
            radius = (hi - lo) * LOCAL_STEP_FRACTION[f]
            sampled = rng.uniform(max(lo, value - radius), min(hi, value + radius))
            candidate[f] = float(sampled)

        probabilities = bundle.predict_probabilities(candidate)
        energy = bundle.predict_energy(candidate)
        p_good = probabilities["G"]
        change = _normalized_change(candidate, current)
        score = _score(p_good, energy, current_energy, change)

        if score > best["score"]:
            best = {
                "params": candidate,
                "good_probability": p_good,
                "energy": energy,
                "score": score,
            }

    recommended = {k: round(v, 3) for k, v in best["params"].items()}
    energy_reduction_pct = (
        (current_energy - best["energy"]) / max(current_energy, 1e-9) * 100.0
    )
    good_delta = best["good_probability"] - current_good

    return {
        "current": {
            "parameters": {f: float(current[f]) for f in FEATURES},
            "good_probability": round(float(current_good), 5),
            "energy": round(float(current_energy), 5),
        },
        "recommended_parameters": recommended,
        "optimized": {
            "good_probability": round(float(best["good_probability"]), 5),
            "energy": round(float(best["energy"]), 5),
        },
        "improvement": {
            "good_probability_change": round(float(good_delta), 5),
            "energy_reduction_percent": round(float(energy_reduction_pct), 3),
        },
        "optimizer_note": (
            "Prototype constrained search. Recommendations remain inside configured "
            "bounds and require process-engineer validation before real equipment use."
        ),
    }
