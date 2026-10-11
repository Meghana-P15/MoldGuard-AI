from __future__ import annotations

from typing import Any, Dict

from ai.moldguard_ai.optimizer import optimize_settings
from ai.moldguard_ai.material_impact import compare_material_proxy
from agentic.runtime import get_bundle


def optimization_assessment(
    params: Dict[str, float],
    cycles: int,
    part_weight_g: float | None,
) -> Dict[str, Any]:
    bundle = get_bundle()
    result = optimize_settings(bundle, params)

    current_total = result["current"]["energy"] * cycles
    optimized_total = result["optimized"]["energy"] * cycles

    result["projected"] = {
        "cycles": cycles,
        "current_energy": round(current_total, 5),
        "optimized_energy": round(optimized_total, 5),
        "energy_saved": round(current_total - optimized_total, 5),
    }
    result["material_impact"] = compare_material_proxy(
        result["current"]["probabilities"],
        result["optimized"]["probabilities"],
        cycles,
        part_weight_g,
    )
    return result
