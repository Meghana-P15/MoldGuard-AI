from __future__ import annotations

from typing import Any, Dict

from ai.moldguard_ai.config import PARAM_BOUNDS


def deterministic_safety_gate(
    quality: Dict[str, Any],
    optimization: Dict[str, Any],
) -> Dict[str, Any]:
    reasons: list[str] = []
    blocked = False

    distribution = quality.get("distribution", {}).get("status")
    if distribution == "OUT_OF_DISTRIBUTION":
        reasons.append("Input is outside the learned operating distribution.")
        blocked = True

    confidence = float(quality.get("confidence", 0.0))
    if confidence < 0.58:
        reasons.append("Model confidence is below the review threshold.")

    recommended = optimization.get("recommended_parameters", {})
    for feature, value in recommended.items():
        if feature not in PARAM_BOUNDS:
            continue
        lo, hi = PARAM_BOUNDS[feature]
        if not lo <= float(value) <= hi:
            reasons.append(
                f"{feature} recommendation {value} is outside configured bounds."
            )
            blocked = True

    guardrail = optimization.get("guardrail", {})
    if not guardrail.get("recommendation_available", False):
        reasons.append("Optimizer did not find a meaningful improvement.")

    if blocked:
        final = "REVIEW_REQUIRED"
    elif quality.get("decision") == "HIGH_RISK":
        final = "REVIEW_REQUIRED"
        reasons.append("High model risk requires qualified operator review.")
    elif reasons:
        final = "REVIEW_REQUIRED"
    else:
        final = "RECOMMEND_WITH_REVIEW"

    return {
        "decision": final,
        "blocked": blocked,
        "human_review_required": True,
        "reasons": reasons or [
            "All deterministic checks passed; human approval is still required."
        ],
        "rule": (
            "The supervisor agent cannot override this deterministic safety gate."
        ),
    }
