from __future__ import annotations

from typing import Dict, Any

from .config import (
    HIGH_REJECT_PROBABILITY,
    MIN_CONFIDENCE_FOR_AUTOMATED_RECOMMENDATION,
    MIN_GOOD_PROBABILITY_FOR_LOW_RISK,
)


def decision_from_prediction(
    probabilities: Dict[str, float],
    distribution_status: str,
) -> Dict[str, Any]:
    confidence = max(probabilities.values()) if probabilities else 0.0
    p_good = probabilities.get("G", 0.0)
    p_reject = probabilities.get("R", 0.0)

    reasons: list[str] = []

    if distribution_status == "OUT_OF_DISTRIBUTION":
        reasons.append("Input is outside the learned operating distribution.")
        return {
            "decision": "REVIEW_REQUIRED",
            "confidence": round(float(confidence), 5),
            "reasons": reasons,
        }

    if p_reject >= HIGH_REJECT_PROBABILITY:
        reasons.append("Reject-class probability is high.")
        return {
            "decision": "HIGH_RISK",
            "confidence": round(float(confidence), 5),
            "reasons": reasons,
        }

    if confidence < MIN_CONFIDENCE_FOR_AUTOMATED_RECOMMENDATION:
        reasons.append("Model confidence is below the review threshold.")
        return {
            "decision": "REVIEW_REQUIRED",
            "confidence": round(float(confidence), 5),
            "reasons": reasons,
        }

    if p_good >= MIN_GOOD_PROBABILITY_FOR_LOW_RISK:
        reasons.append("Good-batch probability is above the low-risk threshold.")
        return {
            "decision": "LOW_RISK",
            "confidence": round(float(confidence), 5),
            "reasons": reasons,
        }

    reasons.append("Prediction is plausible but not strong enough for a low-risk decision.")
    return {
        "decision": "REVIEW_REQUIRED",
        "confidence": round(float(confidence), 5),
        "reasons": reasons,
    }
