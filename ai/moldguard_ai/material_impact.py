from __future__ import annotations

from typing import Dict, Any

from .config import MATERIAL_RISK_WEIGHTS


def risk_weighted_material_proxy(
    probabilities: Dict[str, float],
    cycles: int,
    part_weight_g: float | None,
) -> Dict[str, Any]:
    if part_weight_g is None or part_weight_g <= 0:
        return {
            "available": False,
            "method": "not_calculated",
            "note": "Provide part_weight_g or train a real waste-mass model to estimate material impact.",
        }

    equivalent_risk = sum(
        probabilities.get(label, 0.0) * weight
        for label, weight in MATERIAL_RISK_WEIGHTS.items()
    )
    total_planned_kg = part_weight_g * cycles / 1000.0
    material_at_risk_kg = total_planned_kg * equivalent_risk

    return {
        "available": True,
        "method": "risk_weighted_material_at_risk_proxy",
        "planned_material_kg": round(float(total_planned_kg), 4),
        "risk_equivalent": round(float(equivalent_risk), 5),
        "material_at_risk_kg": round(float(material_at_risk_kg), 4),
        "note": (
            "Prototype proxy: R is weighted as full risk and Y as partial risk. "
            "Replace with a measured reject/flash-waste model for final real-world claims."
        ),
    }


def compare_material_proxy(
    before_probabilities: Dict[str, float],
    after_probabilities: Dict[str, float],
    cycles: int,
    part_weight_g: float | None,
) -> Dict[str, Any]:
    before = risk_weighted_material_proxy(before_probabilities, cycles, part_weight_g)
    after = risk_weighted_material_proxy(after_probabilities, cycles, part_weight_g)

    if not before.get("available") or not after.get("available"):
        return {
            "available": False,
            "before": before,
            "after": after,
        }

    saved = before["material_at_risk_kg"] - after["material_at_risk_kg"]
    pct = saved / max(before["material_at_risk_kg"], 1e-9) * 100.0
    return {
        "available": True,
        "before": before,
        "after": after,
        "material_at_risk_reduction_kg": round(float(saved), 4),
        "material_at_risk_reduction_percent": round(float(pct), 3),
    }
